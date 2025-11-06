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
    hand_gesture: float = 0.35      # NEW: suspicious hand movements
    paper_passing: float = 0.60     # NEW: paper/chit passing detected
    excessive_movement: float = 0.30 # NEW: too much body movement
    unknown: float = 0.05           # fallback

class Config(BaseModel):
    # CAMERA INPUT
    cam_index: int = 0               # Changed to 0 for built-in webcam (was 1)
    camera_resolution: tuple = (1280, 720)

    # YOLO MODEL CONFIG
    yolo_model: str = "yolov8n.pt"   # can change to s/m if device strong
    yolo_conf_threshold: float = 0.40 # LOWERED from 0.55 for better detection
    yolo_min_box_area: int = 500     # LOWERED from 800 to catch smaller objects

    # GAZE / FACE PARAMETERS
    gaze_yaw_thresh: float = 24.0
    gaze_pitch_thresh: float = 18.0

    # HAND GESTURE DETECTION (NEW)
    hand_confidence_threshold: float = 0.60
    hand_movement_threshold: float = 80  # pixels moved to trigger alert
    gesture_cooldown: float = 2.0

    # MOVEMENT DETECTION (NEW)
    movement_threshold: float = 100  # pixels of body movement
    movement_time_window: float = 1.0  # seconds

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
        "exchange": 2.0,
        "hand_gesture": 2.0,      # NEW
        "paper_passing": 3.0,     # NEW
        "excessive_movement": 2.5 # NEW
    }

    # ENABLE / DISABLE MODULES
    ENABLE_AUDIO: bool = True
    ENABLE_EVIDENCE: bool = True
    ENABLE_IDENTITY: bool = True
    ENABLE_SCREEN_AGENT: bool = True  # ENABLED (was False)
    ENABLE_HAND_DETECTION: bool = True # NEW
    ENABLE_MOVEMENT_DETECTION: bool = True # NEW

    # VISUAL ALERTS (NEW)
    alert_box_color_normal: tuple = (0, 255, 0)  # Green
    alert_box_color_warning: tuple = (0, 165, 255)  # Orange
    alert_box_color_danger: tuple = (0, 0, 255)  # Red
    alert_threshold_warning: float = 0.40
    alert_threshold_danger: float = 0.65

    # SERVER CONFIG
    port: int = 8000
    
    # attach weights
    weights: Weights = Weights()


CFG = Config()

# Ensure evidence directory exists
os.makedirs(CFG.evidence_dir, exist_ok=True)