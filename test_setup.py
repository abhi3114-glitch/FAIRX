"""
Test script to verify FAIRX setup
"""
import sys
import cv2

print("="*60)
print("FAIRX Setup Test")
print("="*60)

# Test imports
print("\n1. Testing imports...")
try:
    from ultralytics import YOLO
    print("   ✓ ultralytics")
except ImportError as e:
    print(f"   ✗ ultralytics: {e}")
    sys.exit(1)

try:
    import cv2
    print("   ✓ opencv-python")
except ImportError as e:
    print(f"   ✗ opencv-python: {e}")
    sys.exit(1)

try:
    import mediapipe
    print("   ✓ mediapipe")
except ImportError as e:
    print(f"   ✗ mediapipe: {e}")
    sys.exit(1)

try:
    from fastapi import FastAPI
    print("   ✓ fastapi")
except ImportError as e:
    print(f"   ✗ fastapi: {e}")
    sys.exit(1)

try:
    import uvicorn
    print("   ✓ uvicorn")
except ImportError as e:
    print(f"   ✗ uvicorn: {e}")
    sys.exit(1)

# Test FAIRX modules
print("\n2. Testing FAIRX modules...")
try:
    from src.fairx.config import CFG
    print("   ✓ config")
except ImportError as e:
    print(f"   ✗ config: {e}")
    sys.exit(1)

try:
    from src.fairx.video_source import VideoSource
    print("   ✓ video_source")
except ImportError as e:
    print(f"   ✗ video_source: {e}")
    sys.exit(1)

try:
    from src.fairx.vision import VisionThread
    print("   ✓ vision")
except ImportError as e:
    print(f"   ✗ vision: {e}")
    sys.exit(1)

try:
    from src.fairx.server import app
    print("   ✓ server")
except ImportError as e:
    print(f"   ✗ server: {e}")
    sys.exit(1)

# Test camera detection
print("\n3. Testing camera detection...")
available_cameras = []
for i in range(3):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        available_cameras.append(i)
        cap.release()

if available_cameras:
    print(f"   ✓ Found cameras: {available_cameras}")
else:
    print("   ⚠ No cameras detected (this is OK if using video files)")

# Test YOLO model
print("\n4. Testing YOLO model...")
try:
    model = YOLO("yolov8n.pt")
    print("   ✓ YOLO model loaded successfully")
except Exception as e:
    print(f"   ⚠ YOLO model: {e}")
    print("   Note: Model will be downloaded on first run")

print("\n" + "="*60)
print("Setup test completed!")
print("="*60)
print("\nYou can now run:")
print("  1. python -m src.fairx.run_local")
print("  2. python -m uvicorn src.fairx.server:app --host 0.0.0.0 --port 8000 --reload")
print()