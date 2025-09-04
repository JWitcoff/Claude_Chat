#!/usr/bin/env python3
"""
Microphone and speech recognition test script
Tests ElevenLabs, Google, and Whisper backends
"""

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.speech_engines import MultiEngine, RecognitionBackend
import speech_recognition as sr

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_audio_devices():
    """Test available audio input devices"""
    print("🎤 Testing Audio Devices")
    print("=" * 50)
    
    try:
        mics = sr.Microphone.list_microphone_names()
        print(f"Found {len(mics)} audio input devices:")
        
        for i, name in enumerate(mics):
            marker = " (DEFAULT)" if i == sr.Microphone().device_index else ""
            print(f"  {i}: {name}{marker}")
        
        return True
    except Exception as e:
        print(f"❌ Error listing audio devices: {e}")
        return False

def test_microphone_basics():
    """Test basic microphone functionality"""
    print("\n🔧 Testing Microphone Basics")
    print("=" * 50)
    
    try:
        engine = MultiEngine()
        test_result = engine.test_microphone(duration=2.0)
        
        if test_result['success']:
            print("✅ Microphone test passed!")
            print(f"   Device index: {test_result['microphone_index']}")
            print(f"   Energy threshold: {test_result['energy_threshold']}")
            print(f"   Audio captured: {test_result['audio_captured']}")
        else:
            print(f"❌ Microphone test failed: {test_result['error']}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Microphone test error: {e}")
        return False

def test_calibration():
    """Test microphone calibration"""
    print("\n📏 Testing Microphone Calibration")
    print("=" * 50)
    
    try:
        engine = MultiEngine()
        print("Calibrating microphone for ambient noise...")
        print("(Please stay quiet for 3 seconds)")
        
        engine.calibrate_microphone(duration=3.0)
        print("✅ Calibration completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Calibration failed: {e}")
        return False

async def test_recognition_backend(backend_name: str = None):
    """Test speech recognition with specific or all backends"""
    print(f"\n🗣️  Testing Speech Recognition")
    if backend_name:
        print(f"Backend: {backend_name}")
    else:
        print("All available backends")
    print("=" * 50)
    
    try:
        engine = MultiEngine()
        
        if not engine.engines:
            print("❌ No recognition engines available!")
            return False
        
        print("Available engines:", list(engine.engines.keys()))
        
        # Test specific backend or use multi-engine
        if backend_name:
            backend_enum = RecognitionBackend(backend_name)
            if backend_enum not in engine.engines:
                print(f"❌ Backend {backend_name} not available")
                return False
            
            test_engine = engine.engines[backend_enum]
        else:
            test_engine = engine
        
        print("\n🎤 Speak now (you have 5 seconds)...")
        print("   Try saying: 'Hello Claude, this is a test'")
        
        # Capture audio
        recognizer = sr.Recognizer()
        microphone = engine.get_microphone()
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        print("🔄 Processing audio...")
        
        # Recognize speech
        if hasattr(test_engine, 'recognize_with_fallback'):
            result = await test_engine.recognize_with_fallback(audio)
        else:
            result = await test_engine.recognize(audio)
        
        print("✅ Recognition successful!")
        print(f"   Text: '{result.text}'")
        print(f"   Backend: {result.backend.value}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Processing time: {result.processing_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Recognition test failed: {e}")
        return False

def test_api_keys():
    """Test API key configuration"""
    print("\n🔑 Testing API Keys")
    print("=" * 50)
    
    # Check ElevenLabs API key
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    if elevenlabs_key and elevenlabs_key.strip():
        print("✅ ElevenLabs API key configured")
    else:
        print("⚠️  ElevenLabs API key not found (set ELEVENLABS_API_KEY in .env)")
    
    # Check OpenAI API key (optional)
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key.strip():
        print("✅ OpenAI API key configured (for future use)")
    else:
        print("ℹ️  OpenAI API key not configured (optional)")
    
    return True

def run_full_test_suite():
    """Run all tests"""
    print("🚀 Claude Voice Commands - Microphone Test Suite")
    print("=" * 70)
    
    tests = [
        ("Audio Devices", test_audio_devices),
        ("Microphone Basics", test_microphone_basics),
        ("API Keys", test_api_keys),
        ("Calibration", test_calibration),
    ]
    
    results = {}
    
    # Run synchronous tests
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Run async recognition test
    try:
        result = asyncio.run(test_recognition_backend())
        results["Speech Recognition"] = result
    except Exception as e:
        print(f"❌ Speech Recognition test crashed: {e}")
        results["Speech Recognition"] = False
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"  {test_name:<20} {status}")
        if passed_test:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your microphone setup is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

async def interactive_test():
    """Interactive speech recognition test"""
    print("🗣️  Interactive Speech Recognition Test")
    print("=" * 50)
    print("This will continuously listen and transcribe what you say.")
    print("Say 'stop' to exit.")
    print()
    
    engine = MultiEngine()
    recognizer = sr.Recognizer()
    microphone = engine.get_microphone()
    
    # Calibrate
    with microphone as source:
        print("📏 Calibrating...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print(f"Energy threshold: {recognizer.energy_threshold}")
    
    print("\n🎤 Listening... (say 'stop' to exit)")
    
    while True:
        try:
            with microphone as source:
                # Listen for audio
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=10)
            
            print("🔄 Processing...")
            
            # Recognize speech
            result = await engine.recognize_with_fallback(audio)
            
            print(f"🗣️  You said: '{result.text}'")
            print(f"    Backend: {result.backend.value} | "
                  f"Confidence: {result.confidence:.2f} | "
                  f"Time: {result.processing_time:.2f}s")
            
            # Check for stop command
            if 'stop' in result.text.lower():
                print("👋 Stopping interactive test...")
                break
                
        except sr.WaitTimeoutError:
            # Timeout is normal, just continue
            pass
        except KeyboardInterrupt:
            print("\n👋 Stopping interactive test...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Test microphone and speech recognition")
    parser.add_argument('--backend', choices=['elevenlabs', 'google', 'whisper'], 
                       help='Test specific backend')
    parser.add_argument('--interactive', action='store_true',
                       help='Run interactive continuous test')
    parser.add_argument('--devices', action='store_true',
                       help='List audio devices only')
    
    args = parser.parse_args()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    if args.devices:
        test_audio_devices()
    elif args.interactive:
        asyncio.run(interactive_test())
    elif args.backend:
        asyncio.run(test_recognition_backend(args.backend))
    else:
        # Run full test suite
        success = run_full_test_suite()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()