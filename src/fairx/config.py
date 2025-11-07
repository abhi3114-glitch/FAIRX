"""
FAIRX Configuration Module
Fixed and optimized configuration settings
"""
from typing import Tuple
import os

class Config:
    """Centralized configuration for FAIRX proctoring system"""
    
    # ============ Camera Settings ============
    cam_index: int = 0  # 0 for built-in, 1+ for external/Camo Studio
    camera_resolution: Tuple[int, int] = (1280, 720)
    fps: int = 30
    
    # ============ YOLO Object Detection ============
    yolo_model: str = "yolov8n.pt"  # Nano model for speed
    yolo_conf_threshold: float = 0.40  # Confidence threshold
    yolo_iou_threshold: float = 0.45  # IoU threshold for NMS
    yolo_min_box_area: int = 500  # Minimum bounding box area
    
    # Suspicious objects to detect
    suspicious_objects = [
        'cell phone', 'phone', 'book', 'laptop', 
        'keyboard', 'mouse', 'tablet', 'notebook',
        'remote', 'tv'
    ]
    
    # ============ Hand Gesture Detection ============
    hand_confidence_threshold: float = 0.60
    hand_detection_enabled: bool = True
    min_hand_detection_confidence: float = 0.5
    
    # ============ Movement Detection ============
    movement_threshold: float = 100  # Pixel difference threshold
    movement_detection_enabled: bool = True
    movement_frames_buffer: int = 5
    
    # ============ Gaze Tracking ============
    gaze_detection_enabled: bool = True
    max_look_away_frames: int = 30  # ~1 second at 30fps
    face_detection_confidence: float = 0.5
    
    # ============ Alert Thresholds ============
    alert_threshold_warning: float = 0.40  # Orange alert
    alert_threshold_danger: float = 0.65   # Red alert
    suspicion_decay_time: float = 25.0  # Seconds for score decay
    
    # ============ Feature Flags ============
    ENABLE_AUDIO: bool = True
    ENABLE_IDENTITY: bool = True
    ENABLE_SCREEN_AGENT: bool = True
    ENABLE_HAND_DETECTION: bool = True
    ENABLE_MOVEMENT_DETECTION: bool = True
    ENABLE_GAZE_TRACKING: bool = True
    ENABLE_EVIDENCE_RECORDING: bool = True
    
    # ============ Audio Detection ============
    audio_sample_rate: int = 16000
    audio_frame_duration_ms: int = 30
    audio_aggressiveness: int = 2  # 0-3, higher = more aggressive
    whisper_threshold: float = 0.5
    
    # ============ Evidence Recording ============
    evidence_dir: str = "evidence"
    screenshot_dir: str = os.path.join(evidence_dir, "screenshots")
    video_dir: str = os.path.join(evidence_dir, "videos")
    log_dir: str = os.path.join(evidence_dir, "logs")
    
    video_clip_duration: int = 8  # seconds (4 before + 4 after)
    max_evidence_age_days: int = 30  # Auto-cleanup old evidence
    
    # ============ Suspicion Scoring Weights ============
    WEIGHTS = {
        'identity_mismatch': 0.70,
        'paper_passing': 0.60,
        'multi_face': 0.50,
        'device': 0.40,
        'hand_gesture': 0.35,
        'excessive_movement': 0.30,
        'whisper': 0.25,
        'gaze': 0.18,
        'tab_switch': 0.20
    }
    
    # ============ Server Settings ============
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    websocket_timeout: int = 60
    max_connections: int = 10
    
    # ============ Paths ============
    @staticmethod
    def ensure_directories():
        """Create necessary directories if they don't exist"""
        dirs = [
            Config.evidence_dir,
            Config.screenshot_dir,
            Config.video_dir,
            Config.log_dir
        ]
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)

# Initialize directories on import
Config.ensure_directories()