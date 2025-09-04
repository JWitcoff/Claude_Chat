# CLAUDE.md

This file provides guidance to Claude Code when working with the Claude Voice Commands project.

## Project Overview

This project enables voice command interaction with Claude Code through an MCP (Model Context Protocol) server. Users can speak commands naturally, and Claude Code will receive and execute them.

## Quick Start Commands

### Setup & Installation
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test microphone setup
python tests/test_microphone.py

# Run the MCP server
python -m mcp_server.voice_server
```

### Testing Voice Recognition
```bash
# Test basic voice capture
python tests/test_voice.py

# Test with different backends
python tests/test_voice.py --backend google
python tests/test_voice.py --backend whisper

# Calibrate microphone
python tests/calibrate_mic.py
```

### MCP Server Operations
```bash
# Start MCP server (for Claude Desktop integration)
python -m mcp_server.voice_server

# Test MCP tools directly
python -m mcp_server.test_tools

# Check server health
python -m mcp_server.voice_server --health
```

## Architecture

### Directory Structure
```
claude-voice-commands/
├── mcp_server/           # MCP server implementation
│   ├── voice_server.py   # Main MCP server with tool definitions
│   ├── speech_engines.py # Recognition backend implementations
│   ├── command_queue.py  # Command queuing system
│   └── wake_word.py      # Wake word detection
├── config/               # Configuration files
├── tests/                # Test scripts
└── logs/                 # Runtime logs
```

### Core Components

1. **MCP Server** (`voice_server.py`)
   - FastMCP server exposing voice tools
   - Tools: start_listening, stop_listening, get_command, test_microphone

2. **Speech Engines** (`speech_engines.py`)
   - Google Speech Recognition (primary)
   - Whisper Local (fallback)
   - OpenAI Realtime (future premium option)

3. **Command Queue** (`command_queue.py`)
   - Thread-safe command queuing
   - Priority handling for urgent commands
   - Command history tracking

4. **Wake Word Detection** (`wake_word.py`)
   - Detects "Hey Claude", "Claude", etc.
   - Customizable wake words
   - Low CPU usage monitoring

## MCP Tools Available

### Core Tools
```python
# Start voice listening
await start_listening(mode="wake_word")  # or "continuous"

# Stop voice listening
await stop_listening()

# Get next voice command
command = await get_next_command(timeout=5.0)

# Test microphone setup
status = await test_microphone()
```

### Utility Tools
```python
# Record a voice note
note = await transcribe_voice_note(duration=30)

# Get listening status
status = await get_voice_status()

# Clear command queue
await clear_commands()
```

## Development Workflow

### Adding New Features
1. Check ROADMAP.md for current sprint
2. Create feature branch: `git checkout -b sprint-X-feature`
3. Implement with tests
4. Update ROADMAP.md progress
5. Test with Claude Desktop integration

### Testing Checklist
```bash
# Before committing
python -m pytest tests/          # Run all tests
python tests/test_microphone.py  # Test audio input
python tests/test_mcp_tools.py   # Test MCP integration
python tests/test_recognition.py # Test speech recognition
```

### Debugging

#### Common Issues & Solutions

**Issue: "No module named 'pyaudio'"**
```bash
# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio

# Windows
pip install pipwin
pipwin install pyaudio
```

**Issue: "Microphone not found"**
```bash
# Test available microphones
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

# Set specific microphone
export VOICE_MIC_INDEX=1  # Use the index from list above
```

**Issue: "Recognition fails"**
```bash
# Check ambient noise level
python tests/calibrate_mic.py

# Test with different sensitivity
export VOICE_ENERGY_THRESHOLD=4000  # Higher = less sensitive

# Force specific backend
export VOICE_BACKEND=whisper  # or 'google'
```

**Issue: "MCP connection failed"**
```bash
# Check MCP server is running
ps aux | grep voice_server

# Test MCP tools directly
python -c "from mcp_server.voice_server import test_microphone; print(test_microphone())"

# Check Claude Desktop config
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Performance Monitoring
```bash
# Monitor CPU usage during listening
python tests/benchmark_cpu.py

# Test recognition latency
python tests/benchmark_latency.py

# Check memory usage
python tests/profile_memory.py
```

## Configuration

### Environment Variables (.env)
```bash
# Recognition Settings
VOICE_BACKEND=google           # Primary backend: google, whisper, openai
VOICE_FALLBACK=whisper         # Fallback backend
VOICE_ENERGY_THRESHOLD=4000    # Microphone sensitivity
VOICE_PAUSE_THRESHOLD=0.8      # Pause between words
VOICE_TIMEOUT=5                # Recognition timeout (seconds)

# Wake Word Settings  
WAKE_WORDS=hey claude,claude,ok claude
WAKE_WORD_SENSITIVITY=0.5     # 0-1, higher = more strict

# API Keys (optional)
OPENAI_API_KEY=sk-...         # For OpenAI Realtime (Sprint 7)
ELEVENLABS_API_KEY=...        # Alternative option

# Logging
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/voice.log       
```

### Claude Desktop Configuration
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "voice-commands": {
      "command": "python",
      "args": ["-m", "mcp_server.voice_server"],
      "cwd": "/path/to/claude-voice-commands",
      "env": {
        "PYTHONPATH": "/path/to/claude-voice-commands",
        "VOICE_BACKEND": "google"
      }
    }
  }
}
```

## Sprint Progress Tracking

Current Sprint: **Sprint 0 - Project Setup**

When working on sprints:
1. Update task checkboxes in ROADMAP.md
2. Add completion notes to sprint section
3. Update progress table with dates
4. Commit with message: "Sprint X: [description]"

## Usage Examples

### Basic Voice Command Flow
```python
# User says: "Activate voice mode"
# Claude Code calls:
await start_listening(mode="continuous")

# User says: "Create a Python function to calculate fibonacci"
# Claude Code calls:
command = await get_next_command()
# Returns: {"text": "Create a Python function to calculate fibonacci", "confidence": 0.95}

# User says: "Stop voice mode"  
# Claude Code calls:
await stop_listening()
```

### Wake Word Flow
```python
# Claude Code calls:
await start_listening(mode="wake_word")

# User says: "Hey Claude, run the tests"
# Claude Code polls:
command = await get_next_command(timeout=1.0)
# Returns: {"text": "run the tests", "confidence": 0.92}
```

## Best Practices

1. **Always test microphone first**: Run `test_microphone()` before starting
2. **Handle errors gracefully**: Recognition can fail, always have fallback
3. **Respect user privacy**: Only listen when explicitly activated
4. **Optimize for latency**: Use Google first, Whisper as fallback
5. **Log everything**: Helps debug recognition issues
6. **Update documentation**: Keep ROADMAP.md current with progress

## Future Enhancements (Post-Sprint 10)

- [ ] Voice synthesis responses (Claude speaks back)
- [ ] Multi-user voice profiles
- [ ] Cloud command sync
- [ ] Mobile app companion
- [ ] Voice command marketplace

---

*Last updated: 2025-01-03 - Sprint 0*