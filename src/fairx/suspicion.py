import math, threading
from time import time
from collections import deque
from .config import CFG
from .evidence import EvidenceRecorder

class SuspicionScore:
    def __init__(self):
        self.lock = threading.Lock()
        self.events = deque(maxlen=5000)
        self.last_event = None
        self.last_trigger = {}
        self.evidence = EvidenceRecorder()

    def _base_score(self):
        """Compute current suspicion score"""
        now = time()
        s = 0.0
        with self.lock:
            for ev in list(self.events):
                age = now - ev.t
                if age > CFG.score_decay_sec:
                    continue
                decay = math.exp(-age / CFG.score_decay_sec)
                weight = getattr(CFG.weights, ev.kind, 0.05)
                s += weight * ev.confidence * decay
        return max(0, min(1, s))

    def score(self):
        return self._base_score()

    def trigger_event(self, ev, frame=None):
        """Add event + handle evidence + debounce spam"""
        now = time()
        cool = CFG.event_cooldown.get(ev.kind, 1.5)

        # Debounce repeat events
        if ev.kind in self.last_trigger and now - self.last_trigger[ev.kind] < cool:
            return

        self.last_trigger[ev.kind] = now

        with self.lock:
            self.events.append(ev)
            self.last_event = ev

        score = self._base_score()

        # Save evidence
        if frame is not None:
            # Snap picture for all events
            self.evidence.save_image(frame, ev.kind, ev.confidence)

            # If extremely suspicious, save clip too
            if score >= CFG.clip_score_threshold:
                self.evidence.save_clip_async(ev.kind, ev.confidence)

        print(f"[SCORE] 🔔 Event: {ev.kind}, conf={ev.confidence:.2f}, score={score:.2f}")
