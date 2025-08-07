#!/bin/bash
set -e

echo "🔨 Building GPT-Image-Gen CLI..."

# Check if bun is installed
if ! command -v bun &> /dev/null; then
    echo "Error: Bun is not installed. Please install Bun first."
    echo "Run: curl -fsSL https://bun.sh/install | bash"
    exit 1
fi

# Build the standalone binary
echo "Compiling TypeScript to standalone binary..."
bun build --compile --minify ./src/cli.ts --outfile gpt-image-gen

# Make it executable
chmod +x gpt-image-gen

echo "✅ Build complete!"
echo ""
echo "Binary created: ./gpt-image-gen"
echo ""
echo "To build for all platforms, run:"
echo "  bun run build.ts"
echo ""
echo "To install globally, run:"
echo "  cd .. && ./install-tool.sh gpt-image-gen"