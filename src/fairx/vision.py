"""
FAIRX Vision Module - Object Detection
Fixed and optimized YOLO-based detection
"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Dict, Optional
import logging

from .config import Config

logger = logging.getLogger(__name__)

class VisionDetector:
    """Enhanced object detection for proctoring"""
    
    def __init__(self):
        try:
            self.model = YOLO(Config.yolo_model)
            self.suspicious_objects = Config.suspicious_objects
            logger.info(f"YOLO model loaded: {Config.yolo_model}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None
    
    def detect_objects(self, frame: np.ndarray) -> Tuple[List[Dict], np.ndarray]:
        """
        Detect suspicious objects in frame
        
        Args:
            frame: Input image frame
            
        Returns:
            Tuple of (detections list, annotated frame)
        """
        if self.model is None:
            return [], frame
        
        detections = []
        annotated_frame = frame.copy()
        
        try:
            # Run YOLO inference
            results = self.model(
                frame, 
                conf=Config.yolo_conf_threshold,
                iou=Config.yolo_iou_threshold,
                verbose=False
            )
            
            # Process detections
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Extract box data
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id].lower()
                    
                    # Calculate box area
                    box_area = (x2 - x1) * (y2 - y1)
                    
                    # Check if object is suspicious and meets size threshold
                    if class_name in self.suspicious_objects and box_area >= Config.yolo_min_box_area:
                        detection = {
                            'type': 'device',
                            'object': class_name,
                            'confidence': confidence,
                            'bbox': (x1, y1, x2, y2),
                            'area': box_area
                        }
                        detections.append(detection)
                        
                        # Draw bounding box
                        color = self._get_alert_color(confidence)
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                        
                        # Draw label
                        label = f"{class_name}: {confidence:.2f}"
                        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                        cv2.rectangle(
                            annotated_frame, 
                            (x1, y1 - label_size[1] - 10), 
                            (x1 + label_size[0], y1), 
                            color, 
                            -1
                        )
                        cv2.putText(
                            annotated_frame, 
                            label, 
                            (x1, y1 - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.5, 
                            (255, 255, 255), 
                            1
                        )
            
            return detections, annotated_frame
            
        except Exception as e:
            logger.error(f"Object detection error: {e}")
            return [], frame
    
    def _get_alert_color(self, confidence: float) -> Tuple[int, int, int]:
        """
        Get color based on confidence level
        
        Args:
            confidence: Detection confidence
            
        Returns:
            BGR color tuple
        """
        if confidence >= Config.alert_threshold_danger:
            return (0, 0, 255)  # Red
        elif confidence >= Config.alert_threshold_warning:
            return (0, 165, 255)  # Orange
        else:
            return (0, 255, 0)  # Green
    
    def get_detection_summary(self, detections: List[Dict]) -> str:
        """
        Create human-readable detection summary
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            Summary string
        """
        if not detections:
            return "No suspicious objects detected"
        
        object_counts = {}
        for det in detections:
            obj = det['object']
            object_counts[obj] = object_counts.get(obj, 0) + 1
        
        summary_parts = [f"{count}x {obj}" for obj, count in object_counts.items()]
        return "Detected: " + ", ".join(summary_parts)