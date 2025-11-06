"""
Startup module to initialize all camera threads before FastAPI starts
"""
from .config import CFG
from .vision import VisionThread
from .gaze import GazeThread
from .identity import IdentityThread
from .audio_vad import VADThread
from .screen_agent import ScreenAgent
from .hand_gesture import HandGestureThread
from .movement_detector import MovementDetectorThread

# Global flag to avoid duplicate thread startups
_threads_started = False
_vision_thread = None

def restart_vision_thread(cam_index):
    """Restart vision thread with new camera index"""
    global _vision_thread
    
    if _vision_thread is not None:
        print(f"[STARTUP] Stopping old vision thread...")
        _vision_thread.stop()
        _vision_thread = None
    
    print(f"[STARTUP] Starting new vision thread on camera {cam_index}")
    _vision_thread = VisionThread(source=cam_index)
    _vision_thread.start()
    print(f"[STARTUP] Vision thread restarted on camera {cam_index}")

def switch_to_video_file(video_path):
    """Switch vision thread to use video file"""
    global _vision_thread
    
    if _vision_thread is not None:
        print(f"[STARTUP] Stopping old vision thread...")
        _vision_thread.stop()
        _vision_thread = None
    
    print(f"[STARTUP] Starting vision thread with video file: {video_path}")
    _vision_thread = VisionThread(source=video_path)
    _vision_thread.start()
    print(f"[STARTUP] Vision thread started with video file")

def start_all_threads():
    global _threads_started, _vision_thread

    if _threads_started:
        print("[STARTUP] Threads already running - skipping.")
        return

    print("\n" + "="*60)
    print("FAIRX STARTUP - ENHANCED VERSION")
    print("="*60)

    threads = []

    # Vision thread - supports both camera and video file
    source = CFG.video_file_path if CFG.video_file_path else CFG.cam_index
    source_type = "video file" if CFG.video_file_path else f"camera {CFG.cam_index}"
    print(f"[STARTUP] Starting VisionThread with {source_type}")
    _vision_thread = VisionThread(source=source)
    threads.append(_vision_thread)

    # Gaze - reads from FRAME_BUFFER
    print("[STARTUP] Starting GazeThread (shared feed)")
    threads.append(GazeThread())

    # Identity - uses FRAME_BUFFER only
    if CFG.ENABLE_IDENTITY:
        print("[STARTUP] Starting IdentityThread (shared feed)")
        threads.append(IdentityThread())

    # Audio VAD
    if CFG.ENABLE_AUDIO:
        try:
            print("[STARTUP] Starting VADThread")
            threads.append(VADThread())
        except Exception as e:
            print(f"[STARTUP] Audio VAD failed: {e}")

    # Screen agent
    if CFG.ENABLE_SCREEN_AGENT:
        print("[STARTUP] Starting ScreenAgent")
        threads.append(ScreenAgent())

    # Hand Gesture Detection
    if CFG.ENABLE_HAND_DETECTION:
        print("[STARTUP] Starting HandGestureThread")
        threads.append(HandGestureThread())

    # Movement Detection
    if CFG.ENABLE_MOVEMENT_DETECTION:
        print("[STARTUP] Starting MovementDetectorThread")
        threads.append(MovementDetectorThread())

    # Launch all threads
    print("\n[STARTUP] Launching threads...")
    for t in threads:
        t.start()

    _threads_started = True

    print("="*60)
    print("FAIRX READY - All systems running")
    print("\nActive Modules:")
    print("  - Object Detection (phones, laptops, books)")
    print("  - Gaze Tracking")
    print("  - Identity Verification")
    print("  - Audio Monitoring")
    print("  - Screen Activity Monitoring")
    print("  - Hand Gesture Detection")
    print("  - Movement Detection")
    print("  - Visual Alert System (Green/Orange/Red)")
    print("="*60 + "\n")