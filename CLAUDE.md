# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SiriBot** is a privacy-first macOS menu bar AI assistant powered by Ollama. It runs entirely locally and integrates with Apple's Calendar, Notes, Reminders, and Shortcuts apps. The codebase mixes Python (core AI logic) and Swift (macOS UI and integrations).

## Architecture

SiriBot uses a **multi-agent orchestration pattern** coordinated by a central `SiriBot` class:

### Core Components

1. **Orchestrator** (`orchestrator.py`)
   - Main coordinator that initializes and manages all agents and services
   - Entry point for chat operations, workflow execution, and status checks
   - Lazily initializes advanced services with graceful fallbacks

2. **Agents** (in `agents/`)
   - **ConversationAgent**: Routes user intents, manages conversation history, orchestrates multi-step tasks
   - **ReasoningAgent**: Analyzes problems, plans multi-step solutions, performs reasoning
   - **ToolAgent**: Executes tools safely, validates outputs via SafetyManager
   - **MemoryAgent**: Stores and retrieves conversation context from SQLite (`data/memory.db`)

3. **Tool System** (`tools/`)
   - Registry-based tool registration (in `ToolRegistry`)
   - Tool categories: `system`, `file`, `app`, `network`, `custom`
   - Built-in tools: shell commands, file operations, app launching
   - Tools are registered during `SiriBot.__init__()` and used by ToolAgent

4. **Integrations** (`shared/Services/`)
   - **CalendarIntegration** / **NotesIntegration** / **RemindersIntegration**: Python wrappers for macOS services
   - **WorkflowEngine**: Executes predefined workflows autonomously
   - **PluginMarketplace**: Manages plugin discovery and loading
   - **SyncService**: Device-to-device synchronization
   - All integrations gracefully degrade if unavailable (macOS-only features)

5. **Model Management** (`core/model_manager.py`)
   - Connects to Ollama via HTTP
   - Supports switching between model providers at runtime
   - Falls back gracefully if Ollama is unavailable

6. **macOS UI** (`macos/SiriBot/`)
   - Xcode project generated from `project.yml` (via xcodegen)
   - Swift sources in `Sources/`, shared Swift models in `shared/Models/` and `shared/Services/`
   - Menu bar app with floating chat window

### Data Flow

```
User Input (CLI/Voice/Shortcuts) 
  → ConversationAgent (intent classification)
  → ReasoningAgent (planning) 
  → ToolAgent (execution with safety checks)
  → MemoryAgent (context storage)
  → Response to user
```

## Development Commands

### Setup & Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Initialize configuration
python main.py init --config config/config.yaml
```

### Running

```bash
# Interactive chat
python main.py chat

# Voice mode (hands-free)
python main.py voice

# Single command execution
python main.py run "your command here"

# Show available tools
python main.py tools

# Health check
python main.py health
```

### Workflows & Plugins

```bash
# List workflows
python main.py workflow list

# Run a workflow
python main.py workflow run <workflow_id>

# List installed plugins
python main.py plugins list

# List personal models
python main.py models list

# Show sync status
python main.py sync
```

### macOS App Build

```bash
# Build DMG installer
./setup/build_dmg.sh

# Build studio DMG (development build)
./setup/build_studio_dmg.sh
```

The DMG builder:
- Uses xcodegen to generate Xcode project from `macos/SiriBot/project.yml`
- Builds with Xcode (`xcodebuild`)
- Creates a distributable DMG in `build/`
- Requires macOS 14.0+ and Xcode 15.0+

### Debugging

```bash
# Verbose mode
python main.py --verbose chat

