import cv2, mediapipe as mp, threading, time
from .events import Event
from .suspicion import SCORE
from .config import CFG
from .frame_buffer import FRAME_BUFFER

mp_face = mp.solutions.face_mesh

class GazeThread(threading.Thread):
    def __init__(self, cam_index=0):
        super().__init__(daemon=True)
        
        # Don't open camera - read from shared frame buffer instead
        self.mesh = mp_face.FaceMesh(
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            refine_landmarks=True
        )
        print("[GazeThread] ✅ Initialized (using shared frame buffer)")

    def run(self):
        print("[GazeThread] ✅ Started gaze detection")
        
        while True:
            # Read from shared frame buffer
            with FRAME_BUFFER.lock:
                frame = None if FRAME_BUFFER.frame is None else FRAME_BUFFER.frame.copy()
            
            if frame is None:
                time.sleep(0.01)
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = self.mesh.process(rgb)

            if res.multi_face_landmarks:
                faces = res.multi_face_landmarks

                if len(faces) > 1:
                    SCORE.add(Event.now("multi_face", 0.9, count=len(faces)))

                for face in faces:
                    nose = face.landmark[1]
                    left_eye = face.landmark[33]
                    right_eye = face.landmark[263]

                    dx = (left_eye.x + right_eye.x)/2 - nose.x
                    dy = ((left_eye.y + right_eye.y)/2)/2 - nose.y

                    yaw = dx * 100
                    pitch = dy * 100

                    if abs(yaw) > CFG.gaze_yaw_thresh or abs(pitch) > CFG.gaze_pitch_thresh:
                        SCORE.add(Event.now("gaze", 0.8, yaw=yaw, pitch=pitch))
            
            time.sleep(0.05)  # Process at ~20 FPS