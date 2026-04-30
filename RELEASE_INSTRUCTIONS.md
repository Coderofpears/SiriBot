# SiriBot v1.0.0 Release Instructions

This document provides step-by-step instructions for creating the first production release of SiriBot.

## Prerequisites

1. macOS 14.0+ with Xcode 15.0+ installed
2. GitHub account with write access to the repository
3. GitHub CLI installed (or ability to use GitHub web interface)
4. Ollama installed for local AI processing

## Release Steps

### 1. Verify Code Changes

All necessary changes have been committed to the repository:
- Bug fixes in Python agents and memory management
- Swift compilation issues resolved
- Version updated to 1.0.0
- Comprehensive documentation added
- Build scripts updated

### 2. Create GitHub Release (Web Interface)

1. Go to https://github.com/Coderofpears/SiriBot/releases
2. Click "Draft a new release"
3. Set the tag to `v1.0.0`
4. Set the release title to `v1.0.0 - First Production Release`
5. Copy the content from `RELEASE_NOTES.md` into the description
6. Upload the built DMG files (when built successfully)
7. Click "Publish release"

### 3. Build Process (For maintainers with Xcode)

If you have Xcode installed, you can build the DMG installers:

```bash
# Build main app DMG
./setup/build_dmg.sh

# Build studio DMG
./setup/build_studio_dmg.sh
```

The built DMG files will be located in the `build/` directory.

### 4. Manual Build Process (Alternative)

If Xcode is not available, you can manually create the app bundle:

1. Generate Xcode project:
   ```bash
   cd macos/SiriBot
   ../xcodegen generate
   ```

2. Build using Xcode:
   - Open `SiriBot.xcodeproj` in Xcode
   - Select "Release" configuration
   - Build the project
   - Create an app bundle

3. Create DMG manually:
   ```bash
   # Create staging directory
   mkdir -p build/staging
   
   # Copy app bundle to staging
   cp -R /path/to/built/SiriBot.app build/staging/
   
   # Create Applications symlink
   ln -sf /Applications build/staging/Applications
   
   # Copy documentation
   cp README.md build/staging/README.txt
   
   # Create DMG
   hdiutil create -volname "SiriBot-1.0.0" -srcfolder build/staging -ov -format UDZO build/SiriBot-1.0.0.dmg
   ```

## Post-Release Activities

### 1. Announce the Release
- Share on social media (Twitter, LinkedIn, Reddit)
- Post in relevant macOS/AI communities
- Update project website if applicable

### 2. Monitor Feedback
- Watch GitHub Issues for bug reports
- Respond to user feedback promptly
- Track download statistics

### 3. Plan Next Steps
- Review user feedback for feature requests
- Prioritize bug fixes for next release
- Consider roadmap for v1.1.0

## Troubleshooting

### Build Issues
- Ensure Xcode command line tools are installed: `xcode-select --install`
- Verify Xcode is properly installed and selected: `xcode-select -p`
- Check that all dependencies are installed

### Swift Compilation Issues
- Ensure all Swift files have proper imports
- Verify Codable compliance for data structures
- Check for circular dependencies between services

### Python Issues
- Ensure Python 3.12+ is installed
- Install dependencies: `pip install -r requirements.txt`
- Verify Ollama is running: `ollama serve`

## Release Assets

The following assets should be included in the release:

1. `SiriBot-1.0.0.dmg` - Main application installer
2. `SiriBotStudio-1.0.0.dmg` - Development studio installer (optional)
3. `RELEASE_NOTES.md` - Detailed release information
4. `CHANGELOG.md` - Complete version history

## Documentation Updates

Ensure all documentation is up-to-date:
- `README.md` - Project overview and quick start guide
- `AGENTS.md` - Developer guide for future contributors
- `BUG_FIXES.md` - Summary of bugs fixed in this release
- `CLAUDE.md` - Instructions for AI assistants working with the codebase

This completes the release process for SiriBot v1.0.0!