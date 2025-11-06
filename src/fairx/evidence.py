import cv2, threading
from collections import deque
from time import time

class EvidenceBuffer:
    def __init__(self, fps=20, seconds=15, enabled=True):
        self.enabled = enabled
        self.frames = deque(maxlen=fps * seconds)
        self.fps = fps
        self.size = None

    def push_frame(self, frame):
        if not self.enabled: return
        if self.size is None:
            self.size = (frame.shape[1], frame.shape[0])
        self.frames.append(frame.copy())

    def save_clip_async(self, tag="event"):
        if not self.enabled: return
        threading.Thread(
            target=self._save,
            args=(tag,),
            daemon=True
        ).start()

    def _save(self, tag):
        ts = int(time())
        out_file = f"evidence_{tag}_{ts}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(out_file, fourcc, self.fps, self.size)

        for f in list(self.frames):
            writer.write(f)
        writer.release()
        print(f"[EVIDENCE] Saved: {out_file}")
