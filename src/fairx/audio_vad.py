import threading, time, webrtcvad, sounddevice as sd
from .events import Event
from .suspicion import SCORE

class VADThread(threading.Thread):
    def __init__(self, aggressiveness=2, sample_rate=16000, frame_ms=20):
        super().__init__(daemon=True)
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * frame_ms / 1000)

    def run(self):
        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='int16') as stream:
            while True:
                audio, _ = stream.read(self.frame_size)
                if self.vad.is_speech(audio.tobytes(), self.sample_rate):
                    SCORE.add(Event.now("whisper", 0.6))
                time.sleep(0.005)
