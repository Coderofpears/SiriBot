"""Voice input using Whisper."""
import logging
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper not installed. Voice input disabled.")


class VoiceInput:
    """Handles voice input using Whisper."""
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.energy_threshold = config.voice.input.energy_threshold
        self.pause_threshold = config.voice.input.pause_threshold
    
    def load_model(self, model_name: Optional[str] = None):
        """Load the Whisper model."""
        if not WHISPER_AVAILABLE:
            raise RuntimeError("Whisper not installed")
        
        model = model_name or self.config.voice.input.model
        logger.info(f"Loading Whisper model: {model}")
        self.model = whisper.load_model(model)
        logger.info("Whisper model loaded")
    
    async def transcribe(self, audio_data: np.ndarray) -> str:
        """Transcribe audio to text."""
        if not self.model:
            self.load_model()
        
        try:
            result = self.model.transcribe(audio_data, language="en")
            text = result["text"].strip()
            logger.info(f"Transcribed: {text}")
            return text
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
    
    async def transcribe_file(self, file_path: str) -> str:
        """Transcribe an audio file."""
        if not self.model:
            self.load_model()
        
        try:
            result = self.model.transcribe(file_path, language="en")
            text = result["text"].strip()
            logger.info(f"Transcribed file: {text}")
            return text
        except Exception as e:
            logger.error(f"File transcription failed: {e}")
            return ""


class Microphone:
    """Simple microphone input handler."""
    
    def __init__(self, energy_threshold: int = 300, pause_threshold: float = 2.0):
        self.energy_threshold = energy_threshold
        self.pause_threshold = pause_threshold
        self._stream = None
    
    def start_listening(self):
        """Start listening for voice input."""
        try:
            import pyaudio
            self._stream = pyaudio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024
            )
            logger.info("Microphone listening started")
        except ImportError:
            logger.warning("PyAudio not installed")
        except Exception as e:
            logger.error(f"Microphone start failed: {e}")
    
    def stop_listening(self):
        """Stop listening."""
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
    
    def read_audio(self) -> bytes:
        """Read audio data."""
        if self._stream:
            return self._stream.read(1024)
        return b""
