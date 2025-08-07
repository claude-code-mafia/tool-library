#!/bin/bash
set -e

echo "Setting up b64img..."

# Check if Bun is installed
if ! command -v bun &> /dev/null; then
    echo "Bun is not installed. Installing Bun..."
    curl -fsSL https://bun.sh/install | bash
    
    # Add Bun to PATH for current session
    export BUN_INSTALL="$HOME/.bun"
    export PATH="$BUN_INSTALL/bin:$PATH"
    
    echo "Bun installed successfully!"
else
    echo "Bun is already installed: $(bun --version)"
fi

# Make the TypeScript file executable
chmod +x b64img.ts

# Create a simple wrapper that uses Bun
cat > b64img << 'EOF'
#!/bin/bash
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the TypeScript file with Bun
exec bun run "$SCRIPT_DIR/b64img.ts" "$@"
EOF

chmod +x b64img

echo "Setup complete!"
echo ""
echo "You can now run b64img using:"
echo "  ./b64img --help"
echo ""
echo "To build a standalone binary (no Bun required at runtime):"
echo "  ./build.sh"