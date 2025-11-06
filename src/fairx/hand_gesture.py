"""
NEW MODULE: Hand Gesture Detection
Detects suspicious hand movements, gestures, paper passing, and hand signals
"""
import cv2, mediapipe as mp, threading, time
import numpy as np
from collections import deque
from .events import Event
from .suspicion import SCORE
from .config import CFG
from .frame_buffer import FRAME_BUFFER
from .evidence import EvidenceRecorder

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

EBUF = EvidenceRecorder(fps=15, seconds=8, enabled=CFG.ENABLE_EVIDENCE)

class HandGestureThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=CFG.hand_confidence_threshold,
            min_tracking_confidence=0.5
        )
        
        # Track hand positions over time
        self.hand_history = deque(maxlen=30)  # 30 frames ~ 1 second
        self.last_event_time = 0
        self.cooldown = CFG.event_cooldown.get("hand_gesture", 2.0)
        
        # Gesture patterns
        self.gesture_buffer = deque(maxlen=10)
        
        print("[HandGesture] ✅ Hand detection initialized")

    def _detect_paper_passing(self, hand_landmarks_list):
        """Detect if hands are moving in a passing motion"""
        if len(hand_landmarks_list) < 2:
            return False, 0.0
        
        # Get positions of both hands
        hand1 = hand_landmarks_list[0].landmark[mp_hands.HandLandmark.WRIST]
        hand2 = hand_landmarks_list[1].landmark[mp_hands.HandLandmark.WRIST]
        
        # Calculate distance between hands
        distance = np.sqrt((hand1.x - hand2.x)**2 + (hand1.y - hand2.y)**2)
        
        # If hands are close together (potential passing)
        if distance < 0.15:  # normalized coordinates
            return True, 0.75
        
        return False, 0.0

    def _detect_suspicious_gesture(self, hand_landmarks):
        """Detect pointing, signaling, or other suspicious gestures"""
        # Get finger tip positions
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        
        # Pointing gesture (index extended, others closed)
        index_extended = index_tip.y < hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y
        middle_closed = middle_tip.y > hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
        
        if index_extended and middle_closed:
            return True, "pointing", 0.65
        
        # OK sign or other signals (thumb and index close)
        thumb_index_dist = np.sqrt((index_tip.x - thumb_tip.x)**2 + (index_tip.y - thumb_tip.y)**2)
        if thumb_index_dist < 0.05:
            return True, "signal", 0.70
        
        return False, None, 0.0

    def _calculate_hand_movement(self, current_pos):
        """Calculate total hand movement over time window"""
        if len(self.hand_history) < 5:
            return 0.0
        
        movements = []
        for i in range(1, len(self.hand_history)):
            prev = self.hand_history[i-1]
            curr = self.hand_history[i]
            
            if prev and curr:
                dist = np.sqrt((curr[0] - prev[0])**2 + (curr[1] - prev[1])**2)
                movements.append(dist)
        
        return sum(movements) if movements else 0.0

    def run(self):
        print("[HandGesture] ▶️ Hand gesture detection running...")
        
        while True:
            # Read latest frame
            with FRAME_BUFFER.lock:
                frame = FRAME_BUFFER.frame.copy() if FRAME_BUFFER.frame is not None else None
            
            if frame is None:
                time.sleep(0.01)
                continue
            
            EBUF.push(frame)
            
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)
            
            now = time.time()
            
            if results.multi_hand_landmarks:
                num_hands = len(results.multi_hand_landmarks)
                
                # Track hand positions
                for hand_landmarks in results.multi_hand_landmarks:
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    hand_pos = (wrist.x * w, wrist.y * h)
                    self.hand_history.append(hand_pos)
                    
                    # Check for suspicious gestures
                    is_suspicious, gesture_type, conf = self._detect_suspicious_gesture(hand_landmarks)
                    if is_suspicious and now - self.last_event_time > self.cooldown:
                        SCORE.add(Event.now("hand_gesture", conf, gesture=gesture_type))
                        print(f"[HandGesture] ⚠️ Suspicious gesture: {gesture_type}")
                        EBUF.save_async(f"gesture_{gesture_type}", conf)
                        self.last_event_time = now
                
                # Check for paper passing (2 hands)
                if num_hands >= 2:
                    is_passing, conf = self._detect_paper_passing(results.multi_hand_landmarks)
                    if is_passing and now - self.last_event_time > CFG.event_cooldown.get("paper_passing", 3.0):
                        SCORE.add(Event.now("paper_passing", conf))
                        print("[HandGesture] 🚨 Paper/chit passing detected!")
                        EBUF.save_async("paper_passing", conf)
                        self.last_event_time = now
                
                # Check for excessive hand movement
                if len(self.hand_history) >= 10:
                    movement = self._calculate_hand_movement(self.hand_history[-1])
                    if movement > CFG.hand_movement_threshold:
                        if now - self.last_event_time > self.cooldown:
                            intensity = min(1.0, movement / (CFG.hand_movement_threshold * 2))
                            SCORE.add(Event.now("hand_gesture", intensity, reason="excessive_movement"))
                            print(f"[HandGesture] ⚠️ Excessive hand movement: {movement:.1f}px")
                            EBUF.save_async("hand_movement", intensity)
                            self.last_event_time = now
            
            time.sleep(0.03)  # ~30 FPS