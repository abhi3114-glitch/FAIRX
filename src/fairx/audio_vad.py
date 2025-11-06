import threading, time, webrtcvad, sounddevice as sd, numpy as np, queue
from collections import deque
from .events import Event
from .suspicion import SCORE
from .config import CFG
from .evidence import EvidenceRecorder

class VADThread(threading.Thread):
    def __init__(self, aggressiveness=2, sample_rate=16000, frame_ms=20):
        super().__init__(daemon=True)

        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.frame_size = int(sample_rate * frame_ms / 1000)
        
        # For smoothing speech detection
        self.history = deque(maxlen=25)  # last ~500ms
        
        # to avoid spam triggers
        self.last_event = 0
        self.cooldown = CFG.event_cooldown.get("whisper", 2.0)

        # evidence recorder (audio)
        self.audio_buf = deque(maxlen=int(sample_rate * (CFG.pre_event_sec + CFG.post_event_sec)))
        self.event_in_progress = False
        self.post_frames = 0
        self.save_lock = threading.Lock()

    def _save_audio_clip(self):
        """Save last few seconds of mic as WAV evidence"""
        ts = int(time.time())
        samples = np.array(self.audio_buf, dtype=np.int16)

        if len(samples) < self.sample_rate:
            return

        fname = f"whisper_{ts}.wav"
        path = f"{CFG.evidence_dir}/{fname}"

        import soundfile as sf
        sf.write(path, samples, self.sample_rate)
        print(f"[AUDIO] 🎤 Evidence saved: {path}")

        # also log event clip
        from .evidence import EvidenceRecorder
        # we already recorded via video buffer — audio optional

    def run(self):
        print("[VAD] 🎤 Voice monitor ON")

        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='int16') as stream:
                while True:
                    audio, _ = stream.read(self.frame_size)
                    audio_b = audio.tobytes()

                    # store audio always (for evidence)
                    self.audio_buf.extend(audio.flatten())

                    is_speech = self.vad.is_speech(audio_b, self.sample_rate)
                    self.history.append(1 if is_speech else 0)

                    # Speech detected if >30% frames of last 500ms are voice
                    speech_ratio = sum(self.history) / len(self.history)

                    now = time.time()

                    if speech_ratio > 0.30:
                        # Mark event start
                        if now - self.last_event > self.cooldown:
                            SCORE.add(Event.now("whisper", 0.7))
                            print(f"[VAD] ⚠️ Whisper detected (ratio={speech_ratio:.2f})")

                            self.last_event = now
                            self.event_in_progress = True
                            self.post_frames = 0

                    # if event triggered, collect post frames
                    if self.event_in_progress:
                        self.post_frames += 1
                        # convert post frames = frames at sample_rate
                        if self.post_frames > self.sample_rate * CFG.post_event_sec:
                            with self.save_lock:
                                self._save_audio_clip()
                            self.event_in_progress = False

                    time.sleep(0.002)

        except Exception as e:
            print(f"[VAD] ❌ Mic error: {e}")
