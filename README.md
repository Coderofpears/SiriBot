# SiriBot
### Your Personal AI Assistant for Mac

![SiriBot](https://img.shields.io/badge/Version-1.0.0-blue)
![macOS](https://img.shields.io/badge/macOS-14.0+-orange)
![License](https://img.shields.io/badge/License-MIT-green)

**SiriBot** is an easy-to-use AI assistant that lives in your menu bar and helps you accomplish tasks on your Mac — with just your voice or keyboard.

---

## Features

### 🤖 Always There
- Lives in your menu bar, ready when you need it
- Start chatting instantly with `/voice` or just type
- Works alongside any app

### 🗣️ Voice Control
- "Hey SiriBot, organize my Downloads folder"
- Hands-free operation while you work
- Configurable wake word

### 📅 Apple Integration
- **Calendar** — Create events, see your schedule
- **Notes** — Save notes, search your notes
- **Reminders** — Set and manage reminders
- **Shortcuts** — Works with Apple Shortcuts app

### 🔄 Handoff Mode
Let SiriBot work on its own virtual desktop while you continue working.

### 🌐 Multi-Device Sync
Sync your settings across all your Macs.

---

## Download

### DMG Installer (Recommended)
Download the latest release from GitHub:
- **[Download SiriBot for macOS](https://github.com/Coderofpears/SiriBot/releases/latest)**

### From Source
```bash
git clone https://github.com/Coderofpears/SiriBot.git
cd SiriBot
./setup/build_dmg.sh
```

---

## Getting Started

### 1. Download Ollama
SiriBot uses Ollama for local AI. Download it free from [ollama.com](https://ollama.com) or run:
```bash
brew install ollama
```

### 2. Download a Model
```bash
ollama pull llama3.2
```

### 3. Install SiriBot
Open the DMG and drag SiriBot to Applications.

### 4. Launch SiriBot
Open SiriBot from Applications. On first launch, the setup wizard will guide you through:
- Choosing your AI model
- Setting up voice (optional)
- Granting permissions

---

## Using Apple Shortcuts

SiriBot works with Apple Shortcuts! Add it to your workflows:

### Quick Actions
- `siribot://chat?text=YOUR_MESSAGE` — Send a message
- `siribot://handoff?task=YOUR_TASK` — Run a task
- `siribot://voice?command=YOUR_COMMAND` — Voice command

### Example Shortcuts
1. Open Shortcuts app
2. Tap "+" to create new shortcut
3. Add "URL" action
4. Enter: `siribot://chat?text=What's on my calendar today?`
5. Add "Open URLs" action
6. Run your shortcut!

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| ⌘+L | Toggle listening |
| ⌘+, | Settings |
| ⌘+K | Clear chat |

---

## System Requirements

- macOS 14.0 (Sonoma) or later
- Apple Silicon or Intel Mac
- 4GB RAM minimum
- Ollama (free, runs locally)

---

## Privacy

**Your data stays on your Mac.**
- All AI processing happens locally by default
- No subscription required
- No cloud accounts needed
- Your conversations are private

---

## Support

- **Issues**: [GitHub Issues](https://github.com/Coderofpears/SiriBot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Coderofpears/SiriBot/discussions)

---

**Made with ❤️ for Mac users who want AI that respects their privacy.**