"""
Startup module to initialize all camera threads before FastAPI starts
"""
from .config import CFG
from .vision import VisionThread
from .gaze import GazeThread
from .identity import IdentityThread
from .audio_vad import VADThread
from .screen_agent import ScreenAgent
from .hand_gesture import HandGestureThread  # NEW
from .movement_detector import MovementDetectorThread  # NEW

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
    _vision_thread = VisionThread(cam_index=cam_index)
    _vision_thread.start()
    print(f"[STARTUP] ✅ Vision thread restarted on camera {cam_index}")

def start_all_threads():
    global _threads_started, _vision_thread

    if _threads_started:
        print("[STARTUP] Threads already running — skipping.")
        return

    print("\n" + "="*50)
    print("🚀 FAIRX STARTUP - ENHANCED VERSION")
    print("="*50)

    threads = []

    # ✅ Vision only — ONLY ONE CAMERA CAPTURE
    cam = CFG.cam_index
    print(f"📹 Starting VisionThread on camera index {cam}")
    _vision_thread = VisionThread(cam_index=cam)
    threads.append(_vision_thread)

    # ✅ Gaze — now reads from FRAME_BUFFER, do NOT pass cam index
    print("👁 Starting GazeThread (shared feed)")
    threads.append(GazeThread())

    # ✅ Identity — also uses FRAME_BUFFER only
    if CFG.ENABLE_IDENTITY:
        print("🔐 Starting IdentityThread (shared feed)")
        threads.append(IdentityThread())

    # ✅ Audio VAD
    if CFG.ENABLE_AUDIO:
        try:
            print("🎤 Starting VADThread")
            threads.append(VADThread())
        except Exception as e:
            print(f"⚠ Audio VAD failed: {e}")

    # ✅ Screen agent
    if CFG.ENABLE_SCREEN_AGENT:
        print("🖥 Starting ScreenAgent")
        threads.append(ScreenAgent())

    # ✅ NEW: Hand Gesture Detection
    if CFG.ENABLE_HAND_DETECTION:
        print("✋ Starting HandGestureThread")
        threads.append(HandGestureThread())

    # ✅ NEW: Movement Detection
    if CFG.ENABLE_MOVEMENT_DETECTION:
        print("🏃 Starting MovementDetectorThread")
        threads.append(MovementDetectorThread())

    # ✅ Launch all threads
    print("\n🔧 Launching threads...")
    for t in threads:
        t.start()

    _threads_started = True

    print("="*50)
    print("✅ FAIRX READY — All systems running")
    print("📊 Active Modules:")
    print("   - Object Detection (phones, laptops, books)")
    print("   - Gaze Tracking")
    print("   - Identity Verification")
    print("   - Audio Monitoring")
    print("   - Screen Activity Monitoring")
    print("   - Hand Gesture Detection (NEW)")
    print("   - Movement Detection (NEW)")
    print("   - Visual Alert System (Green/Orange/Red)")
    print("="*50 + "\n")