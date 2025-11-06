import cv2, mediapipe as mp, numpy as np, threading, time
from collections import deque
from .events import Event
from .suspicion import SCORE
from .config import CFG
from .frame_buffer import FRAME_BUFFER
from .evidence import EvidenceRecorder

# Evidence buffer for recording short clips
EBUF = EvidenceRecorder(fps=15, seconds=10, enabled=CFG.ENABLE_EVIDENCE)


class IdentityThread(threading.Thread):
    def __init__(self, cam_index=0, enroll_path="enrolled.npy"):
        super().__init__(daemon=True)

        # Mediapipe Face Detection
        self.detector = mp.solutions.face_detection.FaceDetection(model_selection=0)

        # Create FaceMesh inside thread (thread-safe)
        self.mesh = mp.solutions.face_mesh.FaceMesh(
            refine_landmarks=True,
            min_detection_confidence=0.60,
            min_tracking_confidence=0.60
        )

        self.enroll_path = enroll_path
        self.sim_buffer = deque(maxlen=7)

        self.last_event_time = 0
        self.cooldown = CFG.event_cooldown.get("identity_mismatch", 2.5)

        try:
            self.reference = np.load(enroll_path)
            print("[Identity] ✅ Loaded enrolled identity")
        except:
            self.reference = None
            print("[Identity] ⚠ No enrolled identity — waiting to enroll first face")

    def _embed(self, face):
        face = cv2.resize(face, (160, 160))

        # Color histogram
        hist = np.concatenate([
            cv2.calcHist([c], [0], None, [32], [0, 256]).flatten()
            for c in cv2.split(face)
        ])

        # Laplacian texture
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        lbp = cv2.Laplacian(gray, cv2.CV_64F).flatten()

        v = np.concatenate([hist, lbp])
        return v / (np.linalg.norm(v) + 1e-6)

    def _liveness_check(self, frame, face_lm):
        left_eye = [33, 160, 158, 133, 153, 144]
        right_eye = [263, 387, 386, 362, 380, 373]

        def ratio(pts):
            d1 = np.linalg.norm(np.array(pts[1]) - np.array(pts[5]))
            d2 = np.linalg.norm(np.array(pts[2]) - np.array(pts[4]))
            d3 = np.linalg.norm(np.array(pts[0]) - np.array(pts[3]))
            return (d1 + d2) / (2.0 * d3)

        ih, iw, _ = frame.shape
        l_pts = [(int(face_lm.landmark[i].x * iw), int(face_lm.landmark[i].y * ih)) for i in left_eye]
        r_pts = [(int(face_lm.landmark[i].x * iw), int(face_lm.landmark[i].y * ih)) for i in right_eye]

        ear = (ratio(l_pts) + ratio(r_pts)) / 2
        return ear > 0.18  # below this → eyes not blinking enough → spoof

    def run(self):
        print("[Identity] ▶️ Identity thread active")

        while True:
            with FRAME_BUFFER.lock:
                frame = FRAME_BUFFER.frame.copy() if FRAME_BUFFER.frame is not None else None

            if frame is None:
                time.sleep(0.01)
                continue

            EBUF.push(frame)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            res = self.detector.process(rgb)
            if not res.detections:
                time.sleep(0.05)
                continue

            det = res.detections[0].location_data.relative_bounding_box
            h, w, _ = frame.shape
            x1, y1, x2, y2 = (
                int(det.xmin * w),
                int(det.ymin * h),
                int((det.xmin + det.width) * w),
                int((det.ymin + det.height) * h)
            )

            face = frame[y1:y2, x1:x2]
            if face.size == 0:
                continue

            mesh_res = self.mesh.process(rgb)
            if mesh_res.multi_face_landmarks:
                if not self._liveness_check(frame, mesh_res.multi_face_landmarks[0]):
                    SCORE.add(Event.now("liveness_fail", 0.85))
                    EBUF.save_async("spoof", 0.85)
                    print("[Identity] ❌ Spoof suspected (no blinking)")
                    time.sleep(0.3)
                    continue

            emb = self._embed(face)

            # ✅ Enrollment
            if self.reference is None:
                self.reference = emb
                np.save(self.enroll_path, emb)
                print("[Identity] ✅ User enrolled and saved")
                time.sleep(1)
                continue

            # ✅ Verification
            sim = float(np.dot(self.reference, emb))
            self.sim_buffer.append(sim)
            avg_sim = sum(self.sim_buffer) / len(self.sim_buffer)

            if avg_sim < 0.80:
                now = time.time()
                if now - self.last_event_time > self.cooldown:
                    SCORE.add(Event.now("identity_mismatch", 0.90, sim=avg_sim))
                    EBUF.save_async("identity_mismatch", 0.90)
                    print(f"[Identity] ❌ Identity mismatch: {avg_sim:.2f}")
                    self.last_event_time = now

            time.sleep(0.1)
