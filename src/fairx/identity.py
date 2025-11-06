import cv2, mediapipe as mp, numpy as np, threading
from .events import Event
from .suspicion import SCORE
from .config import CFG

mp_face = mp.solutions.face_detection

class IdentityThread(threading.Thread):
    def __init__(self, cam_index=0, enroll_path="enrolled.npy"):
        super().__init__(daemon=True)

        # Force phone camera + DirectShow backend (Windows stability)
        self.cap = cv2.VideoCapture(CFG.cam_index, cv2.CAP_DSHOW)

        # Improve phone webcam performance & clarity
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.detector = mp_face.FaceDetection(model_selection=0)
        self.enroll_path = enroll_path

        try:
            self.reference = np.load(enroll_path)
        except:
            self.reference = None

    def _embed(self, face):
        face = cv2.resize(face, (128, 128))
        hist = np.concatenate([
            cv2.calcHist([c], [0], None, [32], [0, 256]).flatten()
            for c in cv2.split(face)
        ])
        return hist / (np.linalg.norm(hist) + 1e-6)

    def run(self):
        while True:
            ok, frame = self.cap.read()
            if not ok:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = self.detector.process(rgb)
            if not res.detections:
                continue

            box = res.detections[0].location_data.relative_bounding_box
            h, w, _ = frame.shape
            x1, y1, x2, y2 = (
                int(box.xmin * w),
                int(box.ymin * h),
                int((box.xmin + box.width) * w),
                int((box.ymin + box.height) * h)
            )

            face = frame[y1:y2, x1:x2]
            if face.size == 0:
                continue

            emb = self._embed(face)

            # Enrollment mode: first person
            if self.reference is None:
                self.reference = emb
                np.save(self.enroll_path, emb)
                print("[IDENTITY] Enrollment complete ✅")
            else:
                # Identity verification mode
                sim = float(np.dot(self.reference, emb))
                if sim < 0.80:
                    SCORE.add(Event.now("identity_mismatch", 0.8))
