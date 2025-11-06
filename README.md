# FAIRX - Enhanced AI Exam Proctoring System

An advanced AI-powered exam proctoring system with comprehensive cheating detection capabilities.

## 🚀 New Features (Enhanced Version)

### Detection Capabilities

1. **Object Detection** (Enhanced)
   - Phones, laptops, tablets
   - Books, notebooks, papers
   - Keyboards, mice
   - Lowered detection thresholds for better accuracy

2. **Hand Gesture Detection** (NEW)
   - Suspicious hand movements
   - Paper/chit passing between hands
   - Hand signals and pointing gestures
   - Excessive hand movement tracking

3. **Movement Detection** (NEW)
   - Excessive body movements
   - Position changes
   - Suspicious behavior patterns

4. **Visual Alert System** (NEW)
   - **Green Box**: Normal behavior (score < 0.40)
   - **Orange Box**: Warning level (score 0.40-0.65)
   - **Red Box**: Danger level (score > 0.65)
   - Real-time suspicion score display

5. **Camera Selection** (NEW)
   - Switch between multiple cameras dynamically
   - Auto-detect available cameras
   - Perfect for Camo Studio and external cameras
   - Web-based camera controls

6. **Gaze Tracking**
   - Face detection and tracking
   - Looking away detection
   - Multiple face detection

7. **Audio Monitoring**
   - Voice activity detection
   - Whisper detection

8. **Identity Verification**
   - Face recognition
   - Liveness detection

9. **Screen Monitoring** (Now Enabled)
   - Tab switching detection
   - Suspicious application detection

## 📋 Requirements

```bash
pip install -r requirements.txt
```

### Key Dependencies
- ultralytics (YOLO)
- opencv-python
- mediapipe (face mesh + hands)
- webrtcvad (audio detection)
- fastapi + uvicorn (web server)

## 🎯 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Local Mode
```bash
python -m src.fairx.run_local
```

### 3. Run Web Server Mode (Recommended)
```bash
python -m src.fairx.server
```
Then open: http://localhost:8000

### 4. Using the Web Dashboard

The web interface now includes:
- **Camera Selection**: Choose from available cameras (0, 1, 2, etc.)
- **Auto-Detection**: Automatically detect all available cameras
- **Live Switching**: Change cameras without restarting the server
- **Video File Testing**: Upload video files for testing (see VIDEO_TESTING_GUIDE.md)

#### Camera Setup for Camo Studio Users:
1. Start Camo Studio
2. Open FAIRX dashboard at http://localhost:8000
3. Click "Detect Available" to find your Camo Studio camera
4. Select "Camera 1 (Camo Studio)" from the dropdown
5. Click "Switch Camera"

## ⚙️ Configuration

Edit `src/fairx/config.py` to customize:

### Camera Settings
```python
cam_index: int = 1  # 0 for built-in webcam, 1 for Camo Studio/external
camera_resolution: tuple = (1280, 720)
```

### Detection Thresholds
```python
yolo_conf_threshold: float = 0.40  # Object detection confidence
hand_confidence_threshold: float = 0.60  # Hand detection confidence
movement_threshold: float = 100  # Movement sensitivity
```

### Alert Thresholds
```python
alert_threshold_warning: float = 0.40  # Orange alert
alert_threshold_danger: float = 0.65  # Red alert
```

### Enable/Disable Modules
```python
ENABLE_AUDIO: bool = True
ENABLE_IDENTITY: bool = True
ENABLE_SCREEN_AGENT: bool = True
ENABLE_HAND_DETECTION: bool = True  # NEW
ENABLE_MOVEMENT_DETECTION: bool = True  # NEW
```

## 🎨 Visual Feedback

The system now provides real-time visual feedback:

- **Status Bar**: Shows current alert level and suspicion score
- **Bounding Boxes**: Color-coded based on threat level
  - Green: Normal operation
  - Orange: Suspicious activity detected
  - Red: High-confidence cheating detected
