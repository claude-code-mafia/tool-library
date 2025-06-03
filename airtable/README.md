# Airtable CLI

Command-line interface for managing Airtable bases, tables, and records.

## Purpose

This tool provides a powerful CLI for interacting with Airtable, enabling you to:
- List and inspect bases and tables
- Create, read, update, and delete records
- Export data to CSV or JSON
- View table schemas
- Automate Airtable operations in scripts

## Installation

```bash
# From the tool-library directory
./install-tool.sh airtable
```

## Configuration

### API Key Setup

1. Get your personal access token from: https://airtable.com/create/tokens
2. Set the environment variable:
   ```bash
   export AIRTABLE_API_KEY='your-personal-access-token'
   ```
3. Add to your shell profile for persistence

### Token Permissions

When creating your token, ensure it has:
- `data.records:read` - To list and view records
- `data.records:write` - To create, update, delete records
- `schema.bases:read` - To view base and table schemas

## Usage

```bash
# List all accessible bases
airtable bases

# Show base details and tables
airtable base appXXXXXXXXXXXXXX

# List records from a table
airtable list appXXXXXXXXXXXXXX "Table Name"

# Get a specific record
airtable get appXXXXXXXXXXXXXX "Table Name" recXXXXXXXXXXXXXX

# Create a new record
airtable create appXXXXXXXXXXXXXX "Table Name" --data '{"Name": "John", "Email": "john@example.com"}'

# Update a record
airtable update appXXXXXXXXXXXXXX "Table Name" recXXXXXXXXXXXXXX --data '{"Status": "Active"}'

# Delete a record
airtable delete appXXXXXXXXXXXXXX "Table Name" recXXXXXXXXXXXXXX

# Show table schema
airtable schema appXXXXXXXXXXXXXX "Table Name"

# Export table data
airtable export appXXXXXXXXXXXXXX "Table Name" --output data.csv
airtable export appXXXXXXXXXXXXXX "Table Name" --output data.json
```

## Command Reference

### Global Options
- `--json` - Output in JSON format (available on all commands)
- `--token TOKEN` - Use specific token (overrides AIRTABLE_API_KEY)
- `--version` - Show version information
- `--help` - Show help message

### Commands

#### `bases`
List all accessible bases.
```bash
airtable bases
airtable bases --json
```

#### `base BASE_ID`
Show details about a specific base including all tables.
```bash
airtable base appXXXXXXXXXXXXXX
```

#### `list BASE_ID TABLE_NAME`
List records from a table with optional filtering.
```bash
# Basic listing
airtable list appXXXXXXXXXXXXXX "Contacts"

# With options
airtable list appXXXXXXXXXXXXXX "Contacts" --limit 10
airtable list appXXXXXXXXXXXXXX "Contacts" --view "Active Only"
airtable list appXXXXXXXXXXXXXX "Contacts" --sort "Name"
airtable list appXXXXXXXXXXXXXX "Contacts" --filter "Status=Active"
```

Options:
- `--limit N` - Maximum records to return
- `--view "View Name"` - Use a specific view
- `--sort "Field"` - Sort by field
- `--filter "field=value"` - Simple equality filter

#### `get BASE_ID TABLE_NAME RECORD_ID`
Get a specific record by ID.
```bash
airtable get appXXXXXXXXXXXXXX "Contacts" recXXXXXXXXXXXXXX
```

#### `create BASE_ID TABLE_NAME --data JSON`
Create a new record with field data.
```bash
airtable create appXXXXXXXXXXXXXX "Contacts" \
  --data '{"Name": "Jane Doe", "Email": "jane@example.com", "Status": "Active"}'
```

#### `update BASE_ID TABLE_NAME RECORD_ID --data JSON`
Update specific fields in a record.
```bash
airtable update appXXXXXXXXXXXXXX "Contacts" recXXXXXXXXXXXXXX \
  --data '{"Status": "Inactive", "Notes": "On vacation"}'
```

#### `delete BASE_ID TABLE_NAME RECORD_ID`
Delete a record (with confirmation).
```bash
airtable delete appXXXXXXXXXXXXXX "Contacts" recXXXXXXXXXXXXXX
airtable delete appXXXXXXXXXXXXXX "Contacts" recXXXXXXXXXXXXXX --force  # Skip confirmation
```

