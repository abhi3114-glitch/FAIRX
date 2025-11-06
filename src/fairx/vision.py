import cv2, threading, time
from ultralytics import YOLO
from .events import Event
from .suspicion import SCORE
from .config import CFG
from .frame_buffer import FRAME_BUFFER
from .evidence import EvidenceRecorder
from time import time as now

# EXPANDED: Map YOLO classes to cheating events
DEVICE_CLASSES = {
    67: "phone",
    63: "laptop",
    0: "person",
    73: "book",        # NEW
    84: "book",        # NEW: alternative book class
    76: "keyboard",    # NEW
    64: "mouse",       # NEW
    77: "cell phone",  # NEW: alternative phone detection
}

# Evidence buffer (auto clips around events)
EBUF = EvidenceRecorder(
    fps=15,
    seconds=CFG.pre_event_sec + CFG.post_event_sec,
    enabled=CFG.ENABLE_EVIDENCE
)

# Cooldown storage
last_trigger = {k: 0 for k in set(DEVICE_CLASSES.values())}

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

        # Detection smoothing buffer - REDUCED threshold from 3 to 2
        self.detect_buffer = {c: 0 for c in set(DEVICE_CLASSES.values())}
        
        # NEW: Track alert state for color coding
        self.alert_level = "normal"  # normal, warning, danger

    def _get_box_color(self, confidence):
        """NEW: Return box color based on confidence and current suspicion score"""
        current_score = SCORE.score()
        
        if current_score >= CFG.alert_threshold_danger or confidence >= 0.80:
            self.alert_level = "danger"
            return CFG.alert_box_color_danger  # RED
        elif current_score >= CFG.alert_threshold_warning or confidence >= 0.60:
            self.alert_level = "warning"
            return CFG.alert_box_color_warning  # ORANGE
        else:
            self.alert_level = "normal"
            return CFG.alert_box_color_normal  # GREEN

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
            
            # NEW: Add status indicator in corner
            current_score = SCORE.score()
            status_color = self._get_box_color(current_score)
            status_text = f"Alert: {self.alert_level.upper()} | Score: {current_score:.2f}"
            cv2.rectangle(annotated, (10, 10), (400, 50), (0, 0, 0), -1)
            cv2.putText(annotated, status_text, (20, 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

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

                        # Detection smoothing - REDUCED from 3 to 2
                        self.detect_buffer[label] += 1

                        # Confirm detection with LOWER threshold
                        if self.detect_buffer[label] >= 2:  # CHANGED from 3
                            t = now()
                            # Cooldown check (prevent spam)
                            if t - last_trigger.get(label, 0) > CFG.event_cooldown.get("device", 2):
                                last_trigger[label] = t

                                SCORE.add(Event.now("device", float(conf), label=label))
                                print(f"[Vision] ⚠️ Device detected: {label} ({conf:.2f})")

                                # Save evidence clip
                                EBUF.save_async(label, confidence=float(conf))

                        # NEW: Draw box with dynamic color based on threat level
                        color = self._get_box_color(float(conf))
                        thickness = 3 if self.alert_level == "danger" else 2
                        
                        cv2.rectangle(annotated,(x1,y1),(x2,y2),color,thickness)
                        
                        # NEW: Enhanced label with background
                        label_text = f"{label} {conf:.2f}"
                        (text_w, text_h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                        cv2.rectangle(annotated, (x1, y1-text_h-10), (x1+text_w+10, y1), color, -1)
                        cv2.putText(
                            annotated, label_text,
                            (x1+5, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
                        )

            # decay buffer
            for k in self.detect_buffer:
                self.detect_buffer[k] = max(0, self.detect_buffer[k] - 1)

            # Update live display buffer
            with FRAME_BUFFER.lock:
                FRAME_BUFFER.frame = annotated

            time.sleep(0.01)