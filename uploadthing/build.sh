#!/bin/bash
set -euo pipefail

if ! command -v bun >/dev/null 2>&1; then
  echo "Error: Bun is not installed. Install from https://bun.sh" >&2
  exit 1
fi

echo "Building uploadthing standalone binary..."
cd "$(dirname "$0")"

bun build ./uploadthing.ts --compile --outfile uploadthing
chmod +x uploadthing

echo "Done: ./uploadthing"
