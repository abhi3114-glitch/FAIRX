# Video File Testing Guide for FAIRX

This guide explains how to test FAIRX with a video file instead of a live camera feed, perfect for creating demo recordings for LinkedIn posts.

## Method 1: Using OpenCV VideoCapture (Recommended)

### Step 1: Prepare Your Video File
1. Download a test video from YouTube or any source
2. Save it in your FAIRX directory (e.g., `test_video.mp4`)

### Step 2: Modify vision.py for Video Input

Replace the camera initialization in `/workspace/FAIRX/src/fairx/vision.py`:

```python
# Original (line 43-52):
self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
w, h = CFG.camera_resolution
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
self.cap.set(cv2.CAP_PROP_FPS, 30)

# Replace with:
# For video file testing
video_file = "test_video.mp4"  # Your video file path
self.cap = cv2.VideoCapture(video_file)

# Optional: Loop the video
self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to start
```

### Step 3: Add Video Looping (Optional)

Add this code in the `run()` method after line 79:

```python
ok, frame = self.cap.read()
if not ok:
    # Loop video when it ends
    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    ok, frame = self.cap.read()
    if not ok:
        print("[Vision] ⚠️ Video read fail... retrying")
        time.sleep(0.05)
        continue
```

### Step 4: Run FAIRX
```bash
python -m src.fairx.server
```

Visit http://localhost:8000 to see your video being processed!

## Method 2: Create a Dedicated Video Testing Script

Create `/workspace/FAIRX/src/fairx/run_video.py`:

```python
import cv2
import sys
from .vision import VisionThread
from .config import CFG

class VideoVisionThread(VisionThread):
    def __init__(self, video_path):
        # Skip parent __init__ camera setup
        threading.Thread.__init__(self, daemon=True)
        
        self.video_path = video_path
        self.running = True
        
        # Load YOLO model
        from ultralytics import YOLO
        self.model = YOLO(CFG.yolo_model)
        
        # Open video file
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        print(f"[VideoVision] ✅ Loaded video: {video_path}")
        
        # Initialize other attributes
        self.detect_buffer = {c: 0 for c in set(DEVICE_CLASSES.values())}
        self.alert_level = "normal"
    
    def run(self):
        print("[VideoVision] 🎬 Processing video file...")
        # Rest of the run() logic stays the same
        # ... (copy from VisionThread.run())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.fairx.run_video <video_file.mp4>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    thread = VideoVisionThread(video_path)
    thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[VideoVision] 🛑 Stopping...")
        thread.stop()
```

Run with:
```bash
python -m src.fairx.run_video test_video.mp4
```

## Method 3: Using the Web Dashboard

The web dashboard now includes a "Test with Video File" option:

1. Start the server: `python -m src.fairx.server`
2. Open http://localhost:8000
3. Click "Choose File" under "Test with Video File"
4. Select your video file

**Note:** This currently shows a message that video file mode is for local testing. For full video file support, use Method 1 or 2 above.

## Recording Your Demo

### Option A: Screen Recording
1. Use OBS Studio, Loom, or built-in screen recording
2. Record the FAIRX dashboard at http://localhost:8000
3. Show the detection features in action

### Option B: Virtual Camera
1. Use OBS Studio with Virtual Camera plugin
2. Play your video in OBS
3. Set OBS Virtual Camera as Camera 1 (or appropriate index)
4. FAIRX will detect it as a regular camera

### Tips for Great Demo Videos
- Use videos with clear examples of:
  - Phone usage
  - Looking away from screen
  - Multiple people in frame
  - Books/papers on desk
- Ensure good lighting in test videos
- Keep videos 30-60 seconds for LinkedIn posts
- Add text overlays explaining what FAIRX is detecting

## Troubleshooting

### Video Won't Play
```python
# Check video codec support
cap = cv2.VideoCapture("test.mp4")
print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
print(f"Frame count: {cap.get(cv2.CAP_PROP_FRAME_COUNT)}")
print(f"Width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
print(f"Height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
```

### Video Plays Too Fast/Slow
Add frame rate control in the run loop:
```python
import time
fps = self.cap.get(cv2.CAP_PROP_FPS)
frame_delay = 1.0 / fps if fps > 0 else 0.033

while self.running:
    start_time = time.time()
    # ... process frame ...
    
    # Maintain original video FPS
    elapsed = time.time() - start_time
    if elapsed < frame_delay:
        time.sleep(frame_delay - elapsed)
```

## Example LinkedIn Post Structure

```
🚀 Excited to share FAIRX - an AI-powered exam proctoring system!

✅ Real-time detection of:
- 📱 Unauthorized devices (phones, laptops)
- 👀 Gaze tracking & attention monitoring
- 📚 Books and study materials
- 🤚 Suspicious hand gestures
- 🎭 Identity verification

Built with:
- YOLOv8 for object detection
- MediaPipe for face/hand tracking
- FastAPI for real-time streaming
- OpenCV for video processing

[Video Demo]

#AI #MachineLearning #EdTech #Proctoring #ComputerVision
```

---

**Need Help?** Check the main README.md or open an issue on GitHub.