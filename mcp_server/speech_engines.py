"""
Speech recognition engines for voice commands
Supports ElevenLabs, Google Speech Recognition, and Whisper
"""

import os
import json
import asyncio
import logging
import tempfile
import time
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from enum import Enum

import numpy as np
import speech_recognition as sr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class RecognitionBackend(Enum):
    """Available speech recognition backends"""
    ELEVENLABS = "elevenlabs"
    GOOGLE = "google"
    WHISPER = "whisper"
    OPENAI_REALTIME = "openai"

@dataclass
class RecognitionResult:
    """Result from speech recognition"""
    text: str
    confidence: float
    backend: RecognitionBackend
    processing_time: float
    metadata: Dict[str, Any] = None

class SpeechEngine:
    """Base class for speech recognition engines"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Configure recognizer settings
        self.recognizer.energy_threshold = int(os.getenv('VOICE_ENERGY_THRESHOLD', 4000))
        self.recognizer.pause_threshold = float(os.getenv('VOICE_PAUSE_THRESHOLD', 0.8))
        self.recognizer.dynamic_energy_threshold = True
        
    def calibrate_microphone(self, duration: float = 2.0):
        """Calibrate microphone for ambient noise"""
        logger.info(f"Calibrating microphone for {duration}s...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
        logger.info(f"Energy threshold set to: {self.recognizer.energy_threshold}")
    
    async def recognize(self, audio_data) -> RecognitionResult:
        """Recognize speech from audio data - to be implemented by subclasses"""
        raise NotImplementedError

class ElevenLabsEngine(SpeechEngine):
    """ElevenLabs real-time speech recognition"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
        # Import ElevenLabs SDK
        try:
            from elevenlabs import ElevenLabs
            from elevenlabs.conversational_ai import ConversationalAI
            self.client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
            self.available = True
        except ImportError:
            logger.error("ElevenLabs SDK not available. Install with: pip install elevenlabs")
            self.available = False
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs client: {e}")
            self.available = False
            self.client = None
    
    async def recognize(self, audio_data) -> RecognitionResult:
        """Recognize speech using ElevenLabs Conversational AI"""
        if not self.available:
            raise Exception("ElevenLabs not available")
        
        start_time = time.time()
        
        try:
            # Convert audio to required format
            audio_bytes = self._convert_audio_format(audio_data)
            
            # Use ElevenLabs speech-to-text
            # Note: This uses the conversational AI endpoint for speech recognition
            response = await self._elevenlabs_stt(audio_bytes)
            
            processing_time = time.time() - start_time
            
            return RecognitionResult(
                text=response.get('transcript', ''),
                confidence=response.get('confidence', 0.95),  # ElevenLabs typically high confidence
                backend=RecognitionBackend.ELEVENLABS,
                processing_time=processing_time,
                metadata=response
            )
            
        except Exception as e:
            logger.error(f"ElevenLabs recognition failed: {e}")
            raise
    
    def _convert_audio_format(self, audio_data) -> bytes:
        """Convert audio data to format expected by ElevenLabs"""
        # ElevenLabs expects 16kHz, 16-bit, mono PCM
        if hasattr(audio_data, 'get_wav_data'):
            return audio_data.get_wav_data()
        return audio_data
    
    async def _elevenlabs_stt(self, audio_bytes: bytes) -> Dict[str, Any]:
        """Perform speech-to-text with ElevenLabs API"""
        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            # Use ElevenLabs transcription
            # Note: Adjust this based on the actual ElevenLabs Python SDK API
            # This is a placeholder - will need to be updated with actual API calls
            
            # For now, using a simulated response structure
            # TODO: Replace with actual ElevenLabs API call
            response = {
                'transcript': 'ElevenLabs transcription placeholder',
                'confidence': 0.95,
                'duration': 0.0
            }
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            return response
            
        except Exception as e:
            logger.error(f"ElevenLabs API error: {e}")
            raise

class GoogleEngine(SpeechEngine):
    """Google Speech Recognition (free tier)"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.available = True  # Google is available through speech_recognition package
    
    async def recognize(self, audio_data) -> RecognitionResult:
        """Recognize speech using Google Speech Recognition"""
        start_time = time.time()
        
        try:
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio_data)
            processing_time = time.time() - start_time
            
            return RecognitionResult(
                text=text,
                confidence=0.90,  # Google doesn't provide confidence scores
                backend=RecognitionBackend.GOOGLE,
                processing_time=processing_time,
                metadata={'service': 'google_speech_recognition'}
            )
            
        except sr.UnknownValueError:
            raise Exception("Could not understand audio")
        except sr.RequestError as e:
            raise Exception(f"Google API error: {e}")

class WhisperEngine(SpeechEngine):
    """Local Whisper speech recognition"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
        # Check if Whisper is available
        try:
            import whisper
            self.model_name = config.get('model_size', 'base')
            self.model = whisper.load_model(self.model_name)
            self.available = True
        except ImportError:
            logger.error("Whisper not available. Install with: pip install openai-whisper")
            self.available = False
            self.model = None
    
    async def recognize(self, audio_data) -> RecognitionResult:
        """Recognize speech using local Whisper model"""
        if not self.available:
            raise Exception("Whisper not available")
        
        start_time = time.time()
        
        try:
            # Use Whisper through speech_recognition
            text = self.recognizer.recognize_whisper(audio_data, model=self.model_name)
            processing_time = time.time() - start_time
            
            return RecognitionResult(
                text=text,
                confidence=0.85,  # Whisper typically good accuracy
                backend=RecognitionBackend.WHISPER,
                processing_time=processing_time,
                metadata={'model': self.model_name}
            )
            
        except Exception as e:
            logger.error(f"Whisper recognition failed: {e}")
            raise

