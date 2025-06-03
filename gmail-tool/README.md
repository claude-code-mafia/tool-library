# Gmail CLI Tool

A comprehensive command-line interface for Gmail that leverages the full capabilities of the Gmail API.

## Purpose

This tool provides complete Gmail functionality from the command line, including:
- Reading, sending, and searching emails
- Managing labels and filters
- Batch operations for efficiency
- Push notifications setup
- Full OAuth 2.0 authentication (required as of Sept 2024)

## Setup

### 1. Google Cloud Console Setup
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the credentials JSON file

### 2. Install Tool
```bash
# Install dependencies
pip install -r requirements.txt

# Create config directory
mkdir -p ~/.gmail-cli

# Move credentials file
mv ~/Downloads/credentials.json ~/.gmail-cli/credentials.json

# Make script executable
chmod +x gmail_cli.py
```

### 3. First Run
```bash
./gmail_cli.py list
# This will open a browser for OAuth authentication
# Grant permissions and the tool will save tokens for future use
```

## Usage

### List Messages
```bash
# List recent messages
./gmail_cli.py list

# Search with query
./gmail_cli.py list -q "from:example@gmail.com"
./gmail_cli.py list -q "is:unread label:important"
./gmail_cli.py list -q "has:attachment after:2024/12/1"

# List more messages
./gmail_cli.py list -n 50

# Include spam/trash
./gmail_cli.py list --include-spam-trash
```

### Read Messages
```bash
# Read full message
./gmail_cli.py read MESSAGE_ID

# Read metadata only
./gmail_cli.py read MESSAGE_ID --format metadata

# Get raw message
./gmail_cli.py read MESSAGE_ID --format raw
```

### Send Messages
```bash
# Simple message
./gmail_cli.py send "user@example.com" "Subject" "Message body"

# With attachments
./gmail_cli.py send "user@example.com" "Report" "Please find attached" -a report.pdf -a data.csv
```

### Manage Labels
```bash
# List all labels
./gmail_cli.py labels list

# Create new label
./gmail_cli.py labels create "Projects/ClientA"

# Apply label to message
./gmail_cli.py labels apply MESSAGE_ID "Projects/ClientA"
```

### Delete/Trash Messages
```bash
# Move to trash (recoverable)
./gmail_cli.py trash MESSAGE_ID

# Permanent delete (use with caution!)
./gmail_cli.py delete MESSAGE_ID

# Batch delete multiple messages
./gmail_cli.py batch-delete MSG_ID1 MSG_ID2 MSG_ID3
```

### Filters
```bash
# List all filters
./gmail_cli.py filters list
```

### Push Notifications
```bash
# Set up push notifications (requires Pub/Sub topic)
./gmail_cli.py watch "projects/myproject/topics/gmail-push"

# Watch specific labels
./gmail_cli.py watch "projects/myproject/topics/gmail-push" -l INBOX IMPORTANT
```

## Output Examples

### List Output
```
ID: 18d5a2b3c4d5e6f7
From: John Doe <john@example.com>
To: you@gmail.com
Subject: Meeting Tomorrow
Date: Mon, 1 Jan 2025 10:30:00 -0800
Labels: UNREAD, INBOX, IMPORTANT
--------------------------------------------------
```

### Filter Output
```
Filter ID: ANe1BmhgK2x...
  Criteria: {
    "from": "notifications@github.com"
  }
  Action: {
    "addLabelIds": ["Label_123"],
    "removeLabelIds": ["INBOX"]
  }
--------------------------------------------------
```

## Configuration

- **Config Directory**: `~/.gmail-cli/`
- **Credentials**: `~/.gmail-cli/credentials.json` (OAuth client config)
- **Token Storage**: `~/.gmail-cli/token.pickle` (saved authentication)

## Technical Details

### Dependencies
- `google-api-python-client`: Official Gmail API client
- `google-auth-oauthlib`: OAuth 2.0 authentication flow
- Python 3.6+

### API Usage
- Uses Gmail API v1
- Implements batch operations for efficiency
- Supports all Gmail scopes for full functionality

### Rate Limits
- 250 quota units per user per second
- 1 billion quota units per day
- Batch operations reduce quota usage

### Security
- OAuth 2.0 authentication (mandatory)
- Tokens stored locally with pickle
- No passwords stored
- Refresh tokens handled automatically

## Common Search Queries

- `is:unread` - Unread messages
- `from:user@example.com` - From specific sender
- `to:me` - Sent directly to you
- `subject:invoice` - Subject contains word
- `has:attachment` - Messages with attachments
- `filename:pdf` - Specific attachment types
- `after:2024/12/1 before:2024/12/31` - Date range
- `label:work -label:done` - Label combinations
- `larger:10M` - Size filters
- `in:anywhere` - Search all folders

## Error Handling

The tool provides clear error messages for common issues:
- Missing credentials file
- Invalid OAuth tokens
- API quota exceeded
- Network connectivity issues
- Invalid message IDs

## Future Enhancements

Planned features:
- Interactive mode with message threading
- Template system for common replies
- Offline cache for metadata
- Export to various formats (mbox, PST)
- Advanced filter creation UI
- Keyboard shortcuts in interactive mode