# Claude Voice Commands

Enable natural voice interaction with Claude Code through MCP (Model Context Protocol).

## Features

- 🎤 **Voice-to-text commands** - Speak naturally to Claude Code
- 🔊 **Wake word activation** - "Hey Claude" to start listening
- 🚀 **Low latency** - Sub-second response with Google Speech Recognition
- 🔄 **Multiple backends** - Google, Whisper, and OpenAI Realtime support
- 📝 **Command queue** - Handle multiple rapid commands
- 🛡️ **Privacy-focused** - Only listens when activated

## Quick Start

### Prerequisites

- Python 3.8+
- macOS, Windows, or Linux
- Working microphone
- Claude Desktop app

### Installation

1. Clone the repository:
```bash
git clone https://github.com/JWitcoff/Claude_Chat.git
cd Claude_Chat
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Test your microphone:
```bash
python tests/test_microphone.py
```

5. Configure Claude Desktop (Available Now):
See [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md) for complete setup instructions.

Quick setup:
```json
{
  "mcpServers": {
    "claude-voice-commands": {
      "command": "python",
      "args": ["-m", "mcp_server.voice_server"],
      "cwd": "/path/to/Claude_Chat",
      "env": {
        "PYTHONPATH": "/path/to/Claude_Chat",
        "VOICE_BACKEND": "elevenlabs"
      }
    }
  }
}
```

6. Restart Claude Desktop and test with: **"Test my microphone setup"**

## Usage

### Available Voice Commands (Sprint 2)

**Setup & Testing:**
- **"Test my microphone setup"** - Verify audio configuration
- **"What voice recognition engines are available?"** - Check system status
- **"List my audio devices"** - Show available microphones
- **"Calibrate my microphone"** - Adjust for ambient noise

**Voice Input:**  
- **"I want to give you a voice command"** - Single voice input
- **"Transcribe what I'm about to say"** - Record and convert speech
- **"Listen for my voice input for 10 seconds"** - Timed recording

### Example Interactions

**Current (Sprint 2):**
```
You: "Test my microphone setup"  
Claude: ✅ Microphone test passed! Device: MacBook Pro Microphone

You: "I want to give you a voice command"
Claude: 🎤 Ready to listen. Please speak your command.
You: [Speak: "Create a Python function to sort a list"]
Claude: [Creates the function based on your voice input]
```

**Coming in Sprint 3:**
- Continuous listening mode
- Wake word activation ("Hey Claude")
- Command queuing and chaining

## Configuration

Create a `.env` file:
```bash
# Recognition Settings
VOICE_BACKEND=google        # Primary: google, whisper, openai
VOICE_ENERGY_THRESHOLD=4000 # Microphone sensitivity
WAKE_WORDS=hey claude,claude

# Optional API Keys (for premium features)
OPENAI_API_KEY=sk-...       # For ultra-low latency
```

## Development

See [ROADMAP.md](ROADMAP.md) for the development plan and [CLAUDE.md](CLAUDE.md) for Claude Code guidance.

### Current Status

- **✅ Sprint 0**: Project Setup Complete
- **✅ Sprint 1**: ElevenLabs Voice Recognition Complete  
- **✅ Sprint 2**: MCP Server Foundation Complete
- **🚧 Sprint 3**: Continuous Listening Mode (In Development)

**Main Branch**: Stable releases with Sprint 0-2 complete  
**Development Branch**: `sprint-3-continuous-listening` for new features

## Troubleshooting

### Microphone Issues
```bash
# List available microphones
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

# Calibrate for ambient noise
python tests/calibrate_mic.py
```

### Recognition Issues
- Speak clearly and at normal pace
- Reduce background noise
- Adjust `VOICE_ENERGY_THRESHOLD` in .env

## License

MIT

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Acknowledgments

- Google Speech Recognition API
- OpenAI Whisper
- FastMCP for MCP integration