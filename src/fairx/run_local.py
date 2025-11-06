from time import sleep
import sys
from .config import CFG
from .vision import VisionThread
from .gaze import GazeThread
from .identity import IdentityThread
from .audio_vad import VADThread
from .screen_agent import ScreenAgent
from .hand_gesture import HandGestureThread
from .movement_detector import MovementDetectorThread

if __name__ == "__main__":
    print("="*60)
    print("FAIRX ENHANCED - Running... Press Ctrl+C to stop")
    print("="*60)
    print("\nDetection Features:")
    print("  - Object Detection (phone, laptop, books, papers)")
    print("  - Gaze Tracking & Face Detection")
    print("  - Identity Verification")
    print("  - Audio/Voice Monitoring")
    print("  - Screen Activity Monitoring")
    print("  - Hand Gesture Detection")
    print("  - Movement Detection")
    print("  - Color-Coded Alerts (Green/Orange/Red)")
    print("="*60 + "\n")

    # Check for video file argument
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        print(f"Using video file: {video_path}\n")
        source = video_path
    else:
        source = CFG.cam_index
        print(f"Using camera index: {source}\n")

    threads = [
        VisionThread(source=source),
        GazeThread(),
        IdentityThread()
    ]

    # Add optional modules
    if CFG.ENABLE_AUDIO:
        try:
            threads.append(VADThread())
        except Exception as e:
            print(f"Audio module failed: {e}")

    if CFG.ENABLE_SCREEN_AGENT:
        threads.append(ScreenAgent())

    if CFG.ENABLE_HAND_DETECTION:
        threads.append(HandGestureThread())

    if CFG.ENABLE_MOVEMENT_DETECTION:
        threads.append(MovementDetectorThread())

    print("Starting all detection threads...\n")
    for t in threads:
        t.start()

    print("All systems active!\n")
    print("Usage:")
    print("  - Local mode: python -m src.fairx.run_local [video_file_path]")
    print("  - Web mode: python -m uvicorn src.fairx.server:app --host 0.0.0.0 --port 8000 --reload")
    print()

    while True:
        sleep(1)