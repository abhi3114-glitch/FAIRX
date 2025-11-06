from time import sleep
from .config import CFG
from .vision import VisionThread
from .gaze import GazeThread
from .identity import IdentityThread
from .audio_vad import VADThread
from .screen_agent import ScreenAgent
from .hand_gesture import HandGestureThread  # NEW
from .movement_detector import MovementDetectorThread  # NEW

if __name__ == "__main__":
    print("="*60)
    print("✅ FAIRX ENHANCED - Running... Press Ctrl+C to stop")
    print("="*60)
    print("\n🎯 Detection Features:")
    print("  ✓ Object Detection (phone, laptop, books, papers)")
    print("  ✓ Gaze Tracking & Face Detection")
    print("  ✓ Identity Verification")
    print("  ✓ Audio/Voice Monitoring")
    print("  ✓ Screen Activity Monitoring")
    print("  ✓ Hand Gesture Detection (NEW)")
    print("  ✓ Movement Detection (NEW)")
    print("  ✓ Color-Coded Alerts (Green/Orange/Red)")
    print("="*60 + "\n")

    cam = CFG.cam_index

    threads = [
        VisionThread(cam_index=cam),
        GazeThread(),
        IdentityThread()
    ]

    # Add optional modules
    if CFG.ENABLE_AUDIO:
        try:
            threads.append(VADThread())
        except Exception as e:
            print(f"⚠️ Audio module failed: {e}")

    if CFG.ENABLE_SCREEN_AGENT:
        threads.append(ScreenAgent())

    if CFG.ENABLE_HAND_DETECTION:
        threads.append(HandGestureThread())

    if CFG.ENABLE_MOVEMENT_DETECTION:
        threads.append(MovementDetectorThread())

    print("🚀 Starting all detection threads...\n")
    for t in threads:
        t.start()

    print("✅ All systems active!\n")

    while True:
        sleep(1)