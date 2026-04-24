"""Voice output using TTS."""
import logging
import threading

logger = logging.getLogger(__name__)

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("pyttsx3 not installed. Voice output disabled.")


class VoiceOutput:
    """Handles text-to-speech output."""
    
    def __init__(self, config):
        self.config = config
        self.engine = None
        self.rate = config.voice.output.rate
        self.volume = config.voice.output.volume
        self._init_engine()
    
    def _init_engine(self):
        """Initialize the TTS engine."""
        if not TTS_AVAILABLE:
            return
        
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", self.rate)
            self.engine.setProperty("volume", self.volume)
            logger.info("TTS engine initialized")
        except Exception as e:
            logger.error(f"TTS engine init failed: {e}")
            self.engine = None
    
    def speak(self, text: str, blocking: bool = False):
        """Speak text aloud."""
        if not self.engine:
            logger.warning("TTS engine not available")
            return
        
        def _speak():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS speak failed: {e}")
        
        if blocking:
            _speak()
        else:
            thread = threading.Thread(target=_speak)
            thread.start()
    
    def stop(self):
        """Stop current speech."""
        if self.engine:
            self.engine.stop()
    
    def set_rate(self, rate: int):
        """Set speech rate."""
        self.rate = rate
        if self.engine:
            self.engine.setProperty("rate", rate)
    
    def set_volume(self, volume: float):
        """Set speech volume (0.0-1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        if self.engine:
            self.engine.setProperty("volume", self.volume)
    
    def get_voices(self) -> list[dict]:
        """Get available voices."""
        if not self.engine:
            return []
        
        voices = []
        for voice in self.engine.getProperty("voices"):
            voices.append({
                "id": voice.id,
                "name": voice.name,
                "languages": voice.languages,
                "gender": voice.gender
            })
        return voices
    
    def set_voice(self, voice_id: str):
        """Set the voice by ID."""
        if self.engine:
            self.engine.setProperty("voice", voice_id)
