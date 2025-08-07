#!/bin/bash
set -e

echo "🚀 Setting up GPT-Image-Gen..."

# Check if Bun is installed
if ! command -v bun &> /dev/null; then
    echo "Bun is not installed. Installing Bun..."
    curl -fsSL https://bun.sh/install | bash
    
    # Add Bun to PATH for current session
    export BUN_INSTALL="$HOME/.bun"
    export PATH="$BUN_INSTALL/bin:$PATH"
    
    echo "✅ Bun installed successfully!"
else
    echo "✅ Bun is already installed: $(bun --version)"
fi

# Make CLI executable
chmod +x src/cli.ts

# Create a development wrapper that uses Bun
cat > gpt-image-gen << 'EOF'
#!/bin/bash
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Add Bun to PATH if it exists
if [ -d "$HOME/.bun/bin" ]; then
    export PATH="$HOME/.bun/bin:$PATH"
fi

# Check if running from source or compiled
if [ -f "$SCRIPT_DIR/src/cli.ts" ]; then
    # Run from source with Bun
    exec bun run "$SCRIPT_DIR/src/cli.ts" "$@"
else
    # This shouldn't happen in dev, but handle it
    echo "Error: src/cli.ts not found"
    exit 1
fi
EOF

chmod +x gpt-image-gen

echo ""
echo "✅ Setup complete!"
echo ""
echo "You can now run the tool in development mode:"
echo "  ./gpt-image-gen --help"
echo ""
echo "To build a standalone binary:"
echo "  ./build.sh"
echo ""
echo "To install globally:"
echo "  cd .. && ./install-tool.sh gpt-image-gen"
echo ""
echo "⚠️  Remember to set your OpenAI API key:"
echo "  export OPENAI_API_KEY=sk-..."
echo "  OR"
echo "  ./gpt-image-gen config set api-key sk-..."