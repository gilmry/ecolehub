#!/bin/bash

# Script to generate video documentation for EcoleHub
# This script runs Playwright tests with video recording optimized for documentation

set -e

echo "🎬 Generating EcoleHub Video Documentation"
echo "=========================================="

# Create necessary directories
mkdir -p test-results/videos
mkdir -p test-results/screenshots
mkdir -p docs/videos

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Install Playwright browsers if not already installed
echo "📦 Installing Playwright browsers..."
npm install
npx playwright install

# Start the application
echo "🚀 Starting EcoleHub application..."
docker compose up -d

# Wait for application to be ready
echo "⏳ Waiting for application to be ready..."
sleep 15

# Check if application is accessible
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Application health check failed, but continuing anyway..."
fi

echo "🎥 Recording documentation videos..."

# Run documentation tests with video recording
npx playwright test --config=playwright-video-docs.config.ts e2e/documentation-flow.spec.ts

# Copy videos to documentation folder
echo "📁 Organizing documentation files..."
if [ -d "test-results/videos" ]; then
    cp test-results/videos/* docs/videos/ 2>/dev/null || echo "No videos found to copy"
fi

# Generate HTML report
echo "📊 Generating test report..."
npx playwright show-report --host=0.0.0.0 --port=9323 &
REPORT_PID=$!

echo ""
echo "✅ Video documentation generation complete!"
echo ""
echo "📂 Files generated:"
echo "   - Videos: test-results/videos/"
echo "   - Screenshots: test-results/screenshots/"
echo "   - Documentation videos: docs/videos/"
echo ""
echo "🌐 View HTML report at: http://localhost:9323"
echo "   (Report server PID: $REPORT_PID)"
echo ""
echo "💡 To stop the report server: kill $REPORT_PID"
echo "💡 To stop the application: docker compose down"
echo ""

# Save PID for cleanup
echo $REPORT_PID > .report-server.pid