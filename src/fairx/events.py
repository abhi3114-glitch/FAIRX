from pydantic import BaseModel
from time import time
from .config import CFG

# store last event timestamps to prevent spam
_last_event_time = {}

class Event(BaseModel):
    t: float
    kind: str
    confidence: float
    meta: dict = {}
    evidence: bool = False  # should this event trigger evidence capture?

    @staticmethod
    def now(kind: str, confidence: float, evidence=False, **meta):
        global _last_event_time
        
        ts = time()

        # Anti-spam: cool-down check
        cooldown = CFG.event_cooldown.get(kind, 0)
        last = _last_event_time.get(kind, 0)

        if ts - last < cooldown:
            # too soon, ignore this event
            return None

        _last_event_time[kind] = ts

        # auto-decide if evidence needed
        trigger_evidence = evidence or (confidence >= 0.75)

        return Event(
            t=ts,
            kind=kind,
            confidence=confidence,
            meta=meta,
            evidence=trigger_evidence
        )

    def to_json(self):
        """Clean dict for logging."""
        return {
            "ts": self.t,
            "kind": self.kind,
            "confidence": round(self.confidence, 3),
            "meta": self.meta,
            "evidence": self.evidence
        }
