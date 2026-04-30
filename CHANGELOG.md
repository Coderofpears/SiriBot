# Changelog

All notable changes to SiriBot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-29

### Added
- Initial release of SiriBot
- Menu bar AI assistant for macOS
- Local AI processing with Ollama
- Voice control capabilities
- Apple Calendar, Notes, and Reminders integration
- Handoff mode for background task execution
- Multi-device sync support
- Apple Shortcuts integration
- Privacy-focused design with all data stored locally

### Fixed
- Database connection leaks in memory_agent.py
- Improved Ollama stream parsing in model_manager.py
- Fixed Safety Manager auto-confirmation in tool_agent.py
- Added conversation history size limit in conversation_agent.py
- Improved health check accuracy in orchestrator.py
- Fixed Swift compilation issues in shared services

### Changed
- Updated version to 1.0.0 for production release
- Enhanced documentation with comprehensive AGENTS.md and BUG_FIXES.md
- Improved build process and deployment instructions