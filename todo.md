# FAIRX Fixes - MVP Implementation

## Issues to Fix:
1. ✅ Video lag optimization - reduce frame processing overhead
2. ✅ Video file upload feature - replace camera feed with video file
3. ✅ YOLO model should work on video files same as camera
4. ✅ Improve UI dashboard - remove emojis, modern clean design
5. ✅ Fix all features - ensure every button works
6. ✅ Support both run commands properly:
   - python -m src.fairx.run_local (local mode)
   - python -m uvicorn src.fairx.server:app --host 0.0.0.0 --port 8000 --reload (web mode)

## Files to Create/Modify:
1. src/fairx/config.py - Add video file support config
2. src/fairx/vision.py - Support video file input, optimize performance
3. src/fairx/server.py - Complete UI overhaul, video upload endpoint
4. src/fairx/startup.py - Handle video file initialization
5. src/fairx/video_source.py - NEW: Unified video source handler
6. requirements.txt - Ensure all dependencies

## Implementation Plan:
- Create video_source.py to handle both camera and video file inputs
- Optimize frame processing to reduce lag (skip frames, lower resolution options)
- Add video file upload API endpoint
- Redesign dashboard UI (no emojis, professional look)
- Ensure all buttons are functional
- Test both run modes