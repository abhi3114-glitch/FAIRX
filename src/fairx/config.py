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
    hand_gesture: float = 0.35      # suspicious hand movements
    paper_passing: float = 0.60     # paper/chit passing detected
    excessive_movement: float = 0.30 # too much body movement
    unknown: float = 0.05           # fallback

class Config(BaseModel):
    # VIDEO SOURCE (Camera or File)
    cam_index: int = 0               # Camera index (0 = default, 1 = external)
    video_file_path: str = None      # Path to video file (overrides camera if set)
    camera_resolution: tuple = (1280, 720)
    
    # PERFORMANCE OPTIMIZATION
    frame_skip: int = 1              # Process every Nth frame (1=all, 2=half, 3=third)
    jpeg_quality: int = 75           # JPEG compression quality for streaming (50-95)
    enable_gpu: bool = False         # Use GPU acceleration if available

    # YOLO MODEL CONFIG
    yolo_model: str = "yolov8s.pt"   # yolov8n/s/m/l/x
    yolo_conf_threshold: float = 0.38
    yolo_min_box_area: int = 400
    yolo_iou_threshold: float = 0.45
    
    # YOLO Performance Settings
    yolo_imgsz: int = 640            # Input image size
    yolo_half_precision: bool = False # Use FP16 for faster inference
    yolo_device: str = "cpu"         # "cpu" or "cuda" or "0" for GPU

    # GAZE / FACE PARAMETERS
    gaze_yaw_thresh: float = 24.0
    gaze_pitch_thresh: float = 18.0

    # HAND GESTURE DETECTION
    hand_confidence_threshold: float = 0.60
    hand_movement_threshold: float = 80
    gesture_cooldown: float = 2.0

    # MOVEMENT DETECTION
    movement_threshold: float = 100
    movement_time_window: float = 1.0

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
        "hand_gesture": 2.0,
        "paper_passing": 3.0,
        "excessive_movement": 2.5
    }

    # ENABLE / DISABLE MODULES
    ENABLE_AUDIO: bool = True
    ENABLE_EVIDENCE: bool = True
    ENABLE_IDENTITY: bool = True
    ENABLE_SCREEN_AGENT: bool = True
    ENABLE_HAND_DETECTION: bool = True
    ENABLE_MOVEMENT_DETECTION: bool = True

    # VISUAL ALERTS
    alert_box_color_normal: tuple = (0, 255, 0)  # Green
    alert_box_color_warning: tuple = (0, 165, 255)  # Orange
    alert_box_color_danger: tuple = (0, 0, 255)  # Red
    alert_threshold_warning: float = 0.40
    alert_threshold_danger: float = 0.65

    # SERVER CONFIG
    port: int = 8000
    upload_dir: str = "uploads"      # Directory for uploaded video files
    
    # attach weights
    weights: Weights = Weights()


CFG = Config()

# Ensure directories exist
os.makedirs(CFG.evidence_dir, exist_ok=True)
os.makedirs(CFG.upload_dir, exist_ok=True)