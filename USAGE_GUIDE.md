# FAIRX Usage Guide

## Running the System

### Method 1: Local Mode (Direct Camera/Video Display)
```bash
# With camera
python -m src.fairx.run_local

# With video file
python -m src.fairx.run_local path/to/your/video.mp4
```

### Method 2: Web Dashboard Mode (Recommended)
```bash
python -m uvicorn src.fairx.server:app --host 0.0.0.0 --port 8000 --reload
```
Then open: http://localhost:8000

## Features

### 1. Camera Selection
- Switch between multiple cameras dynamically
- Auto-detect available cameras
- Perfect for external cameras and Camo Studio

### 2. Video File Upload
- Upload video files through the web interface
- System processes video files same as live camera feed
- YOLO model works identically on video files
- Video files automatically loop for continuous testing

### 3. Performance Optimization
- Configurable frame skipping (process every Nth frame)
- Adjustable JPEG quality for streaming
- GPU acceleration support (if available)
- Reduced latency and smoother video feed

### 4. Detection Capabilities
- Object Detection: phones, laptops, books, papers, keyboards
- Gaze Tracking: looking away, face missing
- Hand Gesture Detection: suspicious hand movements
- Movement Detection: excessive body movement
- Identity Verification: face recognition
- Audio Monitoring: voice activity detection
- Screen Monitoring: tab switching detection

### 5. Visual Alerts
- Green: Normal behavior (score < 0.40)
- Orange: Warning level (score 0.40-0.65)
- Red: Danger level (score > 0.65)

## Configuration

Edit `src/fairx/config.py`:

```python
# Performance
frame_skip: int = 1              # Process every Nth frame (1=all, 2=half)
jpeg_quality: int = 75           # JPEG compression (50-95)
enable_gpu: bool = False         # Use GPU if available

# Camera
cam_index: int = 0               # Default camera index
camera_resolution: tuple = (1280, 720)

# YOLO Detection
yolo_model: str = "yolov8s.pt"   # Model size (n/s/m/l/x)
yolo_conf_threshold: float = 0.38 # Detection confidence
```

## Troubleshooting

### Video is Laggy
1. Increase `frame_skip` in config.py (e.g., set to 2 or 3)
2. Lower `jpeg_quality` (e.g., set to 60)
3. Use smaller YOLO model (yolov8n.pt instead of yolov8s.pt)
4. Reduce `camera_resolution` to (640, 480)

### Video File Not Working
1. Ensure video file path is correct
2. Supported formats: MP4, AVI, MOV, MKV
3. Check file permissions
4. Try uploading through web interface instead

### Camera Not Detected
1. Click "Detect Available" button in web dashboard
2. Try different camera indices (0, 1, 2, etc.)
3. Ensure camera is not being used by another application
4. Restart the FAIRX server

### All Buttons Should Work
- Switch Camera: Changes camera source
- Detect Available: Auto-detects all cameras
- Upload & Use Video: Uploads and switches to video file
- Refresh Evidence: Reloads evidence gallery

## Performance Tips

1. **For Better FPS**: Set `frame_skip = 2` and use `yolov8n.pt`
2. **For Better Accuracy**: Set `frame_skip = 1` and use `yolov8m.pt`
3. **For Lower Bandwidth**: Set `jpeg_quality = 60`
4. **For GPU Users**: Set `enable_gpu = True` and `yolo_device = "cuda"`

## Running Both Commands

You can run either command based on your needs:

1. **Local Mode** (`python -m src.fairx.run_local`):
   - Direct OpenCV window display
   - Lower latency
   - Good for testing and development
   - Supports video file as command-line argument

2. **Web Mode** (`python -m uvicorn src.fairx.server:app --host 0.0.0.0 --port 8000 --reload`):
   - Web-based dashboard
   - Remote access capability
   - Better UI with controls
   - Video file upload through interface
   - Multiple simultaneous viewers

Both modes use the same detection engine and produce identical results.