import math, threading
from time import time
from collections import deque
from .config import CFG

class SuspicionScore:
    def __init__(self):
        self.lock = threading.Lock()
        self.events = deque(maxlen=5000)
        self.last_event = None

    def add(self, ev):
        with self.lock:
            self.events.append(ev)
            self.last_event = ev

    def score(self):
        now = time()
        s = 0.0
        with self.lock:
            for ev in list(self.events):
                age = now - ev.t
                if age > CFG.score_decay_sec:
                    continue
                decay = math.exp(-age / CFG.score_decay_sec)
                w = getattr(CFG.weights, ev.kind, 0.05)
                s += w * ev.confidence * decay
        return max(0, min(1, s))

SCORE = SuspicionScore()
