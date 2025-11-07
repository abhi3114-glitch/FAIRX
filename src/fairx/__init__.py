"""
FAIRX Core Module
Advanced AI-powered exam proctoring with comprehensive cheating detection
Optimized for RTX 3050 + 16GB RAM + R7 6800H
"""

from .config import Config, CFG
from .vision import VisionDetector
from .suspicion import SuspicionTracker, SCORE
from .events import EventLogger
from .evidence import EvidenceRecorder
from .frame_buffer import FrameBuffer, FRAME_BUFFER

__all__ = [
    'Config',
    'CFG',
    'VisionDetector', 
    'SuspicionTracker',
    'SCORE',
    'EventLogger',
    'EvidenceRecorder',
    'FrameBuffer',
    'FRAME_BUFFER'
]

__version__ = "2.2.0"
__author__ = "FAIRX Team"
__description__ = "AI-Powered Exam Proctoring System - Optimized for RTX 3050"