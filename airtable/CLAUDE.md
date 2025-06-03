# Airtable CLI - AI Instructions

## When to Use This Tool

### Automatic Usage Triggers
- User mentions "Airtable" operations
- Tasks involve spreadsheet-like data management
- Need to sync or export Airtable data
- Automating record creation/updates
- Bulk operations on Airtable bases

### Example User Requests
- "List all records in my Airtable"
- "Create a new entry in Airtable"
- "Export Airtable data to CSV"
- "Update the status field in Airtable"
- "Show me what's in this base"

## Important Setup Requirement

**ALWAYS check for API key first:**
```bash
# This will fail if AIRTABLE_API_KEY is not set
airtable bases --json
```

If it fails, instruct user to:
1. Get token from https://airtable.com/create/tokens
2. Set: `export AIRTABLE_API_KEY='token'`

## Usage Patterns

### Discovery Flow
When user asks about Airtable without specifics:
```bash
# 1. First, list their bases
airtable bases --json

# 2. Show tables in a base
airtable base BASE_ID --json

# 3. List records from a table
airtable list BASE_ID "Table Name" --json
```

### Record Operations
```bash
# Always use --json for reliable parsing
airtable get BASE_ID "Table Name" RECORD_ID --json

# Create with proper JSON escaping
airtable create BASE_ID "Table Name" --data '{"Field": "Value"}' --json

# Update specific fields only
airtable update BASE_ID "Table Name" RECORD_ID --data '{"Status": "Done"}' --json

# Delete with --force to skip confirmation in scripts
airtable delete BASE_ID "Table Name" RECORD_ID --force --json
```

### Common Workflows

#### Finding Records
```bash
# List with filtering
airtable list BASE_ID "Contacts" --filter "Status=Active" --json

# Process with jq
airtable list BASE_ID "Tasks" --json | \
  jq '.[] | select(.fields.Priority == "High")'
```

#### Bulk Operations
```bash
# Export all data
airtable export BASE_ID "Table Name" --output backup.json

# Create multiple records
for record in records_*.json; do
  airtable create BASE_ID "Table Name" --data "@$record" --json
  sleep 0.2  # Respect rate limits
done
```

#### Data Sync
```bash
# Export from one base
airtable export BASE_ID_1 "Source Table" --output temp.json

# Import to another (with processing)
cat temp.json | jq -c '.[] | .fields' | while read fields; do
  airtable create BASE_ID_2 "Dest Table" --data "$fields" --json
done
```

## Output Parsing

### JSON Structure
```json
{
  "id": "recXXXXXXXXXXXXXX",
  "createdTime": "2024-01-15T10:30:00.000Z",
  "fields": {
    "Name": "Example",
    "Status": "Active",
    "Count": 42
  }
}
```

### Parsing Examples
```python
# Python
import subprocess
import json

result = subprocess.run(
    ['airtable', 'list', base_id, table_name, '--json'],
    capture_output=True, text=True
)
records = json.loads(result.stdout)
for record in records:
    print(f"{record['id']}: {record['fields'].get('Name', 'Unnamed')}")
```

## Error Handling

### Common Errors and Solutions

1. **No API Key**
```bash
if ! airtable bases --json 2>/dev/null; then
    echo "Please set AIRTABLE_API_KEY environment variable"
    echo "Get token from: https://airtable.com/create/tokens"
fi
```

2. **Invalid Base/Table**
```bash
# Verify base exists
if ! airtable base "$BASE_ID" --json 2>/dev/null; then
    echo "Invalid base ID. Available bases:"
    airtable bases
fi
```

3. **Rate Limiting**
```bash
# Add delays for bulk operations
for record in "${records[@]}"; do
    airtable create BASE_ID "Table" --data "$record" --json || {
        echo "Failed, waiting before retry..."
        sleep 30
        airtable create BASE_ID "Table" --data "$record" --json
    }
    sleep 0.2
done
```

## Integration Best Practices

### When to Use Airtable CLI
- ✅ Reading data for analysis
- ✅ Creating records from other sources
- ✅ Updating status fields
- ✅ Exporting for backups
- ✅ Simple CRUD operations

### When NOT to Use
- ❌ Complex formula fields (use UI)
- ❌ Schema modifications (use UI)
- ❌ Attachment handling (use UI/API)
- ❌ Real-time sync (use webhooks)

### Performance Tips
- Use `--limit` for large tables
- Export to JSON for complex processing
- Batch operations with sleep delays
- Cache base/table IDs

## Common Patterns for AI

### User asks to "add to Airtable"
```bash
# 1. Discover their bases
bases=$(airtable bases --json)
echo "Which base would you like to use?"
# Show bases to user

# 2. Discover tables
tables=$(airtable base BASE_ID --json)
echo "Which table?"
# Show tables to user

# 3. Show schema
airtable schema BASE_ID "Table Name" --json
# Understand required fields

# 4. Create record
airtable create BASE_ID "Table Name" \
  --data '{"Field1": "Value1", "Field2": "Value2"}' --json
```

### User asks to "check Airtable"
```bash
# Show recent records
airtable list BASE_ID "Table Name" --limit 10 --sort "-Created" --json
```

### User asks to "update Airtable"
```bash
# First find the record
records=$(airtable list BASE_ID "Table Name" --filter "Name=Target" --json)
record_id=$(echo "$records" | jq -r '.[0].id')

# Then update it
airtable update BASE_ID "Table Name" "$record_id" \
  --data '{"Status": "Updated"}' --json
```

## Important Notes

1. **Table names with spaces** must be quoted
2. **JSON data** must be valid - use `jq` to validate
3. **Rate limits** are strict - add delays for bulk ops
4. **Field names** are case-sensitive
5. **Deleted records** cannot be recovered

## Security Reminders

- Never log or display the API key
- Use `--token` flag only for one-off operations
- Tokens inherit user permissions
- No way to increase rate limits