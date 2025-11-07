# FAIRX Bug Fixes and Optimization TODO

## Critical Bugs to Fix

### 1. Missing SCORE Instance in suspicion.py ✅
- **File**: `src/fairx/suspicion.py`
- **Issue**: Class `SuspicionTracker` exists but no `SCORE` instance is created
- **Impact**: ImportError in hand_gesture.py and other modules
- **Fix**: Create global SCORE instance at end of file

### 2. Config Import Inconsistency ✅
- **Files**: Multiple files use different config imports
- **Issue**: Some use `from .config import Config`, others use `from .config import CFG`
- **Impact**: NameError at runtime
- **Fix**: Standardize all imports to use `Config`

### 3. Missing save_async Method in evidence.py ✅
- **File**: `src/fairx/evidence.py`
- **Issue**: Method exists but other modules may call it
- **Status**: Already implemented as alias (line 63-65)
- **Action**: Verify it works correctly

### 4. Event System Issues ✅
- **File**: `src/fairx/events.py`
- **Issue**: Old Event.now() pattern referenced in hand_gesture.py
- **Fix**: Update hand_gesture.py to use new EventLogger pattern

### 5. YOLO Model Optimization ✅
- **File**: `src/fairx/config.py`
- **Issue**: Using yolov8n.pt (nano) but user has RTX 3050
- **Hardware**: RTX 3050 (4GB VRAM), 16GB RAM, R7 6800H
- **Optimal Model**: YOLOv8s.pt (small) - best balance for RTX 3050
- **Fix**: Change to yolov8s.pt for better accuracy with acceptable speed

### 6. Missing __init__.py Exports ✅
- **File**: `src/fairx/__init__.py`
- **Issue**: May not export necessary classes
- **Fix**: Add proper exports

### 7. Hand Gesture Module Issues ✅
- **File**: `src/fairx/hand_gesture.py`
- **Issues**:
  - Uses old Event.now() pattern
  - Uses CFG instead of Config
  - References SCORE before it's imported properly
- **Fix**: Update to use new patterns

### 8. Missing Dependencies ✅
- **File**: `requirements.txt`
- **Check**: Ensure all required packages are listed
- **Add if missing**: soundfile, pyaudio alternatives

### 9. Frame Buffer Module ✅
- **File**: Referenced in hand_gesture.py but not examined
- **Action**: Check if frame_buffer.py exists and works

### 10. README Updates ✅
- Update version to reflect fixes
- Add hardware recommendations
- Update YOLO model information
- Add troubleshooting for RTX 3050

## Files to Create/Update

1. ✅ src/fairx/suspicion.py - Add SCORE instance
2. ✅ src/fairx/config.py - Optimize YOLO model
3. ✅ src/fairx/hand_gesture.py - Fix imports and patterns
4. ✅ src/fairx/__init__.py - Add proper exports
5. ✅ src/fairx/evidence.py - Verify save_async works
6. ✅ README.md - Update documentation
7. ✅ requirements.txt - Verify dependencies

## Testing Checklist

- [ ] Import all modules successfully
- [ ] Run test_setup.py
- [ ] Test camera detection
- [ ] Test object detection with new YOLO model
- [ ] Test web server startup
- [ ] Test local mode startup
- [ ] Verify evidence recording
- [ ] Check suspicion scoring

## Git Push Checklist

- [ ] All bugs fixed
- [ ] All tests passing
- [ ] README updated
- [ ] Commit changes
- [ ] Push to GitHub with provided token