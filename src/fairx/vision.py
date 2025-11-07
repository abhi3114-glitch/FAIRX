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
    73: "book",
    84: "book",
    76: "keyboard",
    64: "mouse",
    77: "cell phone",
}

# Evidence buffer
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
        self.cam_index = cam_index
        self.running = True

        # Load YOLO model with enhanced settings
        self.model = YOLO(CFG.yolo_model)
        print(f"[Vision] Loaded YOLO model: {CFG.yolo_model}")
        print(f"[Vision] Model size: {CFG.yolo_model.replace('.pt', '').upper()}")
        print(f"[Vision] Confidence threshold: {CFG.yolo_conf_threshold}")
        print(f"[Vision] Min box area: {CFG.yolo_min_box_area}px")

        self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        w, h = CFG.camera_resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Performance optimization
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.cap.isOpened():
            print(f"[Vision] FAILED to open camera index {cam_index}")
        else:
            print(f"[Vision] Camera ready on index {cam_index}")

        # Detection smoothing buffer
        self.detect_buffer = {c: 0 for c in set(DEVICE_CLASSES.values())}
        
        # Track alert state for color coding
        self.alert_level = "normal"

    def stop(self):
        """Stop the thread gracefully"""
        self.running = False
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        print(f"[Vision] Stopped camera {self.cam_index}")

    def _get_box_color(self, confidence):
        """Return box color based on confidence and current suspicion score"""
        current_score = SCORE.score()
        
        if current_score >= CFG.alert_threshold_danger or confidence >= 0.80:
            self.alert_level = "danger"
            return CFG.alert_box_color_danger
        elif current_score >= CFG.alert_threshold_warning or confidence >= 0.60:
            self.alert_level = "warning"
            return CFG.alert_box_color_warning
        else:
            self.alert_level = "normal"
            return CFG.alert_box_color_normal

    def _process_frame(self, frame, frame_id):
        """Process a single frame with YOLO detection"""
        # Push raw frame into Evidence buffer
        EBUF.push(frame)

        results = None
        if frame_id % 2 == 0:  # YOLO every 2nd frame for performance
            results = self.model.predict(
                frame,
                conf=CFG.yolo_conf_threshold,
                iou=CFG.yolo_iou_threshold,
                imgsz=CFG.yolo_imgsz,
                half=CFG.yolo_half_precision,
                device=CFG.yolo_device,
                verbose=False
            )

        annotated = frame.copy()
        
        # Add status indicator
        current_score = SCORE.score()
        status_color = self._get_box_color(current_score)
        status_text = f"Alert: {self.alert_level.upper()} | Score: {current_score:.2f}"
        model_info = f"Model: {CFG.yolo_model.replace('.pt', '').upper()} | Cam: {self.cam_index}"
        
        # Status background
        cv2.rectangle(annotated, (10, 10), (500, 70), (0, 0, 0), -1)
        cv2.putText(annotated, status_text, (20, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(annotated, model_info, (20, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

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
                    if self.detect_buffer[label] >= 2:
                        t = now()
                        if t - last_trigger.get(label, 0) > CFG.event_cooldown.get("device", 2):
                            last_trigger[label] = t

                            SCORE.add(Event.now("device", float(conf), label=label))
                            print(f"[Vision] Device detected: {label} ({conf:.2f})")

                            EBUF.save_async(label, confidence=float(conf))

                    # Draw box with dynamic color
                    color = self._get_box_color(float(conf))
                    thickness = 3 if self.alert_level == "danger" else 2
                    
                    cv2.rectangle(annotated,(x1,y1),(x2,y2),color,thickness)
                    
                    # Enhanced label with background
                    label_text = f"{label} {conf:.2f}"
                    (text_w, text_h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(annotated, (x1, y1-text_h-10), (x1+text_w+10, y1), color, -1)
                    cv2.putText(
                        annotated, label_text,
                        (x1+5, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
                    )

        # Decay buffer
        for k in self.detect_buffer:
            self.detect_buffer[k] = max(0, self.detect_buffer[k] - 1)

        return annotated

    def run(self):
        print("[Vision] Vision engine running with enhanced YOLO model")

        frame_id = 0
        while self.running:
            ok, frame = self.cap.read()
            if not ok:
                print("[Vision] Camera read fail... retrying")
                time.sleep(0.05)
                continue

            annotated = self._process_frame(frame, frame_id)
            frame_id += 1

            # Update live display buffer
            with FRAME_BUFFER.lock:
                FRAME_BUFFER.frame = annotated

            time.sleep(0.01)
        
        # Cleanup on exit
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()


class VideoFileThread(threading.Thread):
    """Process video file instead of camera feed"""
    def __init__(self, video_path):
        super().__init__(daemon=True)
        self.video_path = video_path
        self.running = True

        # Load YOLO model
        self.model = YOLO(CFG.yolo_model)
        print(f"[VideoFile] Loaded YOLO model: {CFG.yolo_model}")

        # Open video file
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"[VideoFile] Video loaded: {video_path}")
        print(f"[VideoFile] FPS: {self.fps}, Frames: {self.frame_count}")

        # Detection smoothing buffer
        self.detect_buffer = {c: 0 for c in set(DEVICE_CLASSES.values())}
        self.alert_level = "normal"

    def stop(self):
        """Stop the thread gracefully"""
        self.running = False
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        print("[VideoFile] Stopped video processing")

    def _get_box_color(self, confidence):
        """Return box color based on confidence and current suspicion score"""
        current_score = SCORE.score()
        
        if current_score >= CFG.alert_threshold_danger or confidence >= 0.80:
            self.alert_level = "danger"
            return CFG.alert_box_color_danger
        elif current_score >= CFG.alert_threshold_warning or confidence >= 0.60:
            self.alert_level = "warning"
            return CFG.alert_box_color_warning
        else:
            self.alert_level = "normal"
            return CFG.alert_box_color_normal

    def run(self):
        print("[VideoFile] Processing video file...")

        frame_id = 0
        frame_delay = 1.0 / self.fps if self.fps > 0 else 0.033

        while self.running:
            start_time = time.time()
            
            ok, frame = self.cap.read()
            if not ok:
                # Loop video
                print("[VideoFile] End of video - looping...")
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, frame = self.cap.read()
                if not ok:
                    print("[VideoFile] Failed to read video")
                    break

            # Push to evidence buffer
            EBUF.push(frame)

            # Process every 2nd frame
            results = None
            if frame_id % 2 == 0:
                results = self.model.predict(
                    frame,
                    conf=CFG.yolo_conf_threshold,
                    iou=CFG.yolo_iou_threshold,
                    imgsz=CFG.yolo_imgsz,
                    half=CFG.yolo_half_precision,
                    device=CFG.yolo_device,
                    verbose=False
                )

            annotated = frame.copy()
            
            # Add status indicator
            current_score = SCORE.score()
            status_color = self._get_box_color(current_score)
            status_text = f"Alert: {self.alert_level.upper()} | Score: {current_score:.2f}"
            model_info = f"Model: {CFG.yolo_model.replace('.pt', '').upper()} | VIDEO MODE"
            
            cv2.rectangle(annotated, (10, 10), (500, 70), (0, 0, 0), -1)
            cv2.putText(annotated, status_text, (20, 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            cv2.putText(annotated, model_info, (20, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

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

                        self.detect_buffer[label] += 1

                        if self.detect_buffer[label] >= 2:
                            t = now()
                            if t - last_trigger.get(label, 0) > CFG.event_cooldown.get("device", 2):
                                last_trigger[label] = t

                                SCORE.add(Event.now("device", float(conf), label=label))
                                print(f"[VideoFile] Device detected: {label} ({conf:.2f})")

                                EBUF.save_async(label, confidence=float(conf))

                        color = self._get_box_color(float(conf))
                        thickness = 3 if self.alert_level == "danger" else 2
                        
                        cv2.rectangle(annotated,(x1,y1),(x2,y2),color,thickness)
                        
                        label_text = f"{label} {conf:.2f}"
                        (text_w, text_h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                        cv2.rectangle(annotated, (x1, y1-text_h-10), (x1+text_w+10, y1), color, -1)
                        cv2.putText(
                            annotated, label_text,
                            (x1+5, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
                        )

            # Decay buffer
            for k in self.detect_buffer:
                self.detect_buffer[k] = max(0, self.detect_buffer[k] - 1)

            # Update display buffer
            with FRAME_BUFFER.lock:
                FRAME_BUFFER.frame = annotated

            frame_id += 1

            # Maintain original video FPS
            elapsed = time.time() - start_time
            if elapsed < frame_delay:
                time.sleep(frame_delay - elapsed)
        
        # Cleanup
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()