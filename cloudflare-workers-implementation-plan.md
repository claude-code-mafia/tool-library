# Cloudflare Workers CLI Tool Implementation Plan

## Project Overview
Build a comprehensive CLI tool for managing Cloudflare Workers, providing an intuitive interface for deployment, configuration, and monitoring of Workers, KV storage, routes, and cron triggers.

## Core Features & Implementation Details

### 1. Worker Script Management

**Commands:**
- `cfw deploy [script-file]` - Deploy a worker from local file
- `cfw list` - List all workers
- `cfw delete [script-name]` - Delete a worker
- `cfw logs [script-name]` - Tail real-time logs
- `cfw download [script-name]` - Download worker code

**API Endpoints:**
```bash
# List workers
GET /accounts/{account_id}/workers/scripts

# Deploy/Update worker
PUT /accounts/{account_id}/workers/scripts/{script_name}
Content-Type: multipart/form-data
Body: metadata (JSON) + script content

# Delete worker
DELETE /accounts/{account_id}/workers/scripts/{script_name}

# Get worker content
GET /accounts/{account_id}/workers/scripts/{script_name}/content
```

**Example Implementation:**
```python
def deploy_worker(script_name, script_file, metadata=None):
    """Deploy a Worker script"""
    with open(script_file, 'r') as f:
        script_content = f.read()
    
    # Prepare multipart form data
    files = {
        'metadata': (None, json.dumps(metadata or {}), 'application/json'),
        'script': (script_name, script_content, 'application/javascript')
    }
    
    response = requests.put(
        f"{BASE_URL}/accounts/{ACCOUNT_ID}/workers/scripts/{script_name}",
        files=files,
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    )
    return response.json()
```

### 2. KV Namespace Management

**Commands:**
- `cfw kv create [namespace-name]` - Create KV namespace
- `cfw kv list` - List all namespaces
- `cfw kv delete [namespace-id]` - Delete namespace
- `cfw kv put [namespace-id] [key] [value]` - Store value
- `cfw kv get [namespace-id] [key]` - Retrieve value
- `cfw kv keys [namespace-id]` - List all keys
- `cfw kv bulk-put [namespace-id] [json-file]` - Bulk upload

**API Endpoints:**
```bash
# Create namespace
POST /accounts/{account_id}/storage/kv/namespaces
Body: {"title": "namespace-name"}

# List namespaces
GET /accounts/{account_id}/storage/kv/namespaces

# Put value
PUT /accounts/{account_id}/storage/kv/namespaces/{namespace_id}/values/{key_name}
Query params: ?expiration={timestamp}&expiration_ttl={seconds}

# Get value
GET /accounts/{account_id}/storage/kv/namespaces/{namespace_id}/values/{key_name}

# List keys
GET /accounts/{account_id}/storage/kv/namespaces/{namespace_id}/keys

# Bulk operations
PUT /accounts/{account_id}/storage/kv/namespaces/{namespace_id}/bulk
Body: Array of key-value pairs (up to 10,000)
```

**Example Implementation:**
```python
def kv_bulk_upload(namespace_id, data_file):
    """Bulk upload key-value pairs from JSON file"""
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Format for bulk API: [{"key": "k1", "value": "v1"}, ...]
    bulk_data = [{"key": k, "value": v} for k, v in data.items()]
    
    # Split into chunks of 10,000 if needed
    for chunk in chunks(bulk_data, 10000):
        response = requests.put(
            f"{BASE_URL}/accounts/{ACCOUNT_ID}/storage/kv/namespaces/{namespace_id}/bulk",
            json=chunk,
            headers=headers
        )
```

### 3. Routes & Custom Domains

**Commands:**
- `cfw route create [pattern] [script-name]` - Create route
- `cfw route list [zone-id]` - List routes for zone
- `cfw route delete [zone-id] [route-id]` - Delete route
- `cfw route update [zone-id] [route-id] [pattern]` - Update route
- `cfw domain add [domain] [script-name]` - Add custom domain

**API Endpoints:**
```bash
# Create route
POST /zones/{zone_id}/workers/routes
Body: {"pattern": "example.com/api/*", "script": "my-worker"}

# List routes
GET /zones/{zone_id}/workers/routes

# Update route
PUT /zones/{zone_id}/workers/routes/{route_id}
Body: {"pattern": "new-pattern", "script": "worker-name"}

# Delete route
DELETE /zones/{zone_id}/workers/routes/{route_id}
```

**Route Pattern Examples:**
- `example.com/*` - All paths on domain
- `*.example.com/api/*` - API paths on all subdomains
- `example.com/specific-path` - Exact path
- `*example.com/images/*` - Images on domain and subdomains

### 4. Cron Triggers

**Commands:**
- `cfw cron set [script-name] [cron-expression]` - Set cron trigger
- `cfw cron list [script-name]` - List triggers
- `cfw cron remove [script-name] [cron-expression]` - Remove trigger
- `cfw cron test [script-name]` - Test trigger execution

**API Endpoints:**
```bash
# Update cron triggers (replaces all)
PUT /accounts/{account_id}/workers/scripts/{script_name}/schedules
Body: {"schedules": [{"cron": "*/30 * * * *"}, {"cron": "0 0 * * *"}]}

# Get current triggers
GET /accounts/{account_id}/workers/scripts/{script_name}/schedules
```

