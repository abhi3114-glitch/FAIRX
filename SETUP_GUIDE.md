# FAIRX Enhanced - Setup Guide

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Test Your Camera
```bash
python test_cam.py
```
This will help you find the correct camera index (0, 1, 2, etc.)

### Step 3: Update Camera Index
Edit `src/fairx/config.py`:
```python
cam_index: int = 0  # Change to your camera index from Step 2
```

### Step 4: Run the System
```bash
python -m src.fairx.run_local
```

## ✅ What You Should See

When running successfully:
```
==================================================
🚀 FAIRX STARTUP - ENHANCED VERSION
==================================================
📹 Starting VisionThread on camera index 0
👁 Starting GazeThread (shared feed)
🔐 Starting IdentityThread (shared feed)
🎤 Starting VADThread
🖥 Starting ScreenAgent
✋ Starting HandGestureThread
🏃 Starting MovementDetectorThread
==================================================
✅ FAIRX READY — All systems running
==================================================
```

## 🎯 Testing Each Feature

### 1. Object Detection (Phone, Books)
- Hold a phone in front of camera
- Show a book or notebook
- **Expected**: Green/Orange/Red box appears around object
- **Console**: `[Vision] ⚠️ Device detected: phone (0.XX)`

### 2. Hand Gesture Detection
- Wave hands in front of camera
- Make pointing gestures
- Bring both hands together (simulating paper passing)
- **Expected**: Hand movement alerts
- **Console**: `[HandGesture] ⚠️ Suspicious gesture: pointing`

### 3. Gaze Detection
- Look away from camera (left/right/up/down)
- Turn face away
- **Expected**: Gaze alert
- **Console**: `[Gaze] 👀 Suspicious gaze: yaw=XX, pitch=XX`

### 4. Movement Detection
- Move body significantly
- Change sitting position
- **Expected**: Movement alert
- **Console**: `[Movement] ⚠️ Excessive movement detected`

### 5. Audio Detection
- Speak or whisper
- **Expected**: Audio alert
- **Console**: `[VAD] ⚠️ Whisper detected`

### 6. Screen Monitoring (Windows Only)
- Switch between applications
- Open browser
- **Expected**: Tab switch alert
- **Console**: `[SCREEN] 🔄 Window changed`

## 🎨 Visual Alert System

Watch the bounding boxes change color:

| Color | Meaning | Score Range |
|-------|---------|-------------|
| 🟢 Green | Normal | < 0.40 |
| 🟠 Orange | Warning | 0.40 - 0.65 |
| 🔴 Red | Danger | > 0.65 |

## ⚙️ Customization

### Make Detection More Sensitive
Edit `src/fairx/config.py`:
```python
yolo_conf_threshold: float = 0.35  # Lower = more sensitive
hand_confidence_threshold: float = 0.50
movement_threshold: float = 80
```

### Make Detection Less Sensitive
```python
yolo_conf_threshold: float = 0.55  # Higher = less sensitive
hand_confidence_threshold: float = 0.70
movement_threshold: float = 120
```

### Disable Specific Features
```python
ENABLE_HAND_DETECTION: bool = False
ENABLE_MOVEMENT_DETECTION: bool = False
ENABLE_SCREEN_AGENT: bool = False
```

## 🐛 Common Issues

### Issue: "Camera read fail"
**Solution**: 
1. Check camera index in config.py
2. Ensure no other app is using camera
3. Try different index (0, 1, 2)

### Issue: "No hand detection"
**Solution**:
1. Ensure good lighting
2. Keep hands in frame
3. Lower `hand_confidence_threshold` in config

### Issue: "Too many false alarms"
**Solution**:
1. Increase thresholds in config
2. Increase cooldown times
3. Adjust `event_cooldown` values

### Issue: "Objects not detected"
**Solution**:
1. Lower `yolo_conf_threshold` to 0.35
2. Lower `yolo_min_box_area` to 400
3. Ensure good lighting
4. Hold objects clearly in frame

## 📊 Understanding the Suspicion Score

The score in the top-left corner shows overall suspicion level:

- **0.00 - 0.39**: ✅ Normal behavior (Green)
- **0.40 - 0.64**: ⚠️ Suspicious activity (Orange)
- **0.65 - 1.00**: 🚨 High-confidence cheating (Red)

Score increases when cheating detected, decays over 25 seconds.

## 🎥 Evidence Files

All evidence saved to `evidence/` folder:
- `device_TIMESTAMP.mp4` - Object detection clips
- `gaze_TIMESTAMP.mp4` - Gaze violation clips
- `hand_gesture_TIMESTAMP.mp4` - Hand gesture clips
- `paper_passing_TIMESTAMP.mp4` - Paper passing clips
- `whisper_TIMESTAMP.wav` - Audio evidence

## 🔄 Running as Web Service

```bash
python -m src.fairx.server
```

Then open: http://localhost:8000

## 📝 Next Steps

1. ✅ Test all features individually
2. ✅ Adjust thresholds to your needs
3. ✅ Test in real exam conditions
4. ✅ Review evidence files
5. ✅ Fine-tune configuration

## 💡 Pro Tips

1. **Lighting**: Ensure good, even lighting for best detection
2. **Camera Position**: Place camera at eye level
3. **Background**: Use plain background for better detection
4. **Testing**: Test with real users before actual exam
5. **Privacy**: Inform users about monitoring

## 🆘 Still Having Issues?

Check these files for detailed logs:
- Console output shows all detection events
- Evidence folder shows what was detected
- `config.py` for all settings

---

**Happy Proctoring! 🎓**