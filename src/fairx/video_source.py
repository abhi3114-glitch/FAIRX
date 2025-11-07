"""
Unified video source handler - supports both camera and video file inputs
"""
import cv2
import threading
import time
from pathlib import Path
from .config import CFG

class VideoSource:
    """Unified video source that can switch between camera and video file"""
    
    def __init__(self, source=None):
        self.source = source or CFG.cam_index
        self.cap = None
        self.is_video_file = False
        self.video_loop = True  # Loop video files
        self.lock = threading.Lock()
        self._initialize_source()
    
    def _initialize_source(self):
        """Initialize video capture from source"""
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        
        # Check if source is a file path
        if isinstance(self.source, (str, Path)):
            source_path = Path(self.source)
            if source_path.exists() and source_path.is_file():
                self.is_video_file = True
                self.cap = cv2.VideoCapture(str(source_path))
                print(f"[VideoSource] Video file loaded: {source_path}")
            else:
                print(f"[VideoSource] File not found: {source_path}, falling back to camera")
                self.source = CFG.cam_index
                self.is_video_file = False
                self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
        else:
            # Camera index
            self.is_video_file = False
            self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
            w, h = CFG.camera_resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            print(f"[VideoSource] Camera initialized: index {self.source}")
        
        if not self.cap.isOpened():
            print(f"[VideoSource] FAILED to open source: {self.source}")
            return False
        
        return True
    
    def read(self):
        """Read frame from current source"""
        with self.lock:
            if self.cap is None or not self.cap.isOpened():
                return False, None
            
            ret, frame = self.cap.read()
            
            # Loop video file if enabled
            if not ret and self.is_video_file and self.video_loop:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
            
            return ret, frame
    
    def switch_source(self, new_source):
        """Switch to a new video source (camera index or file path)"""
        with self.lock:
            self.source = new_source
            return self._initialize_source()
    
    def release(self):
        """Release video capture"""
        with self.lock:
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
                self.cap = None
    
    def is_opened(self):
        """Check if source is opened"""
        with self.lock:
            return self.cap is not None and self.cap.isOpened()
    
    def get_fps(self):
        """Get FPS of current source"""
        if self.cap is not None and self.cap.isOpened():
            return self.cap.get(cv2.CAP_PROP_FPS)
        return 30.0
    
    def get_frame_count(self):
        """Get total frame count (for video files)"""
        if self.is_video_file and self.cap is not None:
            return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return -1