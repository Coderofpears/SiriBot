# AGENTS.md

## Project Overview
SiriBot is a privacy-first macOS menu bar AI assistant with:
- Python core (agents, tools, CLI) for AI orchestration
- Swift UI (macOS app) for native integration
- Local AI via Ollama (primary) with cloud provider fallbacks
- Apple service integrations (Calendar, Notes, Reminders, Shortcuts)

## Key Architecture Facts
- Multi-agent system coordinated by `SiriBot` orchestrator
- Python CLI entry point: `main.py` → `cli/main.py`
- Swift app entry point: `macos/SiriBot/Sources/main.swift`
- Xcode projects generated from YAML via xcodegen
- Core conversation flow: User → ConversationAgent → ReasoningAgent → ToolAgent → Tools

## Critical Development Commands

### Python Setup & Run
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize config
python main.py init

# Interactive chat
python main.py chat

# Voice mode
python main.py voice

# Run single command
python main.py run "your command"

# Health check
python main.py health
```

### Swift App Build
```bash
# Generate Xcode project
cd macos/SiriBot && xcodegen generate

# Build app
xcodebuild -scheme SiriBot -configuration Release build

# Create distributable DMG
./setup/build_dmg.sh

# Build studio (development version)
./setup/build_studio_dmg.sh
```

## Repo Structure Facts
- `agents/` - Conversation, Reasoning, Tool, Memory agents
- `tools/` - Registry and basic tools (shell, file, app)
- `core/` - Model manager, config, logger
- `cli/` - Command-line interface
- `macos/SiriBot/` - Main Swift app
- `studio/SiriBotStudio/` - Development studio app
- `shared/` - Shared Swift models and services
- `setup/` - Build and deployment scripts

## Testing & Debugging
- No unit tests currently - manual verification required
- Use `--verbose` flag for detailed logging
- Check `data/memory.db` for SQLite memory entries
- Ensure Ollama is running at `localhost:11434` for local AI
- Fixed several Swift compilation issues in shared services (LogService, AIPService, HandoffService, DesktopControlService, VoiceService)

## Deployment
1. Update versions in `orchestrator.py`, `macos/SiriBot/project.yml`, `studio/SiriBotStudio/project.yml`
2. Run `./setup/build_dmg.sh`
3. Find DMG in `build/` directory
4. For releases, follow `.github/RELEASE_GUIDE.md`

## Key Constraints
- Python 3.12+ required
- macOS 14.0+ required for Swift app
- Xcode 15.0+ required for building
- Ollama must be installed for local AI
- SafetyManager blocks risky operations by default

## Recent Bug Fixes
- Fixed database connection leaks in memory_agent.py
- Improved Ollama stream parsing in model_manager.py
- Fixed Safety Manager auto-confirmation in tool_agent.py
- Added conversation history size limit in conversation_agent.py
- Improved health check accuracy in orchestrator.py
- Fixed Swift compilation issues in shared services