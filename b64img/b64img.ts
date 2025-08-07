#!/usr/bin/env bun

import { parseArgs } from "util";
import { readFileSync, writeFileSync, existsSync, mkdirSync, statSync } from "fs";
import { basename, join, extname } from "path";
import { createHash } from "crypto";

interface ImageInfo {
  format: string;
  size: number;
  dimensions?: string;
  path?: string;
}

class B64ImgConverter {
  private readonly magicBytes = {
    png: [0x89, 0x50, 0x4e, 0x47],
    jpeg: [0xff, 0xd8, 0xff],
    webp: { offset: 8, bytes: [0x57, 0x45, 0x42, 0x50] },
    gif: [0x47, 0x49, 0x46],
    avif: { offset: 4, bytes: [0x66, 0x74, 0x79, 0x70] },
    bmp: [0x42, 0x4d],
    ico: [0x00, 0x00, 0x01, 0x00],
  };

  private detectFormat(buffer: Buffer): string {
    // PNG
    if (this.matchBytes(buffer, this.magicBytes.png, 0)) return "png";
    
    // JPEG
    if (this.matchBytes(buffer, this.magicBytes.jpeg, 0)) return "jpeg";
    
    // WebP
    if (this.matchBytes(buffer, this.magicBytes.webp.bytes, this.magicBytes.webp.offset)) return "webp";
    
    // GIF
    if (this.matchBytes(buffer, this.magicBytes.gif, 0)) return "gif";
    
    // AVIF
    if (this.matchBytes(buffer, this.magicBytes.avif.bytes, this.magicBytes.avif.offset)) {
      const brand = buffer.slice(8, 12).toString();
      if (brand === "avif" || brand === "avis") return "avif";
    }
    
    // BMP
    if (this.matchBytes(buffer, this.magicBytes.bmp, 0)) return "bmp";
    
    // ICO
    if (this.matchBytes(buffer, this.magicBytes.ico, 0)) return "ico";
    
    return "unknown";
  }

  private matchBytes(buffer: Buffer, bytes: number[], offset = 0): boolean {
    if (buffer.length < offset + bytes.length) return false;
    return bytes.every((byte, i) => buffer[offset + i] === byte);
  }

  private extractBase64(input: string): string[] {
    const results: string[] = [];
    
    // Remove whitespace and newlines
    input = input.replace(/\s+/g, "");
    
    // Pattern 1: data URL format
    const dataUrlPattern = /data:image\/[^;]+;base64,([A-Za-z0-9+/]+=*)/g;
    let match;
    while ((match = dataUrlPattern.exec(input)) !== null) {
      results.push(match[1]);
    }
    
    // Pattern 2: Custom markers [BASE64_START]...[BASE64_END]
    const markerPattern = /\[BASE64_START(?:_\d+)?\]([A-Za-z0-9+/]+=*)\[BASE64_END(?:_\d+)?\]/g;
    while ((match = markerPattern.exec(input)) !== null) {
      results.push(match[1]);
    }
    
    // If no patterns found, assume the entire input is base64
    if (results.length === 0) {
      // Basic validation: check if it looks like base64
      const cleanInput = input.replace(/[^A-Za-z0-9+/=]/g, "");
      if (cleanInput.length > 0 && cleanInput.length % 4 === 0) {
        results.push(cleanInput);
      }
    }
    
    return results;
  }

  private getDimensions(buffer: Buffer, format: string): string | undefined {
    try {
      switch (format) {
        case "png": {
          if (buffer.length < 24) return undefined;
          const width = buffer.readUInt32BE(16);
          const height = buffer.readUInt32BE(20);
          return `${width}x${height}`;
        }
        case "jpeg": {
          // JPEG dimension extraction is complex, skip for now
          return undefined;
        }
        case "gif": {
          if (buffer.length < 10) return undefined;
          const width = buffer.readUInt16LE(6);
          const height = buffer.readUInt16LE(8);
          return `${width}x${height}`;
        }
        case "webp": {
          // WebP dimension extraction is complex, skip for now
          return undefined;
        }
        case "bmp": {
          if (buffer.length < 26) return undefined;
          const width = buffer.readInt32LE(18);
          const height = Math.abs(buffer.readInt32LE(22));
          return `${width}x${height}`;
        }
        default:
          return undefined;
      }
    } catch {
      return undefined;
    }
  }

