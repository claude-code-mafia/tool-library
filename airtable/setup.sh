#!/bin/bash
# Setup script for Airtable CLI

echo "Setting up Airtable CLI..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To use the Airtable CLI, you need to set your API key:"
echo "  export AIRTABLE_API_KEY='your-personal-access-token'"
echo ""
echo "Get your token from: https://airtable.com/create/tokens"