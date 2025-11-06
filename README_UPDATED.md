# FAIRX - Enhanced AI Exam Proctoring System (UPDATED)

## 🎯 Latest Updates - All Issues Fixed

### ✅ Fixed Issues:
1. **Camera Feed Lag** - Optimized frame processing, adjustable quality
2. **Video File Support** - Upload and use video files same as camera
3. **YOLO on Video Files** - Works identically on both camera and video
4. **Modern UI** - Professional dashboard without emojis
5. **All Buttons Working** - Every feature fully functional
6. **Both Run Modes** - Support for local and web server modes

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Test setup
python test_setup.py
```

### Running the System

#### Option 1: Web Dashboard (Recommended)
```bash
python -m uvicorn src.fairx.server:app --host 0.0.0.0 --port 8000 --reload
```
Then open: http://localhost:8000

#### Option 2: Local Mode
```bash
# With camera
python -m src.fairx.run_local

# With video file
python -m src.fairx.run_local path/to/video.mp4
```

#### Windows Quick Start
```bash
# Double-click these files:
start_web.bat      # For web dashboard
start_local.bat    # For local mode
```

## 📊 Features

### Detection Capabilities
- **Object Detection**: Phones, laptops, books, papers, keyboards, mice
- **Gaze Tracking**: Looking away, face missing, multiple faces
- **Hand Gesture Detection**: Suspicious hand movements, paper passing
- **Movement Detection**: Excessive body movement
- **Identity Verification**: Face recognition, liveness detection
- **Audio Monitoring**: Voice activity, whisper detection
- **Screen Monitoring**: Tab switching, suspicious applications

### Visual Alert System
- **Green Box**: Normal behavior (score < 0.40)
- **Orange Box**: Warning level (score 0.40-0.65)
- **Red Box**: Danger level (score > 0.65)
- Real-time suspicion score display

### Video Source Options
1. **Camera Input**: Switch between multiple cameras
2. **Video File Upload**: Upload and process video files
3. **Auto-Detection**: Detect available cameras automatically
4. **Seamless Switching**: Change sources without restart

## ⚡ Performance Optimization (Fix Camera Lag)

### Quick Fix for Laggy Camera
Edit `src/fairx/config.py`:

```python
# PERFORMANCE OPTIMIZATION
frame_skip: int = 2              # Process every 2nd frame
jpeg_quality: int = 65           # Lower quality = faster
camera_resolution: tuple = (640, 480)  # Lower resolution

# YOLO MODEL
yolo_model: str = "yolov8n.pt"   # Fastest model
```

### Performance Presets

**Maximum Speed (No Lag)**:
```python
frame_skip = 3
jpeg_quality = 60
yolo_model = "yolov8n.pt"
camera_resolution = (640, 480)
```

**Balanced (Recommended)**:
```python
frame_skip = 2
jpeg_quality = 65
yolo_model = "yolov8s.pt"
camera_resolution = (1280, 720)
```

**Maximum Accuracy**:
```python
frame_skip = 1
jpeg_quality = 85
yolo_model = "yolov8m.pt"
camera_resolution = (1280, 720)
```

See **PERFORMANCE_GUIDE.md** for detailed optimization instructions.

## 🎮 Using the Web Dashboard

### Camera Controls
1. **Select Camera**: Choose from dropdown (Camera 0, 1, 2, etc.)
2. **Switch Camera**: Click to activate selected camera
3. **Detect Available**: Auto-detect all connected cameras

### Video File Upload
1. **Choose File**: Click "Choose video file..." button
2. **Select Video**: Pick MP4, AVI, MOV, or MKV file
3. **Upload**: Click "Upload & Use Video"
4. **Processing**: System processes video same as camera feed

### System Status
- **Video Connection**: Shows video feed status
- **Score Connection**: Shows scoring system status
- **Suspicion Score**: Real-time threat level (0.00 - 1.00)
- **Recent Events**: Live event log with detections

### Evidence Gallery
- **Auto-Recording**: Evidence saved on suspicious activity
- **Thumbnails**: Visual gallery of captured evidence
- **Refresh**: Update gallery with latest captures
- **View Details**: Click images for full-size view

## 📁 Project Structure

```
FAIRX/
├── src/fairx/
│   ├── config.py              # Main configuration
│   ├── config_optimized.py    # Performance-optimized config
│   ├── video_source.py        # NEW: Unified video source handler
│   ├── vision.py              # Object detection (UPDATED)
│   ├── gaze.py                # Gaze tracking
│   ├── identity.py            # Face verification
│   ├── audio_vad.py           # Voice detection
│   ├── screen_agent.py        # Screen monitoring
│   ├── hand_gesture.py        # Hand detection
│   ├── movement_detector.py   # Movement detection
│   ├── suspicion.py           # Scoring system
│   ├── events.py              # Event handling
│   ├── evidence.py            # Evidence recording
│   ├── frame_buffer.py        # Shared frame buffer
│   ├── startup.py             # Thread initialization (UPDATED)
│   ├── run_local.py           # Local runner (UPDATED)
│   └── server.py              # Web server (REDESIGNED)
├── evidence/                  # Auto-generated evidence
├── uploads/                   # Uploaded video files
├── test_setup.py              # Setup verification script
├── start_web.bat              # Windows web mode launcher
├── start_local.bat            # Windows local mode launcher
├── USAGE_GUIDE.md             # Detailed usage instructions
├── PERFORMANCE_GUIDE.md       # Performance optimization guide
├── FIXES_SUMMARY.md           # Summary of all fixes
└── requirements.txt           # Dependencies
```

## 🔧 Configuration

### Basic Settings
```python
# Camera/Video Source
cam_index: int = 0                    # Default camera
video_file_path: str = None           # Path to video file
camera_resolution: tuple = (1280, 720)

