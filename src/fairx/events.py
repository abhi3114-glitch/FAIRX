"""
FAIRX Event Logging Module
Fixed event logging with file persistence
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import os

from .config import Config

logger = logging.getLogger(__name__)

class EventLogger:
    """Log and persist proctoring events"""
    
    def __init__(self):
        self.log_file = os.path.join(Config.log_dir, "events.jsonl")
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.events: List[Dict] = []
        
        # Ensure log directory exists
        os.makedirs(Config.log_dir, exist_ok=True)
        
        logger.info(f"Event logger initialized. Session: {self.session_id}")
    
    def log_event(self, event_type: str, details: Dict, severity: str = "info"):
        """
        Log a proctoring event
        
        Args:
            event_type: Type of event (device, gaze, etc.)
            details: Event details dictionary
            severity: Event severity (info, warning, danger)
        """
        timestamp = datetime.now().isoformat()
        
        event = {
            'session_id': self.session_id,
            'timestamp': timestamp,
            'type': event_type,
            'severity': severity,
            'details': details
        }
        
        self.events.append(event)
        self._write_to_file(event)
        
        # Log to console based on severity
        log_message = f"Event: {event_type} | {json.dumps(details)}"
        if severity == "danger":
            logger.warning(log_message)
        elif severity == "warning":
            logger.info(log_message)
        else:
            logger.debug(log_message)
    
    def _write_to_file(self, event: Dict):
        """Write event to JSON Lines file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            logger.error(f"Failed to write event to file: {e}")
    
    def get_events(self, 
                   event_type: Optional[str] = None, 
                   severity: Optional[str] = None,
                   limit: int = 100) -> List[Dict]:
        """
        Retrieve logged events with filters
        
        Args:
            event_type: Filter by event type
            severity: Filter by severity
            limit: Maximum number of events to return
            
        Returns:
            List of matching events
        """
        filtered = self.events
        
        if event_type:
            filtered = [e for e in filtered if e['type'] == event_type]
        
        if severity:
            filtered = [e for e in filtered if e['severity'] == severity]
        
        return filtered[-limit:]
    
    def get_session_summary(self) -> Dict:
        """
        Get summary of current session
        
        Returns:
            Dictionary with session statistics
        """
        event_counts = {}
        severity_counts = {'info': 0, 'warning': 0, 'danger': 0}
        
        for event in self.events:
            event_type = event['type']
            severity = event['severity']
            
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'session_id': self.session_id,
            'total_events': len(self.events),
            'event_counts': event_counts,
            'severity_counts': severity_counts,
            'start_time': self.events[0]['timestamp'] if self.events else None,
            'end_time': self.events[-1]['timestamp'] if self.events else None
        }
    
    def export_session(self, filepath: Optional[str] = None) -> str:
        """
        Export session to JSON file
        
        Args:
            filepath: Optional custom filepath
            
        Returns:
            Path to exported file
        """
        if filepath is None:
            filepath = os.path.join(
                Config.log_dir, 
                f"session_{self.session_id}.json"
            )
        
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    'summary': self.get_session_summary(),
                    'events': self.events
                }, f, indent=2)
            
            logger.info(f"Session exported to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export session: {e}")
            raise
    
    def clear_events(self):
        """Clear all events from memory (not from file)"""
        self.events.clear()
        logger.info("Events cleared from memory")