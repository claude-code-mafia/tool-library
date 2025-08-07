# b64img - Base64 to Binary Image Converter

A fast, lightweight CLI tool built with Bun that converts base64-encoded image data to binary files. Designed to work seamlessly with AI image generation tools (like GPT-Image-1 MCP servers) that return base64 data.

## Features

- 🚀 **Lightning Fast** - Built with Bun for optimal performance (~10ms startup, ~1GB/sec conversion)
- 🎯 **Smart Detection** - Automatically detects image formats (PNG, JPEG, WebP, GIF, AVIF, BMP, ICO)
- 🔄 **Flexible Input** - Accepts stdin, files, or command arguments
- 📦 **Batch Processing** - Convert multiple base64 images at once
- 🎨 **Format Preservation** - Maintains original image quality and format
- 📊 **Metadata Extraction** - Get image dimensions and format info as JSON
- 🔧 **Unix Philosophy** - Does one thing well, composable with other tools

## Installation

### Option 1: Using install-tool.sh (Recommended)
```bash
# From the tool-library directory
./install-tool.sh b64img
```

### Option 2: Manual Installation with Bun
```bash
# Install Bun if not already installed
curl -fsSL https://bun.sh/install | bash

# Run directly with Bun
bun run b64img.ts --help

# Or build standalone binary
./build.sh
```

### Option 3: Use with bunx (no installation)
```bash
bunx /path/to/b64img.ts input.b64
```

## Usage

### Basic Conversion
```bash
# From stdin
echo "iVBORw0KGgo..." | b64img output.png

# From file
b64img input.b64 -o output.png

# Auto-generate filename
cat gpt-output.txt | b64img --auto
# Creates: img-2024-01-07-123456.png
```

### Extract from Wrapped Formats
```bash
# Extract from data URL
echo "data:image/png;base64,iVBORw0KGgo..." | b64img --extract

# Extract from custom markers
echo "[BASE64_START]iVBORw0KGgo...[BASE64_END]" | b64img

# Multiple images with markers
echo "[BASE64_START_1]...[BASE64_END_1][BASE64_START_2]...[BASE64_END_2]" | b64img --outdir ./images/
```

### Batch Processing
```bash
# Convert all .b64 files in directory
b64img *.b64 --outdir ./images/

# Process multiple files
b64img file1.b64 file2.b64 file3.b64 --outdir ./output/
```

### Metadata and JSON Output
```bash
# Get image metadata as JSON
b64img input.b64 --json
# Output: { "format": "png", "size": 1234567, "dimensions": "1024x1024", "path": "output.png" }

# Metadata only (no file creation)
echo "iVBORw0KGgo..." | b64img --json
```

### Integration with Other Tools
```bash
# Pipe to image viewer
b64img input.b64 --stdout | open -f -a Preview

# Upload to cloud storage
b64img input.b64 --stdout | aws s3 cp - s3://bucket/image.png

# Chain with other tools
curl api.example.com/generate | b64img --auto | cf-images upload
```

## Command Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output FILE` | `-o` | Specify output filename |
| `--stdout` | | Output binary to stdout for piping |
| `--auto` | `-a` | Auto-generate filename with timestamp |
| `--extract` | `-e` | Extract base64 from wrappers (default: true) |
| `--json` | `-j` | Output metadata as JSON |
| `--outdir DIR` | `-d` | Output directory for batch processing |
| `--format FORMAT` | `-f` | Force output format (png, jpeg, webp, etc) |
| `--help` | `-h` | Show help message |

## Supported Formats

The tool automatically detects these image formats via magic bytes:
- **PNG** - Portable Network Graphics
- **JPEG/JPG** - Joint Photographic Experts Group
- **WebP** - Google's modern image format
- **GIF** - Graphics Interchange Format
- **AVIF** - AV1 Image File Format
- **BMP** - Bitmap Image File
- **ICO** - Icon format

## Performance

- **Startup Time**: ~10ms (compiled binary)
- **Conversion Speed**: ~1GB/sec on modern hardware
- **Memory Efficient**: Streams large images instead of loading entirely into memory
- **Binary Size**: ~15MB standalone executable

## Use Cases

### AI Image Generation Workflows
Many AI services return images as base64 strings. This tool bridges the gap:
```bash
# OpenAI DALL-E
curl -X POST https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{"prompt":"A sunset"}' | \
  jq -r '.data[0].b64_json' | \
  b64img --auto

# MCP Image Server
echo "generate sunset scene" | mcp-image-server | b64img --extract --auto
```

### CI/CD Pipelines
```bash
# Generate and save test images
for prompt in "test1" "test2" "test3"; do
  generate-image "$prompt" | b64img --outdir ./test-images/
done
```

### Web Scraping
```bash
# Extract embedded images from HTML
curl example.com | grep -o 'data:image/[^"]*' | while read dataurl; do
  echo "$dataurl" | b64img --extract --auto
done
```

## Error Handling

The tool provides clear error messages:
- Invalid base64 data
- Unknown image format
- File not found
- Write permission errors
- Malformed input data

Exit codes:
- `0` - Success
- `1` - Error occurred

## Development

### Prerequisites
- Bun 1.0+ (for development)
- TypeScript (included with Bun)

### Building from Source
```bash
# Clone and enter directory
cd b64img

# Install Bun (if needed)
curl -fsSL https://bun.sh/install | bash

# Run development version
bun run b64img.ts --help

# Build standalone binary
./build.sh

# Run tests
bun test
```

### Project Structure
```
b64img/
├── b64img.ts          # Main TypeScript source
├── build.sh           # Build script for binary
├── setup.sh           # Installation helper
├── README.md          # This file
├── CLAUDE.md          # AI assistant instructions
└── test/              # Test files
    └── samples/       # Sample base64 files
```

## Why This Tool?

Many AI image generation APIs return base64-encoded strings rather than URLs or files. This creates a gap in automation workflows. b64img solves this by:

1. **Converting** base64 to proper binary files
2. **Preserving** image quality and format
3. **Enabling** integration with storage services
4. **Following** Unix philosophy - do one thing well

## License

MIT

## Contributing

Contributions welcome! This tool follows the tool-library conventions:
- Keep it simple and focused
- Maintain backward compatibility
- Add tests for new features
- Update documentation

## Related Tools

- `cf-images` - Upload images to Cloudflare Images
- `upload-to-r2` - Upload to Cloudflare R2
- `image-gen` - Generate images with AI
- `aws s3` - Upload to Amazon S3