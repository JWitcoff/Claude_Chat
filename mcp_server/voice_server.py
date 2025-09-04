#!/usr/bin/env python3
"""
MCP Server for Claude Voice Commands
Provides real-time voice command capabilities for Claude Code through ElevenLabs integration
"""

import os
import sys
import json
import logging
import asyncio
import tempfile
import time
import builtins
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# Configure stderr-only logging for MCP compatibility
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# Safety net: make print default to stderr to avoid stdout contamination
_orig_print = builtins.print
def _safe_print(*args, **kwargs):
    kwargs.setdefault("file", sys.stderr)
    return _orig_print(*args, **kwargs)
builtins.print = _safe_print

# Add current directory to Python path for imports
VOICE_COMMANDS_PATH = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(VOICE_COMMANDS_PATH))

# Import MCP framework
try:
    from fastmcp import FastMCP
    MCP_AVAILABLE = True
    logging.info("[MCP] FastMCP imported successfully")
except ImportError as e:
    print(f"FastMCP not available: {e}. Install with: pip install fastmcp", file=sys.stderr)
    MCP_AVAILABLE = False

# Import speech recognition components
try:
    from mcp_server.speech_engines import MultiEngine, RecognitionResult
    from dotenv import load_dotenv
    import speech_recognition as sr
    SPEECH_COMPONENTS_AVAILABLE = True
    logging.info("[SPEECH] Speech components imported successfully")
except ImportError as e:
    print(f"Speech components not available: {e}", file=sys.stderr)
    SPEECH_COMPONENTS_AVAILABLE = False

# Load environment variables
if SPEECH_COMPONENTS_AVAILABLE:
    load_dotenv()

