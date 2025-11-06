import cv2, mediapipe as mp, threading
from .events import Event
from .suspicion import SCORE
from .config import CFG

mp_face = mp.solutions.face_mesh

class GazeThread(threading.Thread):
    def __init__(self, cam_index=0):
        super().__init__(daemon=True)

        # Force phone camera index + DirectShow
        self.cap = cv2.VideoCapture(CFG.cam_index, cv2.CAP_DSHOW)

        # Recommended camera settings for phone webcam
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.mesh = mp_face.FaceMesh(
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            refine_landmarks=True
        )

    def run(self):
        while True:
            ok, frame = self.cap.read()
            if not ok:
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
