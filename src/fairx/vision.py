import cv2, threading, time
from ultralytics import YOLO
from .events import Event
from .suspicion import SCORE
from .config import CFG
from .frame_buffer import FRAME_BUFFER
from .evidence import EvidenceRecorder
from time import time as now

# Map YOLO classes to cheating events
DEVICE_CLASSES = {
    67: "phone",
    63: "laptop",
    0: "person"
}

# Evidence buffer (auto clips around events)
EBUF = EvidenceRecorder(
    fps=15,
    seconds=CFG.pre_event_sec + CFG.post_event_sec,
    enabled=CFG.ENABLE_EVIDENCE
)

# Cooldown storage
last_trigger = {k: 0 for k in DEVICE_CLASSES.values()}

class VisionThread(threading.Thread):
    def __init__(self, cam_index=CFG.cam_index):
        super().__init__(daemon=True)

        self.model = YOLO(CFG.yolo_model)
        print(f"[Vision] ✅ Loaded YOLO model: {CFG.yolo_model}")

        self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        w, h = CFG.camera_resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        if not self.cap.isOpened():
            print(f"[Vision] ❌ FAILED to open camera index {cam_index}")
        else:
            print(f"[Vision] ✅ Camera ready on index {cam_index}")

        # Detection smoothing buffer
        self.detect_buffer = {c: 0 for c in DEVICE_CLASSES.values()}

    def run(self):
        print("[Vision] 🚀 Vision engine running")

        frame_id = 0
        while True:
            ok, frame = self.cap.read()
            if not ok:
                print("[Vision] ⚠️ Camera read fail... retrying")
                time.sleep(0.05)
                continue

            # Push raw frame into Evidence buffer
            EBUF.push(frame)

            frame_id += 1
            results = None
            if frame_id % 2 == 0:  # YOLO every 2nd frame = faster
                results = self.model.predict(
                    frame,
                    conf=CFG.yolo_conf_threshold,
                    imgsz=640,
                    verbose=False
                )

            annotated = frame.copy()

            if results:
                for r in results:
                    if not hasattr(r, "boxes") or r.boxes is None:
                        continue

                    for box, cls, conf in zip(
                        r.boxes.xyxy.cpu().numpy(),
                        r.boxes.cls.cpu().numpy(),
                        r.boxes.conf.cpu().numpy()
                    ):
                        c = int(cls)
                        if c not in DEVICE_CLASSES: continue
                        label = DEVICE_CLASSES[c]

                        x1, y1, x2, y2 = map(int, box)
                        area = (x2 - x1) * (y2 - y1)

                        if area < CFG.yolo_min_box_area:
                            continue

                        # Detection smoothing
                        self.detect_buffer[label] += 1

                        # Confirm detection
                        if self.detect_buffer[label] >= 3:
                            t = now()
                            # Cooldown check (prevent spam)
                            if t - last_trigger[label] > CFG.event_cooldown.get(label, 2):
                                last_trigger[label] = t

                                SCORE.add(Event.now("device", float(conf), label=label))
                                print(f"[Vision] ⚠️ Device detected: {label} ({conf:.2f})")

                                # Save evidence clip
                                EBUF.save_async(label, confidence=float(conf))

                        # Draw box
                        color = (0,255,0)
                        cv2.rectangle(annotated,(x1,y1),(x2,y2),color,2)
                        cv2.putText(
                            annotated, f"{label} {conf:.2f}",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
                        )

            # decay buffer
            for k in self.detect_buffer:
                self.detect_buffer[k] = max(0, self.detect_buffer[k] - 1)

            # Update live display buffer
            with FRAME_BUFFER.lock:
                FRAME_BUFFER.frame = annotated

            time.sleep(0.01)
