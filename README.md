# 🤖 SiriBot

**SiriBot** is an open-source, local-first, multimodal, agentic AI assistant that controls your Mac.

## Features

### Core Capabilities
- **Local-First AI**: Runs entirely on your machine using Ollama/llama.cpp
- **BYOK Support**: Plug in your own API keys for OpenAI/Anthropic cloud fallback
- **Voice Control**: Hands-free operation with hotword detection
- **Desktop Control**: Automate clicks, typing, and UI interactions
- **Handoff Mode**: AI works independently on its own virtual desktop
- **Apple Shortcuts**: Deep integration with macOS Shortcuts app

### Applications
- **SiriBot** (Menu Bar App): Always listening, minimal footprint
- **SiriBot Studio**: Full-featured desktop application for power users

## Quick Start

### Prerequisites
- macOS 14.0+
- Xcode 15+ (for building)
- Ollama (for local AI, optional)

### Installation

1. **Install XcodeGen**:
```bash
brew install xcodegen
```

2. **Build the app**:
```bash
cd macos/SiriBot
xcodegen generate
xcodebuild -scheme SiriBot -configuration Release build
```

3. **Run SiriBot**:
```bash
open macos/build/Release/SiriBot.app
```

### Configuration
On first launch, the Setup wizard will guide you through:
- AI Provider selection (Ollama/OpenAI/Anthropic)
- Voice settings
- Desktop control permissions

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SiriBot Studio / Menu Bar                  │
├─────────────────────────────────────────────────────────────┤
│                  Background Service (Hotword)                │
├─────────────────────────────────────────────────────────────┤
│                    SiriBot Orchestrator                      │
├────────────────┬────────────────┬──────────────────────────┤
│  Conversation  │    Reasoning   │         Tool              │
│    Agent       │     Agent      │        Agent              │
├────────────────┴────────────────┴──────────────────────────┤
│                    Tool Registry                             │
├──────────────┬──────────────┬──────────────┬───────────────┤
│ System Tools │ App Control  │ File Ops     │ Desktop Ctrl  │
├──────────────┴──────────────┴──────────────┴───────────────┤
│              Model Manager (Ollama + BYOK)                  │
├─────────────────────────────────────────────────────────────┤
│         Multi-Device Sync │ Workflow Engine                 │
│         Plugin Marketplace │ Personal Model Manager         │
└─────────────────────────────────────────────────────────────┘
```
┌─────────────────────────────────────────────────────────────┐
│                    SiriBot Studio / Menu Bar                  │
├─────────────────────────────────────────────────────────────┤
│                  Background Service (Hotword)                │
├─────────────────────────────────────────────────────────────┤
│                    SiriBot Orchestrator                      │
├────────────────┬────────────────┬──────────────────────────┤
│  Conversation  │    Reasoning   │         Tool             │
│    Agent       │     Agent      │        Agent             │
├────────────────┴────────────────┴────────────────────────┤
│                    Tool Registry                            │
├──────────────┬──────────────┬──────────────┬───────────────┤
│ System Tools │ App Control  │ File Ops     │ Desktop Ctrl  │
├──────────────┴──────────────┴──────────────┴───────────────┤
│              Model Manager (Ollama + BYOK)                  │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### Voice Control
Say "Hey Siri" to activate voice mode. Configure your hotword in Settings.

### Handoff Mode
Tell SiriBot to handle a complex task:
> "Organize my Downloads folder and move all PDFs to a Documents subfolder"

SiriBot will:
1. Create its own virtual desktop
2. Execute the task step by step
3. Notify you when complete

### Skills System
Extend SiriBot with custom skills:
- **Code Helper**: Write and debug code
- **File Organizer**: Sort and manage files
- **Research**: Find and summarize information
- **Writer**: Draft documents and emails

### Multi-Device Sync
Sync your settings, memory, and preferences across all your Macs:
- Real-time synchronization
- Conflict resolution
- Offline support

### Autonomous Workflows
Create self-directing workflows that execute tasks automatically:
- Scheduled workflows (e.g., daily reports)
- Event-triggered workflows
- Multi-step task automation
- Retry logic and error handling

### Plugin Marketplace
Extend SiriBot with plugins:
- **Code Helper**: Advanced code analysis
- **Web Search**: Search the web for information
- **Image Processor**: Process and manipulate images
- Install from marketplace or build your own

### Personal Fine-Tuned Models
Train your own AI models:
- LoRA adapters for efficient fine-tuning
- Custom training datasets
- Model evaluation and metrics
- Export and share configurations

### Apple Shortcuts Integration
Use SiriBot from Shortcuts app:
```
siribot://chat?text=YOUR_MESSAGE
siribot://handoff?task=YOUR_TASK
siribot://voice?command=YOUR_COMMAND
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| ⌘+, | Settings |
| ⌘+L | Toggle Listening |
| ⌘+H | Handoff Mode |
| ⌘+K | Clear Chat |

## Project Structure

```
SiriBot/
├── macos/
│   └── SiriBot/           # Main menu bar app
│       ├── Sources/       # Swift source files
│       ├── Resources/     # Assets, configs
│       └── Supporting/    # Info.plist, entitlements
├── studio/
│   └── SiriBotStudio/     # Full desktop application
├── shared/
│   ├── Models/           # Data models
│   └── Services/         # Core services (AI, Voice, etc.)
├── shortcuts/            # Apple Shortcuts documentation
├── setup/                # Build and deployment scripts
└── README.md
```

## Development

### Building
```bash
./setup/build.sh
```

### Deploying to GitHub
```bash
GITHUB_TOKEN=xxx ./setup/deploy.sh SiriBot
```

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please read the contribution guidelines and submit PRs.

---

**SiriBot** — Your AI, on your Mac, in your control.
