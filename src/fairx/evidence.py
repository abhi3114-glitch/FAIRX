import cv2, threading, os, json
from collections import deque
from time import time, strftime, localtime
from .config import CFG

class EvidenceRecorder:
    def __init__(self, fps=15, seconds=12, enabled=True):
        self.enabled = enabled
        self.fps = fps
        self.buffer = deque(maxlen=fps * seconds)
        self.size = None
        self.lock = threading.Lock()

        os.makedirs(CFG.evidence_dir, exist_ok=True)
        self.log_file = os.path.join(CFG.evidence_dir, "log.jsonl")

    def push(self, frame):
        if not self.enabled or frame is None:
            return
        
        if self.size is None:
            self.size = (frame.shape[1], frame.shape[0])

        with self.lock:
            self.buffer.append(frame.copy())

    #
    # -------- IMAGE EVIDENCE (snapshot) --------
    #
    def save_image(self, frame, tag, confidence):
        ts = time()
        readable = strftime("%Y-%m-%d_%H-%M-%S", localtime(ts))
        filename = f"{tag}_{readable}.jpg"
        path = os.path.join(CFG.evidence_dir, filename)

        cv2.imwrite(path, frame)

        log = {
            "ts": readable,
            "image": filename,
            "kind": tag,
            "confidence": confidence,
            "type": "image"
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(log) + "\n")

        print(f"[EVIDENCE] 📸 Snapshot saved: {path}")

    #
    # -------- VIDEO CLIP EVIDENCE --------
    #
    def save_clip_async(self, tag="event", confidence=0):
        if not self.enabled:
            return
        threading.Thread(
            target=self._save_clip,
            args=(tag, confidence),
            daemon=True
        ).start()

    def save_async(self, tag="event", confidence=0):
        """Alias for save_clip_async - used by other modules"""
        return self.save_clip_async(tag, confidence)

    def _save_clip(self, tag, confidence):
        ts = time()
        readable = strftime("%Y-%m-%d_%H-%M-%S", localtime(ts))
        filename = f"{tag}_{readable}.mp4"
        path = os.path.join(CFG.evidence_dir, filename)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(path, fourcc, self.fps, self.size)

        with self.lock:
            frames = list(self.buffer)

        for f in frames:
            writer.write(f)
        writer.release()

        log = {
            "ts": readable,
            "file": filename,
            "kind": tag,
            "confidence": confidence,
            "frames": len(frames),
            "type": "video"
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(log) + "\n")

        print(f"[EVIDENCE] 🎥 Clip saved: {path} ({len(frames)} frames)")