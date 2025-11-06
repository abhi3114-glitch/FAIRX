"""
NEW MODULE: Movement Detection
Detects excessive body movements and position changes
"""
import cv2, threading, time
import numpy as np
from collections import deque
from .events import Event
from .suspicion import SCORE
from .config import CFG
from .frame_buffer import FRAME_BUFFER
from .evidence import EvidenceRecorder

EBUF = EvidenceRecorder(fps=15, seconds=8, enabled=CFG.ENABLE_EVIDENCE)

class MovementDetectorThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        
        self.prev_frame = None
        self.movement_history = deque(maxlen=30)  # Track last 30 frames
        self.last_event_time = 0
        self.cooldown = CFG.event_cooldown.get("excessive_movement", 2.5)
        
        # Background subtractor for motion detection
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, 
            varThreshold=16, 
            detectShadows=False
        )
        
        print("[Movement] ✅ Movement detector initialized")

    def _calculate_movement(self, frame):
        """Calculate amount of movement in frame"""
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(frame)
        
        # Calculate percentage of frame with movement
        movement_pixels = np.sum(fg_mask > 0)
        total_pixels = fg_mask.shape[0] * fg_mask.shape[1]
        movement_ratio = movement_pixels / total_pixels
        
        return movement_ratio, fg_mask

    def _detect_position_change(self, frame):
        """Detect significant position changes using frame differencing"""
        if self.prev_frame is None:
            self.prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return 0.0
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate frame difference
        frame_diff = cv2.absdiff(self.prev_frame, gray)
        _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
        
        # Calculate movement score
        movement_score = np.sum(thresh) / (thresh.shape[0] * thresh.shape[1] * 255)
        
        self.prev_frame = gray
        return movement_score

    def run(self):
        print("[Movement] ▶️ Movement detection running...")
        
        while True:
            # Read latest frame
            with FRAME_BUFFER.lock:
                frame = FRAME_BUFFER.frame.copy() if FRAME_BUFFER.frame is not None else None
            
            if frame is None:
                time.sleep(0.01)
                continue
            
            EBUF.push(frame)
            
            # Calculate movement
            movement_ratio, fg_mask = self._calculate_movement(frame)
            position_change = self._detect_position_change(frame)
            
            # Store in history
            self.movement_history.append(movement_ratio)
            
            # Calculate average movement over time window
            if len(self.movement_history) >= 15:  # ~0.5 seconds
                avg_movement = sum(self.movement_history) / len(self.movement_history)
                
                now = time.time()
                
                # Detect excessive movement
                if avg_movement > 0.15 or position_change > 0.20:  # Thresholds
                    if now - self.last_event_time > self.cooldown:
                        intensity = min(1.0, (avg_movement + position_change) / 0.5)
                        
                        SCORE.add(Event.now("excessive_movement", intensity, 
                                          movement=avg_movement, 
                                          position_change=position_change))
                        
                        print(f"[Movement] ⚠️ Excessive movement detected: {avg_movement:.3f}")
                        EBUF.save_async("excessive_movement", intensity)
                        self.last_event_time = now
            
            time.sleep(0.03)  # ~30 FPS