# Custom config file
python main.py --config /path/to/config.yaml chat
```

## Directory Structure

```
SiriBot/
├── main.py                         # Entry point
├── orchestrator.py                 # SiriBot orchestrator (core coordinator)
├── cli/
│   ├── main.py                     # Click CLI commands
│   └── interface.py                # Interactive chat interface
├── agents/
│   ├── conversation_agent.py       # Intent routing & conversation flow
│   ├── reasoning_agent.py          # Planning & reasoning
│   ├── tool_agent.py               # Tool execution & safety checks
│   └── memory_agent.py             # Conversation memory (SQLite)
├── core/
│   ├── config.py                   # Pydantic config model
│   ├── model_manager.py            # Ollama connection & provider switching
│   └── logger.py                   # Logging setup
├── tools/
│   ├── registry.py                 # Tool registry and Tool dataclass
│   └── basic/                      # Shell, file, and app tools
├── shared/
│   ├── Services/                   # Apple integrations (Calendar, Notes, Reminders)
│   ├── Models/                     # Swift data models (Message, ViewModel, etc.)
│   └── Protocols/                  # Swift protocol definitions
├── macos/
│   ├── SiriBot/
│   │   ├── project.yml             # Xcode project spec (xcodegen)
│   │   ├── Sources/                # Swift source code
│   │   ├── Resources/              # Assets, images, nibs
│   │   └── Supporting/             # Info.plist, entitlements
│   └── SiriBot.xcodeproj/          # Generated Xcode project
├── setup/
│   ├── build_dmg.sh                # DMG builder script
│   ├── build.sh                    # Build script
│   └── quickstart.py               # Post-install setup wizard
├── config/
│   └── config.example.yaml         # Example configuration
├── data/
│   └── memory.db                   # SQLite memory database
├── shortcuts/                      # Apple Shortcuts integration
│   ├── URLHandler.swift            # Shortcuts URL scheme handler
│   └── shortcuts_config.json       # Shortcut URL patterns
└── requirements.txt                # Python dependencies
```

## Key Design Patterns

- **Agent Pattern**: Each agent handles a specific responsibility (conversation, reasoning, tools, memory)
- **Tool Registry**: Extensible tool system with safety checks (SafetyManager prevents unsafe tool execution)
- **Graceful Degradation**: Advanced services (sync, workflows, plugins, integrations) fail silently; core functionality persists
- **Async/Await**: Heavy use of `asyncio` for non-blocking operations
- **Pydantic Models**: Configuration validation via `core/config.py`

## Important Notes

- **No tests**: This codebase has no test suite. New features should be tested manually.
- **Python 3.12+**: Required by Pydantic 2.0 and type hints
- **Ollama Dependency**: Core AI requires Ollama running locally (`ollama serve`)
- **macOS-Only**: Many integrations (Calendar, Notes, Reminders, voice) are macOS-specific
- **Configuration**: Config is YAML-based (`config/config.yaml`) with Pydantic validation
- **Safety**: SafetyManager in ToolAgent validates tool usage before execution
- **Voice**: Uses OpenAI Whisper (speech-to-text) and pyttsx3 (text-to-speech)

## Common Tasks

### Adding a New Tool
1. Create tool function in `tools/basic/` with signature: `def tool_fn(args: dict) -> dict`
2. Wrap in `Tool` dataclass with name, description, category, function, parameters
3. Register in `SiriBot._register_tools()` via `self.tool_registry.register(tool)`

### Adding a New Agent
1. Create new class in `agents/` inheriting the agent pattern
2. Implement required interface expected by ConversationAgent
3. Initialize in `SiriBot.__init__()` and integrate into workflow

### Adding a New Integration
1. Create service module in `shared/Services/`
2. Add getter function (e.g., `get_calendar_integration()`)
3. Initialize gracefully in `SiriBot._init_advanced_services()` with try/except fallback
4. Add to `get_integrations()` check

### Building for Distribution
1. Update version in `orchestrator.py` (`VERSION`), `macos/SiriBot/project.yml` (`MARKETING_VERSION`), and `README.md`
2. Run `./setup/build_dmg.sh`
3. Verify DMG in `build/`

## Debugging Hints

- **Model Connection Issues**: Check if Ollama is running (`ollama serve`) on localhost:11434
- **macOS Integration Failures**: Usually due to missing permissions or being on non-macOS
- **Service Initialization**: Look for warnings in logs; services fail gracefully
- **Memory Growth**: Check `data/memory.db` size and MemoryAgent cleanup policies
- **Async Issues**: Use verbose logging (`--verbose`) to trace async execution order