  private generateFilename(format: string, index?: number): string {
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, -5);
    const suffix = index !== undefined ? `-${index}` : "";
    return `img-${timestamp}${suffix}.${format}`;
  }

  async processInput(
    input: string | Buffer,
    options: {
      output?: string;
      stdout?: boolean;
      auto?: boolean;
      extract?: boolean;
      json?: boolean;
      outdir?: string;
      format?: string;
      quality?: number;
    }
  ): Promise<ImageInfo[]> {
    const results: ImageInfo[] = [];
    
    // Convert input to string if it's a buffer
    const inputStr = input instanceof Buffer ? input.toString() : input;
    
    // Extract base64 strings
    const base64Strings = options.extract !== false 
      ? this.extractBase64(inputStr)
      : [inputStr.replace(/\s+/g, "")];
    
    if (base64Strings.length === 0) {
      throw new Error("No valid base64 data found");
    }
    
    // Process each base64 string
    for (let i = 0; i < base64Strings.length; i++) {
      const base64 = base64Strings[i];
      
      // Decode base64
      let buffer: Buffer;
      try {
        buffer = Buffer.from(base64, "base64");
      } catch (err) {
        throw new Error(`Invalid base64 data at position ${i + 1}: ${err}`);
      }
      
      // Detect format
      const detectedFormat = this.detectFormat(buffer);
      if (detectedFormat === "unknown" && !options.format) {
        throw new Error(`Unknown image format at position ${i + 1}`);
      }
      
      const format = options.format || detectedFormat;
      
      // Prepare image info
      const info: ImageInfo = {
        format,
        size: buffer.length,
        dimensions: this.getDimensions(buffer, detectedFormat),
      };
      
      // Handle output
      if (options.stdout && base64Strings.length === 1) {
        // Write to stdout (only for single images)
        process.stdout.write(buffer);
      } else if (options.json) {
        // JSON output only, no file writing
        results.push(info);
      } else {
        // Determine output path
        let outputPath: string;
        
        if (options.outdir) {
          // Batch output to directory
          if (!existsSync(options.outdir)) {
            mkdirSync(options.outdir, { recursive: true });
          }
          outputPath = join(options.outdir, this.generateFilename(format, i));
        } else if (options.output && base64Strings.length === 1) {
          // Single file with specified name
          outputPath = options.output;
        } else if (options.auto || base64Strings.length > 1) {
          // Auto-generate filename
          outputPath = this.generateFilename(format, base64Strings.length > 1 ? i : undefined);
        } else {
          outputPath = options.output || this.generateFilename(format);
        }
        
        // Write file
        writeFileSync(outputPath, buffer);
        info.path = outputPath;
        results.push(info);
        
        if (!options.json) {
          console.log(outputPath);
        }
      }
    }
    
    if (options.json) {
      console.log(JSON.stringify(results.length === 1 ? results[0] : results, null, 2));
    }
    
    return results;
  }

  async processFile(filePath: string, options: any): Promise<ImageInfo[]> {
    if (!existsSync(filePath)) {
      throw new Error(`File not found: ${filePath}`);
    }
    
    const content = readFileSync(filePath, "utf8");
    return this.processInput(content, options);
  }

  async processStdin(options: any): Promise<ImageInfo[]> {
    const chunks: Buffer[] = [];
    
    for await (const chunk of Bun.stdin.stream()) {
      chunks.push(Buffer.from(chunk));
    }
    
    const input = Buffer.concat(chunks);
    return this.processInput(input, options);
  }
}

async function main() {
  const { values, positionals } = parseArgs({
    args: Bun.argv.slice(2),
    options: {
      output: { type: "string", short: "o" },
      stdout: { type: "boolean" },
      auto: { type: "boolean", short: "a" },
      extract: { type: "boolean", short: "e" },
      json: { type: "boolean", short: "j" },
      outdir: { type: "string", short: "d" },
      format: { type: "string", short: "f" },
      quality: { type: "string", short: "q" },
      help: { type: "boolean", short: "h" },
    },
    strict: false,
    allowPositionals: true,
  });

  if (values.help) {
    console.log(`b64img - Convert base64 encoded images to binary files

Usage:
  b64img [options] [input-file ...]
  echo "base64-data" | b64img [options]
  
Options:
  -o, --output FILE    Output filename (single file mode)
  --stdout            Output binary to stdout
  -a, --auto          Auto-generate filename
  -e, --extract       Extract base64 from wrappers (default: true)
  -j, --json          Output metadata as JSON
  -d, --outdir DIR    Output directory for batch processing
  -f, --format FORMAT Force output format (png, jpeg, webp, etc)
  -q, --quality NUM   JPEG/WebP quality (1-100)
  -h, --help          Show this help

Examples:
  echo "iVBORw0KGgo..." | b64img output.png
  cat image.b64 | b64img --auto
  b64img input.txt --extract --outdir ./images/
  echo "[BASE64_START]iVBOR...[BASE64_END]" | b64img --extract
  b64img file.b64 --json > metadata.json`);
    process.exit(0);
  }

  const converter = new B64ImgConverter();
  
  try {
    const options = {
      output: values.output as string,
      stdout: values.stdout as boolean,
      auto: values.auto as boolean,
      extract: values.extract !== false, // Default true
      json: values.json as boolean,
      outdir: values.outdir as string,
      format: values.format as string,
      quality: values.quality ? parseInt(values.quality as string) : undefined,
    };

    if (positionals.length > 0) {
      // Process files
      for (const file of positionals) {
        // Check if it's a glob pattern
        if (file.includes("*")) {
          const glob = new Bun.Glob(file);
          for await (const path of glob.scan()) {
            await converter.processFile(path, options);
          }
        } else {
          await converter.processFile(file, options);
        }
      }
    } else {
      // Process stdin
      await converter.processStdin(options);
    }
  } catch (error) {
    console.error(`Error: ${error}`);
    process.exit(1);
  }
}

// Run if executed directly
if (import.meta.main) {
  main();
}

export { B64ImgConverter, ImageInfo };