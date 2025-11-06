"""
Optimized configuration for smooth camera feed with minimal lag
Copy this to config.py or adjust your config.py with these settings
"""
from pydantic import BaseModel
import os

class Weights(BaseModel):
    device: float = 0.40
    whisper: float = 0.25
    gaze: float = 0.18
    multi_face: float = 0.50
    tab_switch: float = 0.15
    exchange: float = 0.25
    liveness_fail: float = 0.30
    identity_mismatch: float = 0.70
    hand_gesture: float = 0.35
    paper_passing: float = 0.60
    excessive_movement: float = 0.30
    unknown: float = 0.05

class Config(BaseModel):
    # VIDEO SOURCE
    cam_index: int = 0
    video_file_path: str = None
    camera_resolution: tuple = (1280, 720)  # Lower to (640, 480) for even better performance
    
    # PERFORMANCE OPTIMIZATION - TUNED FOR SMOOTH VIDEO
    frame_skip: int = 2              # Process every 2nd frame (50% faster)
    jpeg_quality: int = 65           # Lower quality = faster streaming
    enable_gpu: bool = False         # Set True if you have CUDA GPU

    # YOLO MODEL CONFIG - OPTIMIZED FOR SPEED
    yolo_model: str = "yolov8n.pt"   # Nano model = fastest (use yolov8s.pt for better accuracy)
    yolo_conf_threshold: float = 0.40 # Slightly higher to reduce false positives
    yolo_min_box_area: int = 500     # Ignore very small detections
    yolo_iou_threshold: float = 0.45
    
    # YOLO Performance Settings
    yolo_imgsz: int = 640            # Don't increase this
    yolo_half_precision: bool = False # Set True if using GPU
    yolo_device: str = "cpu"         # "cuda" if GPU available

    # GAZE / FACE PARAMETERS
    gaze_yaw_thresh: float = 24.0
    gaze_pitch_thresh: float = 18.0

    # HAND GESTURE DETECTION
    hand_confidence_threshold: float = 0.65  # Higher = less false positives
    hand_movement_threshold: float = 100
    gesture_cooldown: float = 2.5

    # MOVEMENT DETECTION
    movement_threshold: float = 120
    movement_time_window: float = 1.0

    # SCORING / DECAY
    score_decay_sec: float = 25.0
    clip_score_threshold: float = 0.55

    # EVIDENCE STORAGE
    evidence_dir: str = "evidence"
    pre_event_sec: int = 3           # Reduced from 4 to save memory
    post_event_sec: int = 3          # Reduced from 4 to save memory

    # Prevent repeated same alerts spam
    event_cooldown: dict = {
        "device": 2.5,               # Increased cooldowns to reduce spam
        "gaze": 1.5,
        "multi_face": 3.0,
        "identity_mismatch": 3.0,
        "whisper": 2.0,
        "tab_switch": 6.0,
        "exchange": 2.5,
        "hand_gesture": 2.5,
        "paper_passing": 3.5,
        "excessive_movement": 3.0
    }

    # ENABLE / DISABLE MODULES - Disable some for better performance
    ENABLE_AUDIO: bool = False       # Disable if not needed
    ENABLE_EVIDENCE: bool = True
    ENABLE_IDENTITY: bool = False    # Disable if not needed
    ENABLE_SCREEN_AGENT: bool = False # Disable if not needed
    ENABLE_HAND_DETECTION: bool = True
    ENABLE_MOVEMENT_DETECTION: bool = True

    # VISUAL ALERTS
    alert_box_color_normal: tuple = (0, 255, 0)
    alert_box_color_warning: tuple = (0, 165, 255)
    alert_box_color_danger: tuple = (0, 0, 255)
    alert_threshold_warning: float = 0.40
    alert_threshold_danger: float = 0.65

    # SERVER CONFIG
    port: int = 8000
    upload_dir: str = "uploads"
    
    # attach weights
    weights: Weights = Weights()


CFG = Config()

# Ensure directories exist
os.makedirs(CFG.evidence_dir, exist_ok=True)
os.makedirs(CFG.upload_dir, exist_ok=True)

print("[CONFIG] Optimized configuration loaded for smooth video feed")
print(f"[CONFIG] Frame skip: {CFG.frame_skip} | JPEG quality: {CFG.jpeg_quality}")
print(f"[CONFIG] YOLO model: {CFG.yolo_model} | Resolution: {CFG.camera_resolution}")