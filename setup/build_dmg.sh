#!/bin/bash
# SiriBot DMG Builder - Creates a distributable DMG for macOS
set -e

APP_NAME="SiriBot"
VERSION="1.0.0"
DMG_NAME="SiriBot-${VERSION}"
BUILD_DIR="build/dmg"
STAGING_DIR="build/staging"

echo "🔨 Building ${APP_NAME} DMG..."

# Clean previous builds
rm -rf "${BUILD_DIR}" "${STAGING_DIR}"
mkdir -p "${STAGING_DIR}"

# Build the app
cd macos/SiriBot
xcodegen generate
xcodebuild -scheme ${APP_NAME} -configuration Release build OBJROOT="${BUILD_DIR}/obj" SYMROOT="${BUILD_DIR}/sym" DSTROOT="${STAGING_DIR}" CODE_SIGN_IDENTITY="-" CODE_SIGNING_REQUIRED=NO CODE_SIGNING_ALLOWED=NO

# Copy app to staging
cp -R "${STAGING_DIR}/Applications/${APP_NAME}.app" "${STAGING_DIR}/"

# Create Applications link
ln -sf "/Applications" "${STAGING_DIR}/Applications"

# Copy README
cp README.md "${STAGING_DIR}/README.txt"
cp setup/quickstart.py "${STAGING_DIR}/Setup.py"

# Create DMG
hdiutil create -volname "${DMG_NAME}" -srcfolder "${STAGING_DIR}" -ov -format UDZO "build/${DMG_NAME}.dmg"

echo "✅ Created: build/${DMG_NAME}.dmg"
echo ""
echo "To install:"
echo "  open build/${DMG_NAME}.dmg"
echo "  Drag SiriBot.app to Applications"