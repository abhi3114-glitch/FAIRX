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
    from src.fairx.config import Config
    print("   ✓ config")
except ImportError as e:
    print(f"   ✗ config: {e}")
    sys.exit(1)

try:
    from src.fairx.suspicion import SCORE
    print("   ✓ suspicion (SCORE instance)")
except ImportError as e:
    print(f"   ✗ suspicion: {e}")
    sys.exit(1)

try:
    from src.fairx.vision import VisionDetector
    print("   ✓ vision")
except ImportError as e:
    print(f"   ✗ vision: {e}")
    sys.exit(1)

try:
    from src.fairx.events import EventLogger
    print("   ✓ events")
except ImportError as e:
    print(f"   ✗ events: {e}")
    sys.exit(1)

try:
    from src.fairx.evidence import EvidenceRecorder
    print("   ✓ evidence")
except ImportError as e:
    print(f"   ✗ evidence: {e}")
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
    model = YOLO("yolov8s.pt")
    print("   ✓ YOLO model (yolov8s) loaded successfully")
    print("   ℹ Optimized for RTX 3050 (4GB VRAM)")
except Exception as e:
    print(f"   ⚠ YOLO model: {e}")
    print("   Note: Model will be downloaded on first run")

print("\n" + "="*60)
print("Setup test completed!")
print("="*60)
print("\nHardware Optimization:")
print("  • YOLO Model: YOLOv8s (optimal for RTX 3050)")
print("  • Target Hardware: RTX 3050 + 16GB RAM + R7 6800H")
print("\nYou can now run:")
print("  1. python -m src.fairx.run_local")
print("  2. python -m src.fairx.server")
print("  3. python run_fairx.py")
print()