**Cron Expression Format:**
- Minutes (0-59)
- Hours (0-23)
- Days of month (1-31)
- Months (1-12 or JAN-DEC)
- Days of week (1-7, Sunday=1)

**Examples:**
- `*/5 * * * *` - Every 5 minutes
- `0 0 * * *` - Daily at midnight
- `0 9 * * 1` - Every Monday at 9 AM

### 5. Real-time Monitoring

**Commands:**
- `cfw tail [script-name]` - Stream real-time logs
- `cfw tail [script-name] --filter "status:500"` - Filtered logs
- `cfw metrics [script-name]` - View worker metrics

**Implementation:**
```python
def tail_logs(script_name, filters=None):
    """Stream real-time logs using wrangler tail equivalent"""
    # Note: Real-time logs API not directly exposed
    # Options:
    # 1. Use subprocess to call wrangler tail
    # 2. Implement WebSocket connection if API becomes available
    # 3. Poll Workers Logs API endpoint
    
    # For now, use subprocess approach
    cmd = ["wrangler", "tail", script_name]
    if filters:
        cmd.extend(["--filter", filters])
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    for line in process.stdout:
        print(json.dumps(json.loads(line), indent=2))
```

### 6. Development Workflow

**Commands:**
- `cfw init [project-name]` - Initialize new worker project
- `cfw dev [script-file]` - Local development server
- `cfw watch [script-file]` - Auto-deploy on changes
- `cfw env set [key] [value]` - Set environment variable
- `cfw secret put [key]` - Store secret (prompts for value)

**Project Structure:**
```
my-worker/
├── worker.js           # Main worker script
├── wrangler.toml      # Config file (optional)
├── .env.local         # Local env vars
└── .cfw.json          # CLI config
```

### 7. Advanced Features

**Bulk Operations:**
- `cfw bulk deploy [config-file]` - Deploy multiple workers
- `cfw bulk delete [pattern]` - Delete workers matching pattern
- `cfw export --all` - Export all workers/configs
- `cfw import [export-file]` - Import from export

**Config File Format (.cfw.json):**
```json
{
  "account_id": "your-account-id",
  "workers": {
    "api-worker": {
      "script": "src/api.js",
      "routes": ["api.example.com/*"],
      "crons": ["0 * * * *"],
      "kv_namespaces": ["API_CACHE"],
      "env_vars": {
        "API_VERSION": "v2"
      }
    }
  }
}
```

## Authentication & Configuration

**Environment Variables:**
```bash
CLOUDFLARE_API_TOKEN=your-token
CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_EMAIL=your-email (legacy)
CLOUDFLARE_API_KEY=your-key (legacy)
```

**Config File (~/.cfw/config.json):**
```json
{
  "profiles": {
    "default": {
      "api_token": "token",
      "account_id": "id"
    },
    "production": {
      "api_token": "prod-token",
      "account_id": "prod-id"
    }
  },
  "current_profile": "default"
}
```

## Error Handling

**Common Errors & Solutions:**
1. **Authentication Failed**
   - Check API token permissions
   - Verify account ID

2. **Route Pattern Invalid**
   - Ensure zone exists
   - Check pattern syntax

3. **KV Limit Exceeded**
   - Bulk operations max 10,000 items
   - Split large uploads

4. **Cron Expression Invalid**
   - Use 5-field format
   - Test with online validators

## Implementation Timeline

1. **Phase 1: Core Script Management** (Week 1)
   - Deploy, list, delete workers
   - Basic authentication
   - Error handling

2. **Phase 2: KV & Routes** (Week 2)
   - KV namespace operations
   - Route management
   - Bulk operations

3. **Phase 3: Advanced Features** (Week 3)
   - Cron triggers
   - Real-time logs
   - Development workflow

4. **Phase 4: Polish & Testing** (Week 4)
   - Comprehensive testing
   - Documentation
   - Performance optimization

## Testing Strategy

**Unit Tests:**
- API client methods
- Input validation
- Error handling

**Integration Tests:**
- Full command workflows
- API response handling
- Edge cases

**Example Test:**
```python
def test_deploy_worker():
    """Test worker deployment"""
    # Create test worker
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js') as f:
        f.write('export default { async fetch(request) { return new Response("Hello") } }')
        f.flush()
        
        result = deploy_worker("test-worker", f.name)
        assert result['success'] == True
        assert result['result']['id'] == "test-worker"
```

## Security Considerations

1. **API Token Storage**
   - Use OS keychain when available
   - Encrypted config file
   - Never log tokens

2. **Input Validation**
   - Sanitize script names
   - Validate cron expressions
   - Check file permissions

3. **Network Security**
   - Always use HTTPS
   - Verify SSL certificates
   - Handle timeouts gracefully

## User Experience

**Interactive Features:**
- Confirmation prompts for destructive actions
- Progress bars for long operations
- Colorized output for better readability
- Tab completion for commands

**Output Formats:**
- Human-readable by default
- JSON output with --json flag
- Quiet mode with --quiet flag
- Verbose debugging with --debug

This implementation plan provides a solid foundation for building a comprehensive Cloudflare Workers CLI tool that covers all major features while maintaining good developer experience and following best practices.