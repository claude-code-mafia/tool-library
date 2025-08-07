#!/bin/bash
set -e

echo "Building b64img standalone binary..."

# Check if bun is installed
if ! command -v bun &> /dev/null; then
    echo "Error: Bun is not installed. Please install Bun first."
    echo "Run: curl -fsSL https://bun.sh/install | bash"
    exit 1
fi

# Build the standalone binary
bun build ./b64img.ts --compile --outfile b64img

# Make it executable
chmod +x b64img

echo "Build complete! Binary created: ./b64img"
echo ""
echo "To install globally, run:"
echo "  sudo mv ./b64img /usr/local/bin/"
echo ""
echo "Or use the install-tool.sh script from the parent directory:"
echo "  cd .. && ./install-tool.sh b64img"