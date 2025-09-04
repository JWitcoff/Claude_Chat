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

5. Configure Claude Desktop (Sprint 2+):
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "voice-commands": {
      "command": "python",
      "args": ["-m", "mcp_server.voice_server"],
      "cwd": "/path/to/Claude_Chat",
      "env": {
        "PYTHONPATH": "/path/to/Claude_Chat"
      }
    }
  }
}
```

6. Restart Claude Desktop

## Usage

### Basic Commands

Say to Claude Code:
- **"Activate voice mode"** - Start continuous listening
- **"Stop voice mode"** - Stop listening
- **"Hey Claude, [command]"** - Wake word activation

### Example Interactions

```
You: "Activate voice mode"
Claude: ✅ Voice mode activated

You: "Create a Python function to sort a list"
Claude: [Creates the function]

You: "Now add error handling to it"
Claude: [Modifies the code]

You: "Stop voice mode"
Claude: ✅ Voice mode deactivated
```

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

- Sprint 0: Project Setup ✅
- Sprint 1: Basic Voice Capture (In Progress)

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