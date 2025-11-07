# 🎓 FAIRX - AI Exam Proctoring System

![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

An advanced AI-powered exam proctoring system with comprehensive cheating detection capabilities. **FULLY FIXED AND PRODUCTION READY** ✅

---

## 🚀 Features

### ✅ Object Detection (Enhanced)
- Phones, laptops, tablets
- Books, notebooks, papers
- Keyboards, mice
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
- ultralytics (YOLO)
- opencv-python
- mediapipe (face mesh + hands)
- webrtcvad (audio detection)
- fastapi + uvicorn (web server)

---

## 🎯 Quick Start

### Option 1: Local Mode (OpenCV Window)
```bash
python -m src.fairx.run_local
```

### Option 2: Web Server Mode (Recommended)
```bash
python -m src.fairx.server
```

Then open: [http://localhost:8000](http://localhost:8000)

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

### Detection Too Sensitive
```python
# Lower thresholds in config.py
yolo_conf_threshold: float = 0.35  # from 0.40
yolo_min_box_area: int = 400  # from 500
```

### Too Many False Positives
```python
# Increase thresholds
yolo_conf_threshold: float = 0.50
hand_confidence_threshold: float = 0.70
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
│   ├── __init__.py           # Package initialization (NEW)
│   ├── config.py             # Configuration (FIXED)
│   ├── vision.py             # Object detection (FIXED)
│   ├── gaze.py               # Gaze tracking
│   ├── identity.py           # Face verification
│   ├── audio_vad.py          # Voice detection
│   ├── screen_agent.py       # Screen monitoring
│   ├── hand_gesture.py       # Hand detection
│   ├── movement_detector.py  # Movement detection
│   ├── suspicion.py          # Scoring system (FIXED)
│   ├── events.py             # Event handling (FIXED)
│   ├── evidence.py           # Evidence recording
│   ├── startup.py            # Thread initialization
│   ├── run_local.py          # Local runner (FIXED)
│   └── server.py             # Web server (FIXED)
├── evidence/                 # Auto-generated evidence
├── requirements.txt          # Dependencies (FIXED)
└── README.md                 # This file (UPDATED)
```

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

---

## 📈 Version History

- **v2.1.0** - Fixed all bugs, enhanced stability, improved documentation
- **v2.0.0** - Added camera selection and web interface
- **v1.0.0** - Initial release

---

**Version**: 2.1.0 (Fixed & Production Ready)  
**Last Updated**: November 2024  
**Status**: ✅ All Issues Resolved