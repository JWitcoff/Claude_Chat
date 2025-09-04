#!/usr/bin/env python3
"""
Test script for MCP voice server tools
Tests each tool individually without requiring MCP connection
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO)

async def test_mcp_tools():
    """Test all MCP tools individually"""
    
    # Import the tools from the server
    try:
        from mcp_server.voice_server import (
            ping, test_microphone, calibrate_audio, 
            list_audio_devices, get_engine_status, transcribe_once
        )
        print("✅ Successfully imported MCP tools")
    except ImportError as e:
        print(f"❌ Failed to import MCP tools: {e}")
        return False
    
    results = {}
    
    # Test 1: Ping
    print("\n🔧 Testing ping...")
    try:
        result = await ping({"test": "data"})
        print(f"   Result: {result}")
        results['ping'] = result.get('ok', False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['ping'] = False
    
    # Test 2: Engine Status
    print("\n📊 Testing get_engine_status...")
    try:
        result = await get_engine_status()
        print(f"   Available engines: {result.get('available_engines', [])}")
        print(f"   Primary: {result.get('primary_engine')}")
        print(f"   ElevenLabs configured: {result.get('elevenlabs_api_configured')}")
        results['engine_status'] = result.get('total_engines', 0) > 0
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['engine_status'] = False
    
    # Test 3: List Audio Devices
    print("\n🎤 Testing list_audio_devices...")
    try:
        result = await list_audio_devices()
        print(f"   Found {result.get('total_count', 0)} devices")
        if result.get('devices'):
            for device in result['devices'][:3]:  # Show first 3
                marker = " (default)" if device.get('default') else ""
                print(f"     {device['index']}: {device['name']}{marker}")
        results['audio_devices'] = result.get('total_count', 0) > 0
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['audio_devices'] = False
    
    # Test 4: Calibrate Audio
    print("\n📏 Testing calibrate_audio...")
    try:
        result = await calibrate_audio(duration=1.0)
        print(f"   Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"   Energy threshold: {result.get('energy_threshold', 0):.1f}")
        results['calibrate'] = result.get('success', False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['calibrate'] = False
    
    # Test 5: Test Microphone
    print("\n🔊 Testing test_microphone...")
    try:
        result = await test_microphone(duration=1.0)
        print(f"   Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"   Device index: {result.get('microphone_index')}")
            print(f"   Audio captured: {result.get('audio_captured')}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        results['microphone'] = result.get('success', False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['microphone'] = False
    
    # Test 6: Transcribe Once (optional - requires speaking)
    print("\n🗣️  Testing transcribe_once (quick timeout)...")
    try:
        result = await transcribe_once(duration=1)  # Very short timeout
        if result.get('success'):
            print(f"   ✅ Transcription: '{result.get('text')}'")
            print(f"   Backend: {result.get('backend')}")
        else:
            if result.get('timeout'):
                print("   ⏰ No speech detected (expected)")
                results['transcribe'] = True  # This is expected
            else:
                print(f"   ❌ Error: {result.get('error')}")
                results['transcribe'] = False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['transcribe'] = False
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name:<15} {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All MCP tools are working correctly!")
        return True
    else:
        print("⚠️  Some tools have issues. Check the errors above.")
        return False

if __name__ == "__main__":
    print("🧪 MCP Tools Test Suite")
    print("=" * 50)
    success = asyncio.run(test_mcp_tools())
    sys.exit(0 if success else 1)