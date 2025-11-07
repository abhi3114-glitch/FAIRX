"""
FAIRX Package Initialization
Place this in: src/__init__.py and src/fairx/__init__.py
"""

# src/__init__.py
"""FAIRX - AI Exam Proctoring System"""
__version__ = "2.1.0"

# src/fairx/__init__.py
"""
FAIRX Core Module
Advanced AI-powered exam proctoring with comprehensive cheating detection
"""

from .config import Config
from .vision import VisionDetector
from .suspicion import SuspicionTracker
from .events import EventLogger

__all__ = [
    'Config',
    'VisionDetector', 
    'SuspicionTracker',
    'EventLogger'
]

__version__ = "2.1.0"
__author__ = "FAIRX Team"
__description__ = "AI-Powered Exam Proctoring System"