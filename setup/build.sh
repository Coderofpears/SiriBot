#!/bin/bash
set -e

echo "🔧 Building SiriBot..."

# Check for XcodeGen
if ! command -v xcodegen &> /dev/null; then
    echo "Installing XcodeGen..."
    brew install xcodegen
fi

# Build main app
echo "Building SiriBot.app..."
cd macos/SiriBot
xcodegen generate
xcodebuild -scheme SiriBot -configuration Release build
cd ../..

# Build studio app
echo "Building SiriBotStudio.app..."
cd studio/SiriBotStudio
xcodegen generate
xcodebuild -scheme SiriBotStudio -configuration Release build
cd ../..

echo "✅ Build complete!"
echo ""
echo "To run SiriBot:"
echo "  open macos/build/Release/SiriBot.app"
echo ""
echo "To run SiriBot Studio:"
echo "  open studio/build/Release/SiriBotStudio.app"
