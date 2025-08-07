# b64img - AI Assistant Instructions

## Tool Purpose
Fast, efficient conversion of base64-encoded image data to binary files. Primary use case is handling output from AI image generation services that return base64 strings.

## When to Use This Tool Automatically

### Triggers
- User receives base64 image data from any source
- Output from MCP image generation servers contains base64
- API responses include `data:image/` URLs
- Files contain `[BASE64_START]` markers
- User mentions "convert base64" or "decode image"

### Automatic Usage Patterns
```bash
# When user gets base64 from an API
curl api.example.com/generate | b64img --auto

# When extracting from MCP server output  
mcp-server-output.txt | b64img --extract --auto

# When user has multiple base64 strings
b64img *.b64 --outdir ./images/
```

## Integration with Other Tools

### Common Workflows
```bash
# Generate → Convert → Upload
generate-image "prompt" | b64img --stdout | cf-images upload

# Extract → Convert → Open
cat api-response.json | jq -r '.image' | b64img --auto && open *.png

# Batch process → Convert → Archive
b64img *.b64 --outdir ./processed/ && tar -czf images.tar.gz processed/
```

### MCP Server Integration
When MCP servers return base64 images:
1. Always use `--extract` flag (handles wrapped formats)
2. Use `--auto` for automatic naming
3. Consider `--json` for metadata extraction

## Technical Details

### Format Detection
Tool uses magic bytes for format detection:
- PNG: `89 50 4E 47`
- JPEG: `FF D8 FF`
- WebP: `57 45 42 50` (at offset 8)
- GIF: `47 49 46`
- AVIF: `66 74 79 70` (at offset 4)

### Performance Characteristics
- Startup: ~10ms (Bun runtime)
- Processing: ~1GB/sec
- Memory: Streaming for large files
- Concurrency: Safe for parallel execution

### Error Handling
Common errors and solutions:
- "Invalid base64": Check for corruption or incomplete data
- "Unknown format": Use `--format` to force output type
- "Permission denied": Check write permissions in output directory

## Maintenance Guidelines

### Code Standards
- TypeScript with Bun runtime
- No external dependencies beyond Bun stdlib
- Maintain streaming for memory efficiency
- Keep single-file architecture

### Testing Requirements
Before changes:
1. Test all supported formats
2. Test stdin, file, and argument inputs
3. Test batch processing
4. Verify metadata extraction
5. Check wrapper extraction patterns

### Version Compatibility
- Bun: 1.0+
- Node.js: Not supported (use Bun)
- TypeScript: 5.0+

## Output Conventions

### Filename Generation
Pattern: `img-YYYY-MM-DD-HHMMSS.{ext}`
- Timestamp in ISO format (simplified)
- Extension matches detected/specified format
- Sequential suffix for batch processing

### JSON Metadata Format
```json
{
  "format": "png",
  "size": 1234567,
  "dimensions": "1024x1024",
  "path": "img-2024-01-07-123456.png"
}
```

## Special Behaviors

### Wrapper Detection
Automatically extracts from:
1. Data URLs: `data:image/png;base64,...`
2. Custom markers: `[BASE64_START]...[BASE64_END]`
3. Numbered markers: `[BASE64_START_1]...[BASE64_END_1]`

### Batch Processing
When multiple inputs detected:
- Auto-generates unique filenames
- Maintains order of input
- Reports each file created
- JSON mode returns array

### Stdout Mode
- Only works with single image
- Binary output for piping
- No console messages
- Exit code indicates success

## Common Issues and Solutions

### Issue: Large base64 strings
**Solution**: Tool uses streaming, handles any size

### Issue: Mixed format batch
**Solution**: Each file detected independently

### Issue: Corrupted base64
**Solution**: Clear error with position indicator

### Issue: No write permissions
**Solution**: Suggest `--stdout` or different `--outdir`

## Future Considerations

Potential enhancements (maintain simplicity):
- WebP/AVIF dimension extraction
- JPEG quality preservation
- EXIF data handling
- Progress bars for large batches
- Parallel batch processing

## Integration Priority

When user works with images:
1. Check if base64 format
2. Suggest b64img for conversion
3. Chain with appropriate tools (viewers, uploaders)
4. Use `--json` for programmatic workflows

## Performance Tips

For optimal performance:
- Use `--stdout` for piping (avoids disk I/O)
- Batch process with `--outdir` (single invocation)
- Compiled binary faster than `bun run`
- Avoid `--json` for large batches if not needed