#### `schema BASE_ID TABLE_NAME`
Show detailed schema information for a table.
```bash
airtable schema appXXXXXXXXXXXXXX "Contacts"
```

#### `export BASE_ID TABLE_NAME`
Export all records from a table.
```bash
# Export to CSV
airtable export appXXXXXXXXXXXXXX "Contacts" --output contacts.csv

# Export to JSON
airtable export appXXXXXXXXXXXXXX "Contacts" --output contacts.json

# Output to stdout
airtable export appXXXXXXXXXXXXXX "Contacts" --format json
```

## Examples

### Finding Your Base ID
```bash
# List all bases to find the one you need
$ airtable bases
Found 3 bases:

ID: appABC123456789
Name: Marketing Database
Permission: create

ID: appDEF987654321
Name: Product Catalog
Permission: edit
```

### Working with Records
```bash
# List records with a filter
$ airtable list appABC123456789 "Campaigns" --filter "Status=Active"
Found 3 records:

ID: recXXX111
Created: 2024-01-15T10:30:00.000Z
Fields:
  Name: Spring Campaign
  Status: Active
  Budget: 50000

# Create a new record
$ airtable create appABC123456789 "Campaigns" \
    --data '{"Name": "Summer Sale", "Status": "Planning", "Budget": 75000}'
Record created successfully!
ID: recXXX222
...

# Update the record
$ airtable update appABC123456789 "Campaigns" recXXX222 \
    --data '{"Status": "Active"}'
Record updated successfully!
```

### Automation Examples

#### Backup a Table
```bash
#!/bin/bash
# Daily backup script
DATE=$(date +%Y%m%d)
airtable export appXXXXXXXXXXXXXX "Important Data" \
  --output "backup_${DATE}.json"
```

#### Process Records with jq
```bash
# Get all email addresses from active contacts
airtable list appXXXXXXXXXXXXXX "Contacts" --json | \
  jq -r '.[] | select(.fields.Status == "Active") | .fields.Email'
```

#### Bulk Import
```bash
# Read JSON file and create records
cat new_records.json | jq -c '.[]' | while read record; do
  airtable create appXXXXXXXXXXXXXX "Contacts" --data "$record"
  sleep 0.2  # Respect rate limits
done
```

## Output Formats

### Human-Readable (default)
```
ID: recXXXXXXXXXXXXXX
Created: 2024-01-15T10:30:00.000Z
Fields:
  Name: John Doe
  Email: john@example.com
  Status: Active
```

### JSON Format (--json)
```json
{
  "id": "recXXXXXXXXXXXXXX",
  "createdTime": "2024-01-15T10:30:00.000Z",
  "fields": {
    "Name": "John Doe",
    "Email": "john@example.com",
    "Status": "Active"
  }
}
```

## Error Handling

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | General error (API errors, network issues) |
| 2 | Invalid input (bad JSON, missing arguments) |

Common errors:
- **Missing API key**: Set AIRTABLE_API_KEY environment variable
- **Invalid base/table**: Check IDs with `airtable bases` and `airtable base BASE_ID`
- **Rate limit exceeded**: Tool includes automatic retry, but may still fail on heavy usage
- **Permission denied**: Ensure your token has required scopes

## Rate Limits

Airtable API limits:
- 5 requests per second per base
- The tool includes automatic retry logic for rate limit errors
- For bulk operations, consider adding delays between requests

## Technical Details

- **Language**: Python 3.6+
- **Dependencies**: pyairtable (handles retries and rate limiting)
- **API**: Uses Airtable Web API with Personal Access Tokens
- **Rate limiting**: Automatic retry with exponential backoff

## Security Notes

- Never commit your API key to version control
- Use personal access tokens instead of legacy API keys
- Limit token permissions to only what's needed
- Tokens inherit your user permissions - they cannot exceed what you can do in the UI

## Limitations

- Cannot modify table structure (use Airtable UI)
- Filter support is basic (single field equality only)
- No support for attachments or complex field types in CLI
- Rate limits cannot be increased even on paid plans