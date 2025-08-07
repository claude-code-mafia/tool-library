# Cloudflare Workers CLI Implementation Plan - Team Requirements

## Executive Summary
This implementation plan addresses the specific requirements from the team for managing Cloudflare Workers with Durable Objects and custom routes. All requested functionality is supported by Cloudflare's API with no blockers identified.

## Team's Required Commands

```bash
cf-cli create worker cell-router --path ./workers/cell-router
cf-cli deploy cell-router
cf-cli create durable-object CELL_REGISTRY --class CellRegistry
cf-cli add route "*.cells.fidelity.com" --worker cell-router
```

## Implementation Architecture

### 1. Worker Creation & Deployment

**Command:** `cf-cli create worker [name] --path [path]`

**Implementation:**
```python
def create_worker(name, path):
    """Create and deploy a worker from local files"""
    # 1. Read worker files from path
    worker_js = read_file(f"{path}/index.js")
    package_json = read_file(f"{path}/package.json", optional=True)
    
    # 2. Detect Durable Object classes
    durable_objects = detect_durable_objects(worker_js)
    
    # 3. Build metadata
    metadata = {
        "main_module": "index.js",
        "compatibility_date": "2024-01-01",
        "bindings": [],
        "migrations": []
    }
    
    # 4. Deploy via multipart upload
    files = {
        'metadata': (None, json.dumps(metadata), 'application/json'),
        'index.js': ('index.js', worker_js, 'application/javascript')
    }
    
    response = requests.put(
        f"{BASE_URL}/accounts/{ACCOUNT_ID}/workers/scripts/{name}",
        files=files,
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    )
```

**Durable Object Detection:**
```python
def detect_durable_objects(code):
    """Parse JavaScript to find Durable Object classes"""
    import re
    # Pattern to match: export class ClassName extends DurableObject
    pattern = r'export\s+class\s+(\w+)\s+(?:extends\s+DurableObject|{[^}]*fetch\s*\()'
    return re.findall(pattern, code)
```

### 2. Durable Object Configuration

**Command:** `cf-cli create durable-object [binding_name] --class [class_name]`

**Implementation:**
```python
def create_durable_object(worker_name, binding_name, class_name):
    """Add Durable Object binding to existing worker"""
    # 1. Get current worker metadata
    current = get_worker_metadata(worker_name)
    
    # 2. Add DO binding
    do_binding = {
        "type": "durable_object_namespace",
        "name": binding_name,
        "class_name": class_name,
        "script_name": worker_name
    }
    
    # 3. Add migration for new DO
    migration = {
        "tag": f"v{len(current.get('migrations', [])) + 1}",
        "new_sqlite_classes": [class_name]
    }
    
    # 4. Update metadata
    metadata = current.get('metadata', {})
    metadata['bindings'] = metadata.get('bindings', []) + [do_binding]
    metadata['migrations'] = metadata.get('migrations', []) + [migration]
    
    # 5. Redeploy worker with updated metadata
    redeploy_worker(worker_name, metadata)
```

**Key Features:**
- Validates class exists in worker code
- Auto-generates migration tags
- Supports SQLite backend (recommended)
- Can bind to classes in same or different workers

### 3. Route Management

**Command:** `cf-cli add route [pattern] --worker [worker_name]`

**Implementation:**
```python
def add_route(pattern, worker_name):
    """Add route pattern to worker"""
    # 1. Extract domain from pattern
    domain = extract_domain(pattern)  # "*.cells.fidelity.com" -> "fidelity.com"
    
    # 2. Get zone ID for domain
    zone_id = get_zone_id(domain)
    if not zone_id:
        raise Exception(f"Domain {domain} not found in your Cloudflare account")
    
    # 3. Create route
    route_data = {
        "pattern": pattern,
        "script": worker_name
    }
    
    response = requests.post(
        f"{BASE_URL}/zones/{zone_id}/workers/routes",
        json=route_data,
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    )
    
    return response.json()

def get_zone_id(domain):
    """Get zone ID from domain name"""
    response = requests.get(
        f"{BASE_URL}/zones?name={domain}",
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    )
    zones = response.json().get('result', [])
    return zones[0]['id'] if zones else None
```

### 4. Simplified Deployment Command

**Command:** `cf-cli deploy [worker_name]`

**Implementation:**
```python
def deploy(worker_name):
    """Deploy or update existing worker"""
    # Look for worker in common locations
    paths = [
        f"./workers/{worker_name}",
        f"./{worker_name}",
        "./src",
        "."
    ]
    
    for path in paths:
        if os.path.exists(f"{path}/index.js"):
            return create_worker(worker_name, path)
    
    raise Exception(f"Worker files not found for {worker_name}")
```

## Complete CLI Structure

