from pydantic import BaseModel

class Weights(BaseModel):
    device: float = 0.35
    whisper: float = 0.25
    gaze: float = 0.15
    multi_face: float = 0.15
    tab_switch: float = 0.05
    exchange: float = 0.05
    liveness_fail: float = 0.1
    identity_mismatch: float = 0.2

class Config(BaseModel):
    cam_index: int = 1
    vad_frame_ms: int = 20
    gaze_yaw_thresh: float = 25.0
    gaze_pitch_thresh: float = 20.0
    score_decay_sec: float = 30.0
    pre_event_sec: int = 5
    post_event_sec: int = 5
    port: int = 8000

    ENABLE_AUDIO: bool = True
    ENABLE_EVIDENCE: bool = True
    ENABLE_IDENTITY: bool = True
    ENABLE_SCREEN_AGENT: bool = False

    weights: Weights = Weights()

CFG = Config()
