"""
FAIRX Suspicion Tracking Module
Fixed scoring system with time-based decay
"""
import time
from typing import Dict, List
from collections import deque
import logging

from .config import Config

logger = logging.getLogger(__name__)

class SuspicionTracker:
    """Track and calculate suspicion scores over time"""
    
    def __init__(self):
        self.events: deque = deque(maxlen=1000)
        self.current_score: float = 0.0
        self.weights: Dict[str, float] = Config.WEIGHTS
        self.decay_time: float = Config.suspicion_decay_time
        
    def add_event(self, event_type: str, confidence: float = 1.0):
        """
        Add a suspicious event
        
        Args:
            event_type: Type of event (device, gaze, multi_face, etc.)
            confidence: Confidence level (0.0 - 1.0)
        """
        timestamp = time.time()
        weight = self.weights.get(event_type, 0.2)
        
        event = {
            'type': event_type,
            'timestamp': timestamp,
            'confidence': confidence,
            'weight': weight,
            'score': weight * confidence
        }
        
        self.events.append(event)
        self._update_score()
        
        logger.debug(f"Event added: {event_type} (confidence: {confidence:.2f}, score: {event['score']:.2f})")
    
    def add(self, event_dict: dict):
        """
        Alias for add_event to support legacy code patterns
        
        Args:
            event_dict: Dictionary with 'type' and 'confidence' keys
        """
        event_type = event_dict.get('type', 'unknown')
        confidence = event_dict.get('confidence', 0.5)
        self.add_event(event_type, confidence)
    
    def _update_score(self):
        """Calculate current suspicion score with time decay"""
        current_time = time.time()
        total_score = 0.0
        active_events = 0
        
        for event in self.events:
            age = current_time - event['timestamp']
            
            # Apply exponential decay
            if age < self.decay_time:
                decay_factor = 1.0 - (age / self.decay_time)
                decayed_score = event['score'] * decay_factor
                total_score += decayed_score
                active_events += 1
        
        # Normalize score to 0-1 range
        # Use sigmoid-like function to prevent scores from growing too large
        self.current_score = min(1.0, total_score)
        
        if active_events > 0:
            logger.debug(f"Score updated: {self.current_score:.3f} (from {active_events} active events)")
    
    def get_score(self) -> float:
        """
        Get current suspicion score
        
        Returns:
            Float between 0.0 and 1.0
        """
        self._update_score()
        return self.current_score
    
    def get_alert_level(self) -> str:
        """
        Get alert level based on current score
        
        Returns:
            'normal', 'warning', or 'danger'
        """
        score = self.get_score()
        
        if score >= Config.alert_threshold_danger:
            return 'danger'
        elif score >= Config.alert_threshold_warning:
            return 'warning'
        else:
            return 'normal'
    
    def get_recent_events(self, seconds: int = 30) -> List[Dict]:
        """
        Get events from the last N seconds
        
        Args:
            seconds: Time window in seconds
            
        Returns:
            List of recent events
        """
        current_time = time.time()
        cutoff_time = current_time - seconds
        
        recent = [
            event for event in self.events 
            if event['timestamp'] >= cutoff_time
        ]
        
        return recent
    
    def get_event_summary(self) -> Dict:
        """
        Get summary of all events
        
        Returns:
            Dictionary with event type counts
        """
        summary = {}
        
        for event in self.events:
            event_type = event['type']
            summary[event_type] = summary.get(event_type, 0) + 1
        
        return summary
    
    def reset(self):
        """Reset all tracking data"""
        self.events.clear()
        self.current_score = 0.0
        logger.info("Suspicion tracker reset")
    
    def get_statistics(self) -> Dict:
        """
        Get detailed statistics
        
        Returns:
            Dictionary with various statistics
        """
        recent_events = self.get_recent_events(60)
        
        return {
            'current_score': self.current_score,
            'alert_level': self.get_alert_level(),
            'total_events': len(self.events),
            'recent_events_60s': len(recent_events),
            'event_summary': self.get_event_summary(),
            'highest_weight_event': max(
                (e for e in recent_events), 
                key=lambda x: x['score'],
                default=None
            )
        }

# Global instance for easy import
SCORE = SuspicionTracker()