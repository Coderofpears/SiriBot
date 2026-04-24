# GitHub Release Workflow for SiriBot
# This file provides instructions for creating releases

## Quick Release Process

### Option 1: Using GitHub Web Interface
1. Go to https://github.com/Coderofpears/SiriBot/releases
2. Click "Draft a new release"
3. Enter version tag (e.g., v1.0.0)
4. Add release notes
5. Upload the DMG files from `build/` folder
6. Click "Publish release"

### Option 2: Using GitHub CLI
```bash
# Create a tag
git tag v1.0.0
git push origin v1.0.0

# This will trigger the release workflow automatically
```

## Version Numbering

Follow semver: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

## Release Checklist

- [ ] Update version in project.yml files
- [ ] Update CHANGELOG.md
- [ ] Update README.md if needed
- [ ] Build DMGs locally to test
- [ ] Create release notes
- [ ] Test the DMG on a clean machine

## After Release

The workflow will:
1. Build both apps
2. Create DMG installers
3. Upload to GitHub releases
4. Send notification (if configured)