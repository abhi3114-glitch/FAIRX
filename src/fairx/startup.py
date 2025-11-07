"""
Startup module to initialize all camera threads before FastAPI starts
"""
from .config import CFG
from .vision import VisionThread, VideoFileThread
from .gaze import GazeThread
from .identity import IdentityThread
from .audio_vad import VADThread
from .screen_agent import ScreenAgent
from .hand_gesture import HandGestureThread
from .movement_detector import MovementDetectorThread

# Global flag to avoid duplicate thread startups
_threads_started = False
_vision_thread = None
_other_threads = []

def stop_vision_thread():
    """Stop the current vision thread"""
    global _vision_thread
    
    if _vision_thread is not None:
        print("[STARTUP] Stopping vision thread...")
        _vision_thread.stop()
        _vision_thread = None

def restart_vision_thread(cam_index):
    """Restart vision thread with new camera index"""
    global _vision_thread
    
    stop_vision_thread()
    
    print(f"[STARTUP] Starting new vision thread on camera {cam_index}")
    _vision_thread = VisionThread(cam_index=cam_index)
    _vision_thread.start()
    print(f"[STARTUP] Vision thread restarted on camera {cam_index}")

def start_video_file_mode(video_path):
    """Start vision thread in video file mode"""
    global _vision_thread
    
    stop_vision_thread()
    
    print(f"[STARTUP] Starting video file mode: {video_path}")
    _vision_thread = VideoFileThread(video_path=video_path)
    _vision_thread.start()
    print(f"[STARTUP] Video file thread started")

def start_all_threads():
    global _threads_started, _vision_thread, _other_threads

    if _threads_started:
        print("[STARTUP] Threads already running - skipping.")
        return

    print("\n" + "="*50)
    print("FAIRX STARTUP - ENHANCED VERSION")
    print("="*50)

    # Vision thread - ONLY ONE CAMERA CAPTURE
    cam = CFG.cam_index
    print(f"[Vision] Starting VisionThread on camera index {cam}")
    _vision_thread = VisionThread(cam_index=cam)
    _vision_thread.start()

    # Gaze - reads from FRAME_BUFFER
    print("[Gaze] Starting GazeThread (shared feed)")
    _other_threads.append(GazeThread())

    # Identity - uses FRAME_BUFFER only
    if CFG.ENABLE_IDENTITY:
        print("[Identity] Starting IdentityThread (shared feed)")
        _other_threads.append(IdentityThread())

    # Audio VAD
    if CFG.ENABLE_AUDIO:
        try:
            print("[Audio] Starting VADThread")
            _other_threads.append(VADThread())
        except Exception as e:
            print(f"[Audio] VAD failed: {e}")

    # Screen agent
    if CFG.ENABLE_SCREEN_AGENT:
        print("[Screen] Starting ScreenAgent")
        _other_threads.append(ScreenAgent())

    # Hand Gesture Detection
    if CFG.ENABLE_HAND_DETECTION:
        print("[Hand] Starting HandGestureThread")
        _other_threads.append(HandGestureThread())

    # Movement Detection
    if CFG.ENABLE_MOVEMENT_DETECTION:
        print("[Movement] Starting MovementDetectorThread")
        _other_threads.append(MovementDetectorThread())

    # Launch all threads
    print("\n[System] Launching threads...")
    for t in _other_threads:
        t.start()

    _threads_started = True

    print("="*50)
    print("FAIRX READY - All systems running")
    print("Active Modules:")
    print("   - Object Detection (phones, laptops, books)")
    print("   - Gaze Tracking")
    print("   - Identity Verification")
    print("   - Audio Monitoring")
    print("   - Screen Activity Monitoring")
    print("   - Hand Gesture Detection")
    print("   - Movement Detection")
    print("   - Visual Alert System (Green/Orange/Red)")
    print("="*50 + "\n")