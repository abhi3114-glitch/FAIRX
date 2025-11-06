from time import sleep
from .config import CFG
from .vision import VisionThread
from .gaze import GazeThread
from .identity import IdentityThread

if __name__ == "__main__":
    print("✅ FAIRX Running... Press Ctrl+C to stop")

    cam = CFG.cam_index  # ✅ phone camera index

    threads = [
        VisionThread(cam_index=cam),
        GazeThread(cam_index=cam),
        IdentityThread(cam_index=cam)
    ]

    for t in threads:
        t.start()

    while True:
        sleep(1)