# Performance
frame_skip: int = 1                   # Process every Nth frame
jpeg_quality: int = 75                # JPEG compression quality
enable_gpu: bool = False              # GPU acceleration

# YOLO Detection
yolo_model: str = "yolov8s.pt"        # Model size (n/s/m/l/x)
yolo_conf_threshold: float = 0.38     # Detection confidence
yolo_min_box_area: int = 400          # Minimum detection size
```

### Enable/Disable Modules
```python
ENABLE_AUDIO: bool = True             # Audio monitoring
ENABLE_IDENTITY: bool = True          # Face recognition
ENABLE_SCREEN_AGENT: bool = True      # Screen monitoring
ENABLE_HAND_DETECTION: bool = True    # Hand gestures
ENABLE_MOVEMENT_DETECTION: bool = True # Body movement
ENABLE_EVIDENCE: bool = True          # Evidence recording
```

## 🐛 Troubleshooting

### Camera Feed is Laggy
1. Increase `frame_skip` to 2 or 3
2. Lower `jpeg_quality` to 60-65
3. Use `yolov8n.pt` model
4. Reduce `camera_resolution` to (640, 480)
5. Disable unused modules
6. See **PERFORMANCE_GUIDE.md** for details

### Video File Not Working
1. Ensure file format is supported (MP4, AVI, MOV, MKV)
2. Check file path is correct
3. Try uploading through web interface
4. Verify file is not corrupted

### Camera Not Detected
1. Click "Detect Available" in web dashboard
2. Try different camera indices (0, 1, 2)
3. Ensure camera not used by other apps
4. Restart FAIRX server

### Buttons Not Working
All buttons should now work:
- ✅ Switch Camera
- ✅ Detect Available
- ✅ Upload & Use Video
- ✅ Refresh Evidence

If any button doesn't work, check browser console for errors.

## 📚 Documentation

- **USAGE_GUIDE.md**: Comprehensive usage instructions
- **PERFORMANCE_GUIDE.md**: Detailed performance optimization
- **FIXES_SUMMARY.md**: Summary of all fixes applied
- **VIDEO_TESTING_GUIDE.md**: Video file testing instructions

## 🎯 Testing Checklist

- [ ] Run `python test_setup.py`
- [ ] Test local mode: `python -m src.fairx.run_local`
- [ ] Test web mode: `python -m uvicorn src.fairx.server:app --host 0.0.0.0 --port 8000 --reload`
- [ ] Test camera switching
- [ ] Test video file upload
- [ ] Verify all buttons work
- [ ] Check evidence recording
- [ ] Verify smooth video feed (no lag)

## 🔐 Privacy & Ethics

This system is designed for legitimate exam proctoring purposes only. Ensure:
- Students are informed about monitoring
- Data is handled according to privacy regulations
- Evidence is stored securely
- System is used ethically and legally

## 📞 Support

For issues:
1. Check PERFORMANCE_GUIDE.md for lag issues
2. Check USAGE_GUIDE.md for usage questions
3. Adjust config.py settings as needed
4. Run test_setup.py to verify installation

## 📝 Version History

**Version 2.2 - Latest (All Issues Fixed)**
- ✅ Fixed camera feed lag with optimization
- ✅ Added video file upload and processing
- ✅ YOLO works identically on camera and video
- ✅ Redesigned UI without emojis
- ✅ All buttons fully functional
- ✅ Both run modes properly supported
- ✅ Performance optimization options
- ✅ Comprehensive documentation

**Version 2.1**
- Camera selection feature
- Enhanced detection

**Version 2.0**
- Hand gesture detection
- Movement detection
- Visual alert system

---

**Status**: Production Ready ✅ All Issues Fixed ✅