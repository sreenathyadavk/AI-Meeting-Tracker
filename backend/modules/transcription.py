"""
Transcription module using OpenAI Whisper
Converts audio to text locally (no API costs)
100% Python virtual environment - uses Whisper's built-in audio loading
"""
import logging
import whisper
from pathlib import Path

logger = logging.getLogger(__name__)

# Initialize Whisper model (lazy loading)
_model = None

def get_whisper_model():
    """Get or initialize Whisper model"""
    global _model
    if _model is None:
        logger.info("Loading Whisper model (base)...")
        # Use 'base' model for speed, 'small' or 'medium' for better accuracy
        # Model will be downloaded to ~/.cache/whisper on first run
        _model = whisper.load_model("base")
        logger.info("Whisper model loaded successfully")
    return _model

async def transcribe_audio(file_path: str) -> str:
    """
    Transcribe full audio file to text using Whisper
    
    Args:
        file_path: Path to audio file (MP3, MP4, WAV, M4A)
        
    Returns:
        Full transcript as string
    """
    try:
        model = get_whisper_model()
        
        logger.info(f"Transcribing: {file_path}")
        
        # Use model.transcribe() directly - this processes the FULL audio file
        result = model.transcribe(
            file_path,
            language="en",  # Set to None for auto-detection
            fp16=False  # Use FP32 for CPU compatibility
        )
        
        # Extract full transcript
        full_transcript = result["text"].strip()
        
        # Log detected language
        detected_language = result.get("language", "en")
        logger.info(f"Detected language: {detected_language}")
        logger.info(f"Transcription complete. {len(full_transcript)} characters")
        
        return full_transcript
        
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        # If Whisper's audio loading fails, provide helpful error
        error_msg = str(e)
        if "ffmpeg" in error_msg.lower():
            raise Exception(
                "Audio file format requires ffmpeg. Please install ffmpeg on your system: "
                "Ubuntu/Debian: sudo apt-get install ffmpeg, "
                "macOS: brew install ffmpeg, "
                f"Original error: {error_msg}"
            )
        raise Exception(f"Failed to transcribe audio: {error_msg}")