# Initialize FastMCP server
if MCP_AVAILABLE:
    mcp = FastMCP("Claude Voice Commands")
    logging.info("[MCP] FastMCP server initialized")

    # Global speech engine instance
    _speech_engine = None

    def get_speech_engine() -> MultiEngine:
        """Get or create the global speech engine instance"""
        global _speech_engine
        if _speech_engine is None:
            if not SPEECH_COMPONENTS_AVAILABLE:
                raise Exception("Speech components not available")
            _speech_engine = MultiEngine()
            logging.info(f"[SPEECH] Engine initialized with backends: {[e.value for e in _speech_engine.engines.keys()]}")
        return _speech_engine

    @mcp.tool()
    async def ping(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simple echo tool to confirm MCP JSON-RPC plumbing.
        Takes any JSON payload and returns it back with ok=True.
        """
        return {"ok": True, "echo": payload, "server": "Claude Voice Commands"}

    @mcp.tool()
    async def test_microphone(duration: float = 2.0) -> Dict[str, Any]:
        """
        Test microphone setup and audio capture
        
        Args:
            duration: Duration in seconds to test audio capture (default: 2.0)
        
        Returns:
            Dictionary containing:
            - success: Whether the test passed
            - microphone_index: Device index used
            - energy_threshold: Ambient noise threshold
            - audio_captured: Whether audio was successfully captured
            - error: Error message if test failed
        """
        try:
            engine = get_speech_engine()
            result = engine.test_microphone(duration=duration)
            
            logging.info(f"[MICROPHONE] Test result: {result.get('success', False)}")
            return result
            
        except Exception as e:
            error_msg = f"Microphone test failed: {str(e)}"
            logging.error(f"[MICROPHONE] {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "microphone_index": "unknown"
            }

    @mcp.tool()
    async def transcribe_once(duration: int = 5, backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Capture and transcribe a single voice command
        
        Args:
            duration: Maximum seconds to wait for speech (default: 5)
            backend: Specific backend to use: 'elevenlabs', 'google', 'whisper' (default: auto-fallback)
        
        Returns:
            Dictionary containing:
            - success: Whether transcription succeeded
            - text: Transcribed text
            - backend: Recognition backend used
            - confidence: Recognition confidence score
            - processing_time: Time taken in seconds
            - error: Error message if transcription failed
        """
        try:
            engine = get_speech_engine()
            
            logging.info(f"[TRANSCRIBE] Starting single transcription (duration: {duration}s, backend: {backend or 'auto'})")
            
            # Capture audio
            recognizer = sr.Recognizer()
            microphone = engine.get_microphone()
            
            with microphone as source:
                # Quick calibration
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                logging.info(f"[TRANSCRIBE] Listening for speech...")
                
                # Listen for audio with specified timeout
                audio = recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
            logging.info("[TRANSCRIBE] Audio captured, processing...")
            
            # Transcribe using specified backend or fallback system
            if backend:
                # Use specific backend
                from mcp_server.speech_engines import RecognitionBackend
                try:
                    backend_enum = RecognitionBackend(backend.lower())
                    if backend_enum in engine.engines:
                        result = await engine.engines[backend_enum].recognize(audio)
                    else:
                        raise Exception(f"Backend '{backend}' not available")
                except ValueError:
                    raise Exception(f"Invalid backend: {backend}. Available: {[e.value for e in engine.engines.keys()]}")
            else:
                # Use multi-engine fallback
                result = await engine.recognize_with_fallback(audio)
            
            response = {
                "success": True,
                "text": result.text,
                "backend": result.backend.value,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "timestamp": datetime.now().isoformat()
            }
            
            logging.info(f"[TRANSCRIBE] Success: '{result.text}' (backend: {result.backend.value}, {result.processing_time:.2f}s)")
            return response
            
        except sr.WaitTimeoutError:
            error_msg = "No speech detected within timeout period"
            logging.warning(f"[TRANSCRIBE] {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "text": "",
                "timeout": True
            }
        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            logging.error(f"[TRANSCRIBE] {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "text": ""
            }

    @mcp.tool()
    async def calibrate_audio(duration: float = 2.0) -> Dict[str, Any]:
        """
        Calibrate microphone for ambient noise levels
        
        Args:
            duration: Duration in seconds to sample ambient noise (default: 2.0)
        
        Returns:
            Dictionary containing:
            - success: Whether calibration succeeded
            - energy_threshold: New energy threshold value
            - duration: Calibration duration used
            - message: Status message
        """
        try:
            engine = get_speech_engine()
            
            logging.info(f"[CALIBRATE] Starting calibration for {duration}s")
            
            # Perform calibration
            engine.calibrate_microphone(duration=duration)
            
            # Get the updated threshold
            recognizer = sr.Recognizer()
            microphone = engine.get_microphone()
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.1)
                energy_threshold = recognizer.energy_threshold
            
            response = {
                "success": True,
                "energy_threshold": energy_threshold,
                "duration": duration,
                "message": f"Microphone calibrated successfully (threshold: {energy_threshold:.1f})"
            }
            
            logging.info(f"[CALIBRATE] Success: threshold={energy_threshold:.1f}")
            return response
            
        except Exception as e:
            error_msg = f"Calibration failed: {str(e)}"
            logging.error(f"[CALIBRATE] {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }

    @mcp.tool()
    async def list_audio_devices() -> Dict[str, Any]:
        """
        List available audio input devices
        
        Returns:
            Dictionary containing:
            - devices: List of available microphones with index and name
            - default_device: Index of default microphone
            - total_count: Total number of devices found
        """
        try:
            engine = get_speech_engine()
            devices = engine.list_available_microphones()
            
            default_device = None
            for device in devices:
                if device.get('default'):
                    default_device = device['index']
                    break
            
            response = {
                "devices": devices,
                "default_device": default_device,
                "total_count": len(devices)
            }
            
            logging.info(f"[DEVICES] Found {len(devices)} audio devices")
            return response
            
        except Exception as e:
            error_msg = f"Failed to list audio devices: {str(e)}"
            logging.error(f"[DEVICES] {error_msg}")
            return {
                "error": error_msg,
                "devices": [],
                "total_count": 0
            }

    @mcp.tool()
    async def get_engine_status() -> Dict[str, Any]:
        """
        Get status of speech recognition engines
        
        Returns:
            Dictionary containing:
            - available_engines: List of available recognition backends
            - primary_engine: Currently configured primary engine
            - fallback_engine: Currently configured fallback engine
            - elevenlabs_api_configured: Whether ElevenLabs API key is set
            - engine_details: Detailed information about each engine
        """
        try:
            engine = get_speech_engine()
            
            # Check API key status
            elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
            elevenlabs_configured = bool(elevenlabs_key and elevenlabs_key.strip())
            
            # Get engine details
            engine_details = {}
            for backend, eng in engine.engines.items():
                engine_details[backend.value] = {
                    "available": eng.available,
                    "type": eng.__class__.__name__
                }
            
            response = {
                "available_engines": [e.value for e in engine.engines.keys()],
                "primary_engine": engine.primary.value if engine.primary else None,
                "fallback_engine": engine.fallback.value if engine.fallback else None,
                "elevenlabs_api_configured": elevenlabs_configured,
                "engine_details": engine_details,
                "total_engines": len(engine.engines)
            }
            
            logging.info(f"[STATUS] Engines: {response['available_engines']}, Primary: {response['primary_engine']}")
            return response
            
        except Exception as e:
            error_msg = f"Failed to get engine status: {str(e)}"
            logging.error(f"[STATUS] {error_msg}")
            return {
                "error": error_msg,
                "available_engines": [],
                "total_engines": 0
            }

# Main entry point
if __name__ == "__main__":
    if not MCP_AVAILABLE:
        print("Cannot start server - FastMCP not available", file=sys.stderr)
        print("Install with: pip install fastmcp", file=sys.stderr)
        sys.exit(1)
    
    if not SPEECH_COMPONENTS_AVAILABLE:
        print("Cannot start server - Speech components not available", file=sys.stderr)
        print("Check dependencies in requirements.txt", file=sys.stderr)
        sys.exit(1)
    
    # Log server startup
    logging.info("[MCP] Starting Claude Voice Commands MCP Server...")
    logging.info(f"[CONFIG] Working directory: {VOICE_COMMANDS_PATH}")
    
    # Initialize speech engine to validate setup
    try:
        engine = get_speech_engine()
        logging.info(f"[INIT] Speech engine ready with {len(engine.engines)} backends")
    except Exception as e:
        logging.error(f"[INIT] Failed to initialize speech engine: {e}")
        print("Speech engine initialization failed. Check your configuration.", file=sys.stderr)
        sys.exit(1)
    
    # Run the MCP server
    try:
        mcp.run()
    except KeyboardInterrupt:
        logging.info("[MCP] Server stopped by user")
    except Exception as e:
        logging.error(f"[MCP] Server error: {e}")
        sys.exit(1)