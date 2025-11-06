from pydantic import BaseModel
from time import time

class Event(BaseModel):
    t: float
    kind: str
    confidence: float
    meta: dict = {}

    @staticmethod
    def now(kind: str, confidence: float, **meta):
        return Event(
            t=time(),
            kind=kind,
            confidence=confidence,
            meta=meta
        )
