#!/bin/bash
# SiriBot Studio DMG Builder
set -e

APP_NAME="SiriBotStudio"
VERSION="1.0.0"
DMG_NAME="SiriBotStudio-${VERSION}"
BUILD_DIR="build/dmg"
STAGING_DIR="build/staging"

echo "🔨 Building ${APP_NAME} DMG..."

rm -rf "${BUILD_DIR}" "${STAGING_DIR}"
mkdir -p "${STAGING_DIR}"

cd studio/SiriBotStudio
xcodegen generate
xcodebuild -scheme ${APP_NAME} -configuration Release build OBJROOT="${BUILD_DIR}/obj" SYMROOT="${BUILD_DIR}/sym" DSTROOT="${STAGING_DIR}" CODE_SIGN_IDENTITY="-" CODE_SIGNING_REQUIRED=NO CODE_SIGNING_ALLOWED=NO

cp -R "${STAGING_DIR}/Applications/${APP_NAME}.app" "${STAGING_DIR}/"
ln -sf "/Applications" "${STAGING_DIR}/Applications"
cp README.md "${STAGING_DIR}/README.txt"

hdiutil create -volname "${DMG_NAME}" -srcfolder "${STAGING_DIR}" -ov -format UDZO "build/${DMG_NAME}.dmg"

echo "✅ Created: build/${DMG_NAME}.dmg"