import cv2, mediapipe as mp, threading, time
from collections import deque
from .events import Event
from .suspicion import SCORE
from .config import CFG
from .frame_buffer import FRAME_BUFFER
from .evidence import EvidenceRecorder  # ✅ make sure this matches evidence.py

mp_face = mp.solutions.face_mesh

# Rolling smoothing window
SMOOTH = deque(maxlen=5)
EBUF = EvidenceRecorder(fps=15, seconds=8, enabled=CFG.ENABLE_EVIDENCE)

class GazeThread(threading.Thread):
    def __init__(self, cam_index=0):
        super().__init__(daemon=True)

        self.mesh = mp_face.FaceMesh(
            refine_landmarks=True,
            min_detection_confidence=0.60,
            min_tracking_confidence=0.60
        )

        self.last_event_time = 0
        self.cooldown = CFG.event_cooldown.get("gaze", 1.2)
        print("[Gaze] ✅ Gaze system initialized")

    def run(self):
        print("[Gaze] ▶️ Gaze thread running...")

        while True:
            # Read latest frame
            with FRAME_BUFFER.lock:
                frame = FRAME_BUFFER.frame.copy() if FRAME_BUFFER.frame is not None else None

            if frame is None:
                time.sleep(0.01)
                continue

            EBUF.push(frame)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.mesh.process(rgb)

            # CASE 1: No face -> possible cheating (looking away / hiding face)
            if not results.multi_face_landmarks:
                now = time.time()
                if now - self.last_event_time > self.cooldown:
                    SCORE.add(Event.now("gaze", 0.65, reason="face_missing"))
                    print("[Gaze] ⚠️ Face missing - suspicious")
                    EBUF.save_async("face_missing", 0.65)
                    self.last_event_time = now
                time.sleep(0.05)
                continue

            faces = results.multi_face_landmarks

            # CASE 2: More than 1 face detected
            if len(faces) > 1:
                now = time.time()
                if now - self.last_event_time > CFG.event_cooldown.get("multi_face", 2.5):
                    SCORE.add(Event.now("multi_face", 0.90, count=len(faces)))
                    print("[Gaze] 🚨 Multiple faces detected!")
                    EBUF.save_async("multi_face", 0.90)
                    self.last_event_time = now

            # CASE 3: Normal gaze check
            for face in faces:
                nose = face.landmark[1]
                left_eye = face.landmark[33]
                right_eye = face.landmark[263]

                dx = (left_eye.x + right_eye.x) / 2 - nose.x
                dy = ((left_eye.y + right_eye.y) / 2) - nose.y

                yaw = dx * 100
                pitch = dy * 100

                SMOOTH.append((yaw, pitch))
                avg_yaw = sum(v[0] for v in SMOOTH) / len(SMOOTH)
                avg_pitch = sum(v[1] for v in SMOOTH) / len(SMOOTH)

                cheated = (
                    abs(avg_yaw) > CFG.gaze_yaw_thresh or
                    abs(avg_pitch) > CFG.gaze_pitch_thresh
                )

                if cheated:
                    now = time.time()
                    if now - self.last_event_time > self.cooldown:
                        intensity = min(1.0, (abs(avg_yaw) + abs(avg_pitch)) / 60)
                        
                        SCORE.add(Event.now("gaze", intensity, yaw=avg_yaw, pitch=avg_pitch))
                        print(f"[Gaze] 👀 Suspicious gaze: yaw={avg_yaw:.1f}, pitch={avg_pitch:.1f}")

                        EBUF.save_async("gaze", intensity)
                        self.last_event_time = now

            time.sleep(0.05)  # 20 FPS processing
