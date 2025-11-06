"""
Startup module to initialize all camera threads before FastAPI starts
This should be imported by the server to ensure threads are running
"""
from .config import CFG
from .vision import VisionThread
from .gaze import GazeThread
from .identity import IdentityThread
from .audio_vad import VADThread
from .screen_agent import ScreenAgent

# Global thread instances
_threads_started = False

def start_all_threads():
    """Start all monitoring threads"""
    global _threads_started
    
    if _threads_started:
        print("[STARTUP] Threads already started, skipping...")
        return
    
    print("\n" + "="*50)
    print("🚀 FAIRX STARTING UP")
    print("="*50)
    
    threads = []
    cam = CFG.cam_index
    
    # Vision thread (primary camera capture)
    print(f"📹 Initializing Vision thread (camera index: {cam})...")
    threads.append(VisionThread(cam_index=cam))
    
    # Gaze detection
    print("👁 Initializing Gaze detection...")
    threads.append(GazeThread(cam_index=cam))
    
    # Identity verification
    if CFG.ENABLE_IDENTITY:
        print("🔐 Initializing Identity verification...")
        threads.append(IdentityThread(cam_index=cam))
    
    # Audio VAD
    if CFG.ENABLE_AUDIO:
        print("🎤 Initializing Audio VAD...")
        try:
            threads.append(VADThread())
        except Exception as e:
            print(f"⚠ Audio VAD failed: {e}")
    
    # Screen monitoring
    if CFG.ENABLE_SCREEN_AGENT:
        print("🖥 Initializing Screen Agent...")
        threads.append(ScreenAgent())
    
    # Start all threads
    print("\n🔧 Starting all threads...")
    for t in threads:
        t.start()
    
    _threads_started = True
    
    print("="*50)
    print("✅ FAIRX READY - All threads started!")
    print("="*50 + "\n")