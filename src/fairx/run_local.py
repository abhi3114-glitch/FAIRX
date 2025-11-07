"""
FAIRX Local Runner - Fixed
Run proctoring system locally without web server
"""
import cv2
import logging
import sys
from datetime import datetime

from .config import Config
from .vision import VisionDetector
from .suspicion import SuspicionTracker
from .events import EventLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("FAIRX AI Proctoring System - Local Mode")
    logger.info("=" * 60)
    
    # Initialize components
    try:
        vision_detector = VisionDetector()
        suspicion_tracker = SuspicionTracker()
        event_logger = EventLogger()
        logger.info("✓ All components initialized successfully")
    except Exception as e:
        logger.error(f"✗ Initialization failed: {e}")
        sys.exit(1)
    
    # Initialize camera
    logger.info(f"Opening camera {Config.cam_index}...")
    cap = cv2.VideoCapture(Config.cam_index)
    
    if not cap.isOpened():
        logger.error(f"✗ Cannot open camera {Config.cam_index}")
        logger.info("Try changing cam_index in config.py")
        sys.exit(1)
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.camera_resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.camera_resolution[1])
    cap.set(cv2.CAP_PROP_FPS, Config.fps)
    
    logger.info(f"✓ Camera opened: {Config.camera_resolution[0]}x{Config.camera_resolution[1]} @ {Config.fps}fps")
    logger.info("\nPress 'q' to quit, 'r' to reset score, 's' for statistics\n")
    
    frame_count = 0
    start_time = datetime.now()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to read frame")
                continue
            
            frame_count += 1
            
            # Detect objects
            detections, annotated_frame = vision_detector.detect_objects(frame)
            
            # Process detections
            for det in detections:
                suspicion_tracker.add_event(
                    det['type'], 
                    det.get('confidence', 0.5)
                )
                
                event_logger.log_event(
                    event_type=det['type'],
                    details={
                        'object': det.get('object', 'unknown'),
                        'confidence': det.get('confidence', 0.0),
                        'bbox': det.get('bbox', [])
                    },
                    severity='warning' if det.get('confidence', 0) > 0.6 else 'info'
                )
            
            # Get current score and alert level
            score = suspicion_tracker.get_score()
            alert_level = suspicion_tracker.get_alert_level()
            
            # Draw UI elements
            annotated_frame = draw_ui(annotated_frame, score, alert_level, frame_count, start_time)
            
            # Display frame
            cv2.imshow('FAIRX - AI Proctoring', annotated_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                logger.info("Quit requested by user")
                break
            elif key == ord('r'):
                suspicion_tracker.reset()
                logger.info("Score reset")
            elif key == ord('s'):
                stats = suspicion_tracker.get_statistics()
                logger.info(f"\n=== Statistics ===\n{stats}")
    
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
    
    except Exception as e:
        logger.error(f"Error during execution: {e}")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Export session
        try:
            export_path = event_logger.export_session()
            logger.info(f"Session exported to: {export_path}")
        except Exception as e:
            logger.error(f"Failed to export session: {e}")
        
        # Print summary
        summary = event_logger.get_session_summary()
        logger.info("\n" + "=" * 60)
        logger.info("SESSION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Events: {summary['total_events']}")
        logger.info(f"Severity: {summary['severity_counts']}")
        logger.info(f"Event Types: {summary['event_counts']}")
        logger.info("=" * 60)

def draw_ui(frame, score, alert_level, frame_count, start_time):
    """Draw UI elements on frame"""
    height, width = frame.shape[:2]
    
    # Calculate FPS
    elapsed = (datetime.now() - start_time).total_seconds()
    fps = frame_count / elapsed if elapsed > 0 else 0
    
    # Determine colors based on alert level
    if alert_level == 'danger':
        border_color = (0, 0, 255)  # Red
        text_color = (0, 0, 255)
        status_text = "DANGER"
    elif alert_level == 'warning':
        border_color = (0, 165, 255)  # Orange
        text_color = (0, 165, 255)
        status_text = "WARNING"
    else:
        border_color = (0, 255, 0)  # Green
        text_color = (0, 255, 0)
        status_text = "NORMAL"
    
    # Draw colored border
    thickness = 8
    cv2.rectangle(frame, (0, 0), (width, height), border_color, thickness)
    
    # Draw status bar at top
    bar_height = 60
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (width, bar_height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Draw status text
    cv2.putText(frame, f"Status: {status_text}", (20, 35), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
    
    cv2.putText(frame, f"Score: {score:.2f}", (width - 250, 35), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Draw info at bottom
    info_y = height - 20
    cv2.putText(frame, f"FPS: {fps:.1f}", (20, info_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    cv2.putText(frame, f"Frames: {frame_count}", (150, info_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    cv2.putText(frame, "Press 'q' to quit | 'r' to reset | 's' for stats", 
                (width - 500, info_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return frame

if __name__ == "__main__":
    main()