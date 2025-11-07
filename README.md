# 🎓 FAIRX - AI Exam Proctoring System

![Version](https://img.shields.io/badge/version-2.2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Hardware](https://img.shields.io/badge/optimized-RTX%203050-brightgreen.svg)

An advanced AI-powered exam proctoring system with comprehensive cheating detection capabilities. **FULLY FIXED, OPTIMIZED, AND PRODUCTION READY** ✅

---

## 🚀 Features

### ✅ Object Detection (Enhanced & Optimized)
- Phones, laptops, tablets
- Books, notebooks, papers
- Keyboards, mice
- **YOLOv8s model** - optimized for RTX 3050 (4GB VRAM)
- Lowered detection thresholds for better accuracy

### ✅ Hand Gesture Detection
- Suspicious hand movements
- Paper/chit passing between hands
- Hand signals and pointing gestures
- Excessive hand movement tracking

### ✅ Movement Detection
- Excessive body movements
- Position changes
- Suspicious behavior patterns

### ✅ Visual Alert System
- **Green Box**: Normal behavior (score < 0.40)
- **Orange Box**: Warning level (score 0.40-0.65)
- **Red Box**: Danger level (score > 0.65)
- Real-time suspicion score display

### ✅ Camera Selection
- Switch between multiple cameras dynamically
- Auto-detect available cameras
- Perfect for Camo Studio and external cameras
- Web-based camera controls

### ✅ Gaze Tracking
- Face detection and tracking
- Looking away detection
- Multiple face detection

### ✅ Audio Monitoring
- Voice activity detection
- Whisper detection

### ✅ Identity Verification
- Face recognition
- Liveness detection

### ✅ Screen Monitoring
- Tab switching detection
- Suspicious application detection

---

## 💻 Hardware Requirements

### Recommended (Optimized Configuration)
- **GPU**: NVIDIA RTX 3050 (4GB VRAM) or better
- **CPU**: AMD Ryzen 7 6800H or Intel equivalent
- **RAM**: 16GB
- **Storage**: 5GB free space

### Minimum
- **GPU**: Any CUDA-capable GPU with 2GB+ VRAM
- **CPU**: Quad-core processor
- **RAM**: 8GB
- **Storage**: 3GB free space

### Model Selection by Hardware
- **RTX 3050 (4GB)**: YOLOv8s ✅ (Optimal - current default)
- **RTX 3060 (6GB+)**: YOLOv8m (Better accuracy)
- **RTX 4060 (8GB+)**: YOLOv8l (Best accuracy)
- **CPU Only**: YOLOv8n (Fastest, lower accuracy)

---

## 📦 Installation

### 1. Clone Repository
```bash
git clone https://github.com/abhi3114-glitch/FAIRX.git
cd FAIRX
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
- ultralytics (YOLO) - optimized for RTX 3050
- opencv-python
- mediapipe (face mesh + hands)
- webrtcvad (audio detection)
- fastapi + uvicorn (web server)
- torch + torchvision (CUDA support)

### 3. Verify Setup
```bash
python test_setup.py
```

---

## 🎯 Quick Start

### Option 1: Interactive Launcher (Recommended)
```bash
python run_fairx.py
```

### Option 2: Web Server Mode
```bash
python -m src.fairx.server
```
Then open: [http://localhost:8000](http://localhost:8000)

### Option 3: Local Mode (OpenCV Window)
```bash
python -m src.fairx.run_local
```

---

## 🌐 Web Interface

The web interface now includes:

- **Camera Selection**: Choose from available cameras (0, 1, 2, etc.)
- **Auto-Detection**: Automatically detect all available cameras
- **Live Switching**: Change cameras without restarting the server
- **Real-time Monitoring**: Live video feed with alert overlay
- **Statistics Dashboard**: Score, events, FPS tracking
- **Activity Log**: Timestamped event history

---

## 📷 Using with Camo Studio

1. Start Camo Studio
2. Open FAIRX dashboard at [http://localhost:8000](http://localhost:8000)
3. Click "Detect Available" to find your Camo Studio camera
4. Select "Camera 1 (Camo Studio)" from the dropdown
5. Click "Switch Camera"

---

## ⚙️ Configuration

Edit `src/fairx/config.py` to customize:

```python
# Camera Settings
cam_index: int = 0  # 0 for built-in webcam, 1 for Camo Studio/external
camera_resolution: tuple = (1280, 720)

# YOLO Model (Optimized for RTX 3050)
yolo_model: str = "yolov8s.pt"  # Small model - best for RTX 3050

# Detection Thresholds
yolo_conf_threshold: float = 0.40  # Object detection confidence
hand_confidence_threshold: float = 0.60  # Hand detection confidence
movement_threshold: float = 100  # Movement sensitivity

# Alert Thresholds
alert_threshold_warning: float = 0.40  # Orange alert
alert_threshold_danger: float = 0.65  # Red alert

# Feature Flags
ENABLE_AUDIO: bool = True
ENABLE_IDENTITY: bool = True
ENABLE_SCREEN_AGENT: bool = True
ENABLE_HAND_DETECTION: bool = True
ENABLE_MOVEMENT_DETECTION: bool = True
```

### Model Selection for Different Hardware

For **RTX 3060 or better** (6GB+ VRAM):
```python
yolo_model: str = "yolov8m.pt"  # Medium model
```

For **CPU only** or **low-end GPU**:
```python
yolo_model: str = "yolov8n.pt"  # Nano model
```

---

## 📊 Alert System

The system now provides real-time visual feedback:

- **Status Bar**: Shows current alert level and suspicion score
- **Bounding Boxes**: Color-coded based on threat level
  - **Green**: Normal operation
  - **Orange**: Suspicious activity detected
  - **Red**: High-confidence cheating detected
- **Labels**: Enhanced labels with confidence scores
- **Camera Info**: Display current camera index

---

## 🎯 Detected Events

The system detects and logs:

| Event Type | Description | Weight |
|------------|-------------|--------|
| `identity_mismatch` | Wrong person detected | 0.70 |
| `paper_passing` | Paper/chit passing | 0.60 |
| `multi_face` | Multiple people detected | 0.50 |
| `device` | Phone, laptop, book detected | 0.40 |
| `hand_gesture` | Suspicious hand movements | 0.35 |
| `excessive_movement` | Too much body movement | 0.30 |
| `whisper` | Voice activity detected | 0.25 |
| `tab_switch` | Application switching | 0.20 |
| `gaze` | Looking away or face missing | 0.18 |

Scores decay over time (25 seconds) to avoid false positives.

---

## 💾 Evidence Recording

When suspicious activity is detected:

- Screenshots are automatically saved
- Video clips are recorded (4 seconds before + 4 seconds after event)
- All evidence stored in `evidence/` directory

```
evidence/
├── screenshots/
├── videos/
└── logs/
    ├── events.jsonl
    └── session_*.json
```

---

## 🛠️ Troubleshooting

### Camera Not Opening
```python
# Try different camera index in config.py
cam_index: int = 1  # or 0, 2, etc.
```

Or use the web dashboard to auto-detect cameras.

### Camo Studio Not Detected
- Make sure Camo Studio is running
- Click "Detect Available" in the web dashboard
- Try camera indices 0-4 manually
- Restart FAIRX server if needed

### Low FPS / Performance Issues
```python
# For RTX 3050, use YOLOv8s (default - already optimized)
yolo_model: str = "yolov8s.pt"

# If still slow, try nano model
yolo_model: str = "yolov8n.pt"

# Reduce resolution
camera_resolution: tuple = (960, 540)
```

### Out of Memory (CUDA)
```python
# Switch to nano model
yolo_model: str = "yolov8n.pt"

# Or reduce batch size in vision.py
# The system is already optimized for 4GB VRAM
```

### Detection Too Sensitive
```python
# Increase thresholds in config.py
yolo_conf_threshold: float = 0.50  # from 0.40
hand_confidence_threshold: float = 0.70  # from 0.60
```

### Too Many False Positives
```python
# Increase alert thresholds
alert_threshold_warning: float = 0.50  # from 0.40
alert_threshold_danger: float = 0.75  # from 0.65
```

### Hand Detection Not Working
- Ensure good lighting
- Keep hands visible in frame
- Check `ENABLE_HAND_DETECTION: bool = True` in config

---

## 📁 Project Structure

```
FAIRX/
├── src/fairx/
│   ├── __init__.py           # Package initialization (FIXED)
│   ├── config.py             # Configuration (OPTIMIZED for RTX 3050)
│   ├── vision.py             # Object detection (FIXED)
│   ├── gaze.py               # Gaze tracking
│   ├── identity.py           # Face verification
│   ├── audio_vad.py          # Voice detection
│   ├── screen_agent.py       # Screen monitoring
│   ├── hand_gesture.py       # Hand detection (FIXED)
│   ├── movement_detector.py  # Movement detection
│   ├── suspicion.py          # Scoring system (FIXED - SCORE instance added)
│   ├── events.py             # Event handling (FIXED)
│   ├── evidence.py           # Evidence recording (FIXED)
│   ├── frame_buffer.py       # Frame buffer (VERIFIED)
│   ├── startup.py            # Thread initialization
│   ├── run_local.py          # Local runner (FIXED)
│   └── server.py             # Web server (FIXED)
├── evidence/                 # Auto-generated evidence
├── requirements.txt          # Dependencies (VERIFIED)
├── test_setup.py             # Setup verification (UPDATED)
├── run_fairx.py              # Unified launcher
└── README.md                 # This file (UPDATED)
```

---

## 🔧 What's Fixed in v2.2.0

### Critical Bug Fixes
1. ✅ **Missing SCORE instance** - Added global SCORE instance in suspicion.py
2. ✅ **Config import inconsistency** - Standardized all imports to use Config
3. ✅ **Hand gesture module** - Fixed imports and event handling patterns
4. ✅ **Event system** - Updated to use new EventLogger pattern
5. ✅ **Module exports** - Fixed __init__.py exports

### Optimizations
1. ✅ **YOLO Model** - Changed from yolov8n to yolov8s for RTX 3050
2. ✅ **Performance tuning** - Optimized for 4GB VRAM
3. ✅ **Memory management** - Improved frame buffer handling
4. ✅ **Code consistency** - Unified naming conventions

### Documentation
1. ✅ **Hardware requirements** - Added detailed specs
2. ✅ **Model selection guide** - Hardware-specific recommendations
3. ✅ **Troubleshooting** - Expanded with RTX 3050 tips
4. ✅ **Setup verification** - Updated test_setup.py

---

## 🔒 Ethical Use

This system is designed for legitimate exam proctoring purposes only. Ensure:

- Students are informed about monitoring
- Data is handled according to privacy regulations
- Evidence is stored securely
- System is used ethically and legally

---

## 📝 License

This project is for educational and legitimate proctoring purposes only.

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional gesture recognition patterns
- Better false positive reduction
- Multi-language support
- Mobile app integration
- Enhanced video file support

---

## 💡 Support

For issues or questions, please check:

- Configuration settings in `config.py`
- Camera index and permissions (use web dashboard to detect)
- Python version (3.8+ required)
- All dependencies installed correctly
- Hardware compatibility (RTX 3050 optimized)

---

## 📈 Version History

- **v2.2.0** - Hardware optimization (RTX 3050), all bugs fixed, production ready
- **v2.1.0** - Fixed all bugs, enhanced stability, improved documentation
- **v2.0.0** - Added camera selection and web interface
- **v1.0.0** - Initial release

---

**Version**: 2.2.0 (Optimized & Production Ready)  
**Last Updated**: November 2024  
**Status**: ✅ All Issues Resolved | ✅ Optimized for RTX 3050  
**Hardware**: RTX 3050 (4GB) + 16GB RAM + R7 6800H