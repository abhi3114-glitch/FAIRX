import cv2, threading, time
from ultralytics import YOLO
from .events import Event
from .suspicion import SCORE
from .config import CFG
from .frame_buffer import FRAME_BUFFER

DEVICE_CLASSES = {67:"phone", 63:"laptop"}

class VisionThread(threading.Thread):
    def __init__(self, cam_index=0):
        super().__init__(daemon=True)
        self.model = YOLO("yolov8n.pt")
        self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)

        # HD settings for phone webcam
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Verify camera opened
        if not self.cap.isOpened():
            print(f"[VisionThread] ❌ FAILED to open camera at index {cam_index}")
        else:
            print(f"[VisionThread] ✅ Camera opened at index {cam_index}")

    def run(self):
        print("[VisionThread] ✅ Started vision thread")
        frame_count = 0

        while True:
            ok, frame = self.cap.read()
            if not ok:
                print("[VisionThread] ❌ Could not read frame - retrying...")
                time.sleep(0.1)
                continue
            
            frame_count += 1
            
            # Only log every 30 frames to reduce spam
            if frame_count % 30 == 0:
                print(f"[VisionThread] 📷 Frame {frame_count} captured")

            # YOLO inference
            results = self.model.predict(frame, conf=0.4, verbose=False)
            annotated = results[0].plot()

            # Write annotated frame to buffer
            with FRAME_BUFFER.lock:
                FRAME_BUFFER.frame = annotated.copy()

            # Device suspicion scoring
            for r in results:
                for cls, conf in zip(r.boxes.cls.cpu().numpy(), r.boxes.conf.cpu().numpy()):
                    if int(cls) in DEVICE_CLASSES:
                        SCORE.add(Event.now("device", float(conf)))
                        print(f"[VisionThread] 🚨 Device detected: {DEVICE_CLASSES[int(cls)]} ({conf:.2f})")
            
            # Small sleep to prevent CPU overload
            time.sleep(0.01)