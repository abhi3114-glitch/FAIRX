import threading

class FrameBuffer:
    def __init__(self):
        self.lock = threading.Lock()
        self.frame = None

FRAME_BUFFER = FrameBuffer()
