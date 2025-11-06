"""
Startup module to initialize all camera threads before FastAPI starts
"""
from .config import CFG
from .vision import VisionThread
from .gaze import GazeThread
from .identity import IdentityThread
from .audio_vad import VADThread
from .screen_agent import ScreenAgent

# Global flag to avoid duplicate thread startups
_threads_started = False

def start_all_threads():
    global _threads_started

    if _threads_started:
        print("[STARTUP] Threads already running — skipping.")
        return

    print("\n" + "="*50)
    print("🚀 FAIRX STARTUP")
    print("="*50)

    threads = []

    # ✅ Vision only — ONLY ONE CAMERA CAPTURE
    cam = CFG.cam_index
    print(f"📹 Starting VisionThread on camera index {cam}")
    threads.append(VisionThread(cam_index=cam))

    # ✅ Gaze — now reads from FRAME_BUFFER, do NOT pass cam index
    print("👁 Starting GazeThread (shared feed)")
    threads.append(GazeThread())

    # ✅ Identity — also uses FRAME_BUFFER only
    if CFG.ENABLE_IDENTITY:
        print("🔐 Starting IdentityThread (shared feed)")
        threads.append(IdentityThread())  # Removed cam_index

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

    # ✅ Launch all threads
    print("\n🔧 Launching threads...")
    for t in threads:
        t.start()

    _threads_started = True

    print("="*50)
    print("✅ FAIRX READY — All systems running")
    print("="*50 + "\n")