- **Labels**: Enhanced labels with confidence scores
- **Camera Info**: Display current camera index

## 🔍 Detection Events

The system detects and logs:

1. **device** - Phone, laptop, book, keyboard detected
2. **gaze** - Looking away or face missing
3. **multi_face** - Multiple people detected
4. **whisper** - Voice activity detected
5. **identity_mismatch** - Wrong person detected
6. **tab_switch** - Application switching
7. **hand_gesture** - Suspicious hand movements (NEW)
8. **paper_passing** - Paper/chit passing (NEW)
9. **excessive_movement** - Too much body movement (NEW)

## 📊 Suspicion Scoring

Each event has a weight that contributes to the overall suspicion score:

- **Identity Mismatch**: 0.70 (highest)
- **Paper Passing**: 0.60
- **Multiple Faces**: 0.50
- **Device Detection**: 0.40
- **Hand Gestures**: 0.35
- **Excessive Movement**: 0.30
- **Whisper**: 0.25
- **Gaze**: 0.18

Scores decay over time (25 seconds) to avoid false positives from temporary actions.

## 🎥 Evidence Recording

When suspicious activity is detected:
- Screenshots are automatically saved
- Video clips are recorded (4 seconds before + 4 seconds after event)
- All evidence stored in `evidence/` directory

## 🎬 Video File Testing

For creating demo videos or testing without a live camera:
- See **VIDEO_TESTING_GUIDE.md** for detailed instructions
- Use pre-recorded videos for demonstrations
- Perfect for LinkedIn posts and presentations

## 🐛 Troubleshooting

### Camera Not Working
```python
# Try different camera index in config.py
cam_index: int = 1  # or 0, 2, etc.
```

Or use the web dashboard to auto-detect cameras.

### Camo Studio Not Detected
1. Make sure Camo Studio is running
2. Click "Detect Available" in the web dashboard
3. Try camera indices 0-4 manually
4. Restart FAIRX server if needed

### Low Detection Rate
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

## 📁 Project Structure

```
FAIRX/
├── src/fairx/
│   ├── config.py              # Configuration (UPDATED)
│   ├── vision.py              # Object detection (ENHANCED)
│   ├── gaze.py                # Gaze tracking
│   ├── identity.py            # Face verification
│   ├── audio_vad.py           # Voice detection
│   ├── screen_agent.py        # Screen monitoring
│   ├── hand_gesture.py        # Hand detection (NEW)
│   ├── movement_detector.py   # Movement detection (NEW)
│   ├── suspicion.py           # Scoring system
│   ├── events.py              # Event handling
│   ├── evidence.py            # Evidence recording
│   ├── startup.py             # Thread initialization (UPDATED)
│   ├── run_local.py           # Local runner (UPDATED)
│   └── server.py              # Web server (ENHANCED)
├── web/
│   └── index.html             # Web interface (DEPRECATED - see server.py)
├── evidence/                  # Auto-generated evidence
├── VIDEO_TESTING_GUIDE.md     # Video testing instructions (NEW)
├── requirements.txt
└── README.md                  # This file
```

## 🔐 Privacy & Ethics

This system is designed for legitimate exam proctoring purposes only. Ensure:
- Students are informed about monitoring
- Data is handled according to privacy regulations
- Evidence is stored securely
- System is used ethically and legally

## 📝 License

This project is for educational and legitimate proctoring purposes only.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional gesture recognition patterns
- Better false positive reduction
- Multi-language support
- Mobile app integration
- Enhanced video file support

## 📞 Support

For issues or questions, please check:
1. Configuration settings in `config.py`
2. Camera index and permissions (use web dashboard to detect)
3. Python version (3.8+ required)
4. All dependencies installed correctly
5. VIDEO_TESTING_GUIDE.md for demo recording

---

**Version**: 2.1 Enhanced with Camera Selection
**Last Updated**: 2024
**Status**: Production Ready ✅