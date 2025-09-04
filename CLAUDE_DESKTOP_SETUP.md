# Claude Desktop Setup for Voice Commands

## Quick Setup Instructions

### 1. Add MCP Configuration

Edit your Claude Desktop configuration file:
```bash
# macOS
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows  
notepad %APPDATA%\Claude\claude_desktop_config.json

# Linux
nano ~/.config/Claude/claude_desktop_config.json
```

### 2. Add Voice Commands Server

Replace the contents with:
```json
{
  "mcpServers": {
    "claude-voice-commands": {
      "command": "python",
      "args": [
        "-m",
        "mcp_server.voice_server"
      ],
      "cwd": "/Users/justinwitcoff/Test/136775783/claude-voice-commands",
      "env": {
        "PYTHONPATH": "/Users/justinwitcoff/Test/136775783/claude-voice-commands",
        "VOICE_BACKEND": "elevenlabs",
        "VOICE_FALLBACK": "google",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**⚠️ Important**: Replace the `cwd` and `PYTHONPATH` with your actual project path!

### 3. Restart Claude Desktop

Completely quit and restart Claude Desktop for the changes to take effect.

### 4. Test the Integration

Try these commands with Claude Code:

#### Basic Tests:
- **"Test my microphone setup"**
- **"What voice recognition engines are available?"**
- **"List my audio devices"**
- **"Calibrate my microphone"**

#### Voice Command Tests:
- **"I want to give you a voice command"**
- **"Transcribe what I'm about to say"**
- **"Listen for my voice input for 10 seconds"**

### 5. Expected Behavior

When working correctly, you should see:
- Claude Code can access voice commands tools
- Microphone tests show your available devices
- Voice recognition uses ElevenLabs Pro for high accuracy
- Graceful fallback to Google/Whisper if needed

### 6. Troubleshooting

#### MCP Server Not Starting:
```bash
# Test server directly
cd /path/to/claude-voice-commands
source venv/bin/activate
python -m mcp_server.voice_server
```

#### Tools Not Available:
- Check Claude Desktop logs: `~/Library/Logs/Claude/mcp.log`
- Verify Python path is correct
- Ensure virtual environment is activated

#### Voice Recognition Issues:
```bash
# Test components directly
python tests/test_voice_server_direct.py
```

### 7. Advanced Configuration

You can customize the voice server by modifying environment variables in the Claude Desktop config:

```json
"env": {
  "PYTHONPATH": "/path/to/claude-voice-commands",
  "VOICE_BACKEND": "elevenlabs",           # Primary engine
  "VOICE_FALLBACK": "google",              # Fallback engine  
  "VOICE_ENERGY_THRESHOLD": "4000",       # Microphone sensitivity
  "VOICE_TIMEOUT": "10",                   # Recognition timeout
  "LOG_LEVEL": "DEBUG"                     # Detailed logging
}
```

## Success Indicators

✅ **MCP Server Running**: Claude Desktop starts without errors  
✅ **Tools Available**: Claude Code can list voice commands tools  
✅ **Microphone Working**: Test shows your devices and captures audio  
✅ **Recognition Active**: ElevenLabs Pro transcription working  
✅ **Voice Commands**: You can speak commands that Claude Code receives

## Next Steps

Once this is working, you can:
1. **Use Sprint 3 tools** for continuous listening mode
2. **Add wake word detection** ("Hey Claude")  
3. **Create voice command macros** for common tasks
4. **Integrate with other MCP servers** for expanded functionality

---

**Need Help?** Check the test results and logs, or run the diagnostic tools in the `tests/` directory.