### Core Commands
```bash
# Worker Management
cf-cli create worker [name] --path [path]    # Create & deploy worker
cf-cli deploy [name]                         # Deploy/update worker
cf-cli list workers                          # List all workers
cf-cli delete worker [name]                  # Delete worker
cf-cli logs [name] --tail                    # Stream logs

# Durable Objects
cf-cli create durable-object [binding] --class [class] --worker [name]
cf-cli list durable-objects --worker [name]
cf-cli migrate durable-object [class] --from [old] --to [new]

# Routes
cf-cli add route [pattern] --worker [name]
cf-cli list routes --worker [name]
cf-cli delete route [route-id]

# KV Storage (bonus)
cf-cli create kv [namespace]
cf-cli kv put [namespace] [key] [value]
cf-cli kv get [namespace] [key]
```

### Configuration File Support

**.cf-cli.json** (project config):
```json
{
  "account_id": "your-account-id",
  "workers": {
    "cell-router": {
      "path": "./workers/cell-router",
      "routes": ["*.cells.fidelity.com"],
      "durable_objects": [
        {
          "binding": "CELL_REGISTRY",
          "class": "CellRegistry"
        }
      ]
    }
  }
}
```

**Bulk Deploy:**
```bash
cf-cli deploy --all        # Deploy all workers in config
cf-cli validate           # Validate configuration
```

## Error Handling & Edge Cases

### 1. Zone Not Found
```python
def ensure_zone_exists(domain):
    """Check if domain exists in account"""
    zone_id = get_zone_id(domain)
    if not zone_id:
        print(f"Error: Domain {domain} not found in your Cloudflare account")
        print("Available domains:")
        list_zones()
        sys.exit(1)
    return zone_id
```

### 2. Durable Object Class Validation
```python
def validate_durable_object_class(worker_name, class_name):
    """Ensure DO class exists in worker code"""
    code = get_worker_code(worker_name)
    if class_name not in detect_durable_objects(code):
        print(f"Error: Class {class_name} not found in {worker_name}")
        print("Available classes:", detect_durable_objects(code))
        sys.exit(1)
```

### 3. Route Conflicts
```python
def check_route_conflicts(pattern, zone_id):
    """Warn about conflicting routes"""
    existing_routes = list_routes(zone_id)
    conflicts = [r for r in existing_routes if routes_overlap(r['pattern'], pattern)]
    if conflicts:
        print(f"Warning: Route pattern may conflict with:")
        for r in conflicts:
            print(f"  - {r['pattern']} -> {r['script']}")
```

## Authentication

**Environment Variables:**
```bash
export CLOUDFLARE_API_TOKEN=your-token
export CLOUDFLARE_ACCOUNT_ID=your-account-id
```

**First Run Setup:**
```bash
cf-cli auth init
# Prompts for API token and account ID
# Validates credentials
# Saves to ~/.cf-cli/config.json
```

## Testing Strategy

### Integration Tests
```python
def test_full_workflow():
    """Test complete worker deployment with DO and routes"""
    # 1. Create worker
    result = create_worker("test-cell-router", "./test-workers/cell-router")
    assert result['success']
    
    # 2. Add Durable Object
    result = create_durable_object("test-cell-router", "CELLS", "CellRegistry")
    assert result['success']
    
    # 3. Add route
    result = add_route("test.example.com/*", "test-cell-router")
    assert result['success']
    
    # 4. Verify deployment
    worker = get_worker("test-cell-router")
    assert "CELLS" in [b['name'] for b in worker['bindings']]
    
    # 5. Cleanup
    delete_worker("test-cell-router")
```

## Implementation Timeline

### Week 1: Core Foundation
- [ ] Basic CLI structure with argparse
- [ ] Authentication and config management
- [ ] Worker create/deploy commands
- [ ] Error handling framework

### Week 2: Durable Objects & Routes
- [ ] Durable Object detection and binding
- [ ] Route management with zone lookup
- [ ] Validation and conflict detection
- [ ] Migration support

### Week 3: Advanced Features
- [ ] Real-time log tailing
- [ ] KV namespace management
- [ ] Config file support
- [ ] Bulk operations

### Week 4: Polish & Testing
- [ ] Comprehensive error messages
- [ ] Integration tests
- [ ] Documentation
- [ ] Performance optimization

## Success Metrics

1. **All team commands work exactly as specified**
2. **Deployment time < 5 seconds**
3. **Clear error messages with remediation steps**
4. **Zero manual zone ID lookups required**
5. **Automatic DO class detection and validation**

## Security Considerations

1. **API Token Scoping**
   - Recommend zone-specific tokens
   - Never log sensitive data
   - Secure storage in OS keychain

2. **Code Validation**
   - Syntax check before deployment
   - Size limits enforcement
   - Malicious code detection

3. **Route Security**
   - Validate route patterns
   - Warn about overly broad wildcards
   - Check DNS record existence

## Conclusion

All requested functionality is fully supported by Cloudflare's API. The main implementation consideration is that Durable Objects are configured as part of worker deployment rather than created separately. The CLI will abstract this complexity, providing the exact commands the team expects while handling the underlying API interactions seamlessly.