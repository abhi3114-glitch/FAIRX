from pydantic import BaseModel
import os

class Weights(BaseModel):
    device: float = 0.40            # phone / laptop confirmed
    whisper: float = 0.25           # voice activity cheating
    gaze: float = 0.18              # looking away repeatedly
    multi_face: float = 0.50        # >1 person visible
    tab_switch: float = 0.15        # switching apps
    exchange: float = 0.25          # suspicious gestures/handover
    liveness_fail: float = 0.30
    identity_mismatch: float = 0.70 # most important
    unknown: float = 0.05           # fallback

class Config(BaseModel):
    # CAMERA INPUT
    cam_index: int = 1               # change if external webcam index
    camera_resolution: tuple = (1280, 720)

    # YOLO MODEL CONFIG
    yolo_model: str = "yolov8n.pt"   # can change to s/m if device strong
    yolo_conf_threshold: float = 0.55
    yolo_min_box_area: int = 800     # ignore tiny boxes

    # GAZE / FACE PARAMETERS
    gaze_yaw_thresh: float = 24.0
    gaze_pitch_thresh: float = 18.0

    # SCORING / DECAY
    score_decay_sec: float = 25.0
    clip_score_threshold: float = 0.55

    # EVIDENCE STORAGE
    evidence_dir: str = "evidence"
    pre_event_sec: int = 4
    post_event_sec: int = 4

    # Prevent repeated same alerts spam
    event_cooldown: dict = {
        "device": 2.0,
        "gaze": 1.2,
        "multi_face": 2.5,
        "identity_mismatch": 2.5,
        "whisper": 1.5,
        "tab_switch": 5.0,
        "exchange": 2.0
    }

    # ENABLE / DISABLE MODULES
    ENABLE_AUDIO: bool = True
    ENABLE_EVIDENCE: bool = True
    ENABLE_IDENTITY: bool = True
    ENABLE_SCREEN_AGENT: bool = False

    # SERVER CONFIG
    port: int = 8000
    
    # attach weights
    weights: Weights = Weights()


CFG = Config()

# Ensure evidence directory exists
os.makedirs(CFG.evidence_dir, exist_ok=True)
