#!/usr/bin/env python3
"""
Direct test of voice server components
Tests the underlying functionality without MCP decoration layer
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO)

async def test_voice_server_components():
    """Test the underlying voice server components"""
    
    print("🧪 Testing Voice Server Components")
    print("=" * 50)
    
    # Test 1: Import speech engine
    print("\n📦 Testing speech engine import...")
    try:
        from mcp_server.speech_engines import MultiEngine
        engine = MultiEngine()
        print(f"   ✅ Speech engine initialized with {len(engine.engines)} backends")
        print(f"   Available: {[e.value for e in engine.engines.keys()]}")
        print(f"   Primary: {engine.primary.value if engine.primary else 'None'}")
    except Exception as e:
        print(f"   ❌ Speech engine error: {e}")
        return False
    
    # Test 2: Test microphone functionality
    print("\n🎤 Testing microphone...")
    try:
        result = engine.test_microphone(duration=1.0)
        print(f"   Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"   Device: {result.get('microphone_index')}")
            print(f"   Threshold: {result.get('energy_threshold', 0):.1f}")
        else:
            print(f"   Note: {result.get('error', 'Unknown issue')}")
    except Exception as e:
        print(f"   ❌ Microphone error: {e}")
    
    # Test 3: List audio devices
    print("\n🔊 Testing audio device listing...")
    try:
        devices = engine.list_available_microphones()
        print(f"   Found {len(devices)} devices:")
        for device in devices[:3]:  # Show first 3
            marker = " ⭐" if device.get('default') else ""
            print(f"     {device['index']}: {device['name']}{marker}")
    except Exception as e:
        print(f"   ❌ Device listing error: {e}")
    
    # Test 4: Environment configuration
    print("\n⚙️  Testing configuration...")
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    voice_backend = os.getenv('VOICE_BACKEND', 'elevenlabs')
    
    print(f"   Backend config: {voice_backend}")
    print(f"   ElevenLabs API: {'✅ Configured' if elevenlabs_key else '❌ Not set'}")
    
    # Test 5: Quick recognition test (no actual voice)
    print("\n🗣️  Testing recognition setup...")
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        microphone = engine.get_microphone()
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            threshold = recognizer.energy_threshold
            print(f"   ✅ Recognition setup ready (threshold: {threshold:.1f})")
    except Exception as e:
        print(f"   ⚠️  Recognition setup issue: {e}")
    
    # Test 6: MCP server structure validation
    print("\n🌐 Testing MCP server structure...")
    try:
        from mcp_server.voice_server import mcp
        tools = mcp.list_tools()
        print(f"   ✅ MCP server has {len(tools)} tools:")
        for tool in tools:
            print(f"     - {tool.name}")
    except Exception as e:
        print(f"   ❌ MCP structure error: {e}")
    
    print("\n✨ Component test complete!")
    print("\n🚀 To test with Claude Code:")
    print("   1. Add MCP config to Claude Desktop")
    print("   2. Restart Claude Desktop")
    print("   3. Try: 'Test my microphone using the voice server'")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_voice_server_components())