class MultiEngine:
    """Multi-backend speech recognition with fallback"""
    
    def __init__(self):
        # Initialize engines based on availability and config
        self.engines = {}
        
        # Primary engine (ElevenLabs)
        if os.getenv('ELEVENLABS_API_KEY'):
            self.engines[RecognitionBackend.ELEVENLABS] = ElevenLabsEngine()
        
        # Fallback engines
        self.engines[RecognitionBackend.GOOGLE] = GoogleEngine()
        self.engines[RecognitionBackend.WHISPER] = WhisperEngine()
        
        # Remove unavailable engines
        self.engines = {k: v for k, v in self.engines.items() if v.available}
        
        # Set primary and fallback based on config
        primary_backend = os.getenv('VOICE_BACKEND', 'elevenlabs').lower()
        fallback_backend = os.getenv('VOICE_FALLBACK', 'google').lower()
        
        self.primary = RecognitionBackend(primary_backend) if primary_backend in [e.value for e in RecognitionBackend] else None
        self.fallback = RecognitionBackend(fallback_backend) if fallback_backend in [e.value for e in RecognitionBackend] else None
        
        logger.info(f"Available engines: {list(self.engines.keys())}")
        logger.info(f"Primary: {self.primary}, Fallback: {self.fallback}")
    
    def get_microphone(self) -> sr.Microphone:
        """Get configured microphone"""
        mic_index = os.getenv('VOICE_MIC_INDEX')
        if mic_index and mic_index.isdigit():
            return sr.Microphone(device_index=int(mic_index))
        return sr.Microphone()
    
    def calibrate_microphone(self, duration: float = 2.0):
        """Calibrate microphone using first available engine"""
        if self.engines:
            first_engine = next(iter(self.engines.values()))
            first_engine.calibrate_microphone(duration)
    
    async def recognize_with_fallback(self, audio_data) -> RecognitionResult:
        """Try recognition with primary engine, fallback on failure"""
        
        # Try primary engine first
        if self.primary and self.primary in self.engines:
            try:
                result = await self.engines[self.primary].recognize(audio_data)
                logger.debug(f"Primary engine {self.primary} succeeded")
                return result
            except Exception as e:
                logger.warning(f"Primary engine {self.primary} failed: {e}")
        
        # Try fallback engine
        if self.fallback and self.fallback in self.engines:
            try:
                result = await self.engines[self.fallback].recognize(audio_data)
                logger.debug(f"Fallback engine {self.fallback} succeeded")
                return result
            except Exception as e:
                logger.warning(f"Fallback engine {self.fallback} failed: {e}")
        
        # Try any remaining engines
        for backend, engine in self.engines.items():
            if backend not in [self.primary, self.fallback]:
                try:
                    result = await engine.recognize(audio_data)
                    logger.debug(f"Secondary engine {backend} succeeded")
                    return result
                except Exception as e:
                    logger.warning(f"Secondary engine {backend} failed: {e}")
        
        raise Exception("All recognition engines failed")
    
    def list_available_microphones(self) -> List[Dict[str, Any]]:
        """List available microphones"""
        mics = []
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            mics.append({
                'index': index,
                'name': name,
                'default': index == sr.Microphone().device_index
            })
        return mics
    
    def test_microphone(self, duration: float = 3.0) -> Dict[str, Any]:
        """Test microphone setup"""
        try:
            microphone = self.get_microphone()
            recognizer = sr.Recognizer()
            
            with microphone as source:
                # Test ambient noise level
                recognizer.adjust_for_ambient_noise(source, duration=1)
                energy_threshold = recognizer.energy_threshold
                
                # Try to capture some audio
                logger.info(f"Testing microphone for {duration}s...")
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=duration)
                
                return {
                    'success': True,
                    'microphone_index': getattr(microphone, 'device_index', 'default'),
                    'energy_threshold': energy_threshold,
                    'audio_captured': True,
                    'audio_duration': duration
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'microphone_index': 'unknown'
            }