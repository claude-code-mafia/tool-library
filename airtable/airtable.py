#!/usr/bin/env python3
"""
Airtable CLI - Command line interface for Airtable

Manage your Airtable bases, tables, and records from the command line.
"""

import argparse
import json
import sys
import os
import csv
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from pyairtable import Api, Base, Table
    from pyairtable.formulas import match
except ImportError:
    print("Error: pyairtable is not installed", file=sys.stderr)
    print("Run: pip install pyairtable", file=sys.stderr)
    sys.exit(1)

def get_api_key() -> str:
    """Get API key from environment or fail with helpful message."""
    api_key = os.environ.get('AIRTABLE_API_KEY')
    if not api_key:
        print("Error: AIRTABLE_API_KEY environment variable not set", file=sys.stderr)
        print("Get your personal access token from: https://airtable.com/create/tokens", file=sys.stderr)
        print("Export it: export AIRTABLE_API_KEY='your-token-here'", file=sys.stderr)
        sys.exit(1)
    return api_key

def format_record(record: Dict[str, Any], show_id: bool = True) -> str:
    """Format a record for human-readable output."""
    lines = []
    if show_id:
        lines.append(f"ID: {record['id']}")
        lines.append(f"Created: {record['createdTime']}")
    
    fields = record.get('fields', {})
    if fields:
        lines.append("Fields:")
        for key, value in fields.items():
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value)
            elif isinstance(value, dict):
                value = json.dumps(value)
            lines.append(f"  {key}: {value}")
    else:
        lines.append("Fields: (empty)")
    
    return '\n'.join(lines)

def list_bases(api: Api, args) -> None:
    """List all accessible bases."""
    try:
        bases = api.bases()
        
        if args.json:
            print(json.dumps([b.dict() for b in bases], indent=2))
        else:
            if not bases:
                print("No bases found")
                return
            
            print(f"Found {len(bases)} bases:\n")
            for base in bases:
                print(f"ID: {base.id}")
                print(f"Name: {base.name}")
                print(f"Permission: {base.permission_level}")
                print()
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def show_base(api: Api, args) -> None:
    """Show details about a specific base."""
    try:
        base = api.base(args.base_id)
        schema = base.schema()
        
        if args.json:
            print(json.dumps(schema.dict(), indent=2))
        else:
            print(f"Base ID: {args.base_id}")
            print(f"\nTables ({len(schema.tables)}):")
            for table in schema.tables:
                print(f"\n  {table.name} (ID: {table.id})")
                print(f"  Primary field: {table.primary_field_id}")
                print(f"  Fields: {len(table.fields)}")
                if table.description:
                    print(f"  Description: {table.description}")
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def list_records(api: Api, args) -> None:
    """List records from a table."""
    try:
        table = api.table(args.base_id, args.table_name)
        
        # Build query parameters
        params = {}
        if args.limit:
            params['max_records'] = args.limit
        if args.view:
            params['view'] = args.view
        if args.sort:
            params['sort'] = [args.sort]
        if args.filter:
            # Simple filter format: "field=value"
            if '=' in args.filter:
                field, value = args.filter.split('=', 1)
                params['formula'] = match({field.strip(): value.strip()})
        
        records = table.all(**params)
        
        if args.json:
            print(json.dumps([r for r in records], indent=2))
        else:
            if not records:
                print("No records found")
                return
            
            print(f"Found {len(records)} records:\n")
            for i, record in enumerate(records):
                if i > 0:
                    print("-" * 40)
                print(format_record(record))
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def get_record(api: Api, args) -> None:
    """Get a specific record."""
    try:
        table = api.table(args.base_id, args.table_name)
        record = table.get(args.record_id)
        
        if args.json:
            print(json.dumps(record, indent=2))
        else:
            print(format_record(record))
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def create_record(api: Api, args) -> None:
    """Create a new record."""
    try:
        table = api.table(args.base_id, args.table_name)
        
        # Parse data
        try:
            fields = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON data - {e}", file=sys.stderr)
            sys.exit(1)
        
        record = table.create(fields)
        
        if args.json:
            print(json.dumps(record, indent=2))
        else:
            print("Record created successfully!")
            print(format_record(record))
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def update_record(api: Api, args) -> None:
    """Update an existing record."""
    try:
        table = api.table(args.base_id, args.table_name)
        
        # Parse data
        try:
            fields = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON data - {e}", file=sys.stderr)
            sys.exit(1)
        
        record = table.update(args.record_id, fields)
        
        if args.json:
            print(json.dumps(record, indent=2))
        else:
            print("Record updated successfully!")
            print(format_record(record))
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def delete_record(api: Api, args) -> None:
    """Delete a record."""
    try:
        table = api.table(args.base_id, args.table_name)
        
        # Confirm deletion unless --force
        if not args.force and not args.json:
            response = input(f"Delete record {args.record_id}? (y/N): ")
            if response.lower() != 'y':
                print("Deletion cancelled")
                return
        
        result = table.delete(args.record_id)
        
        if args.json:
            print(json.dumps({"deleted": True, "id": args.record_id}, indent=2))
        else:
            print(f"Record {args.record_id} deleted successfully")
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def show_schema(api: Api, args) -> None:
    """Show table schema."""
    try:
        base = api.base(args.base_id)
        schema = base.schema()
        
        # Find the table
        table_schema = None
        for table in schema.tables:
            if table.name == args.table_name or table.id == args.table_name:
                table_schema = table
                break
        
        if not table_schema:
            print(f"Error: Table '{args.table_name}' not found", file=sys.stderr)
            sys.exit(1)
        
        if args.json:
            print(json.dumps(table_schema.dict(), indent=2))
        else:
            print(f"Table: {table_schema.name}")
            print(f"ID: {table_schema.id}")
            if table_schema.description:
                print(f"Description: {table_schema.description}")
            
            print(f"\nFields ({len(table_schema.fields)}):")
            for field in table_schema.fields:
                print(f"\n  {field.name}")
                print(f"    Type: {field.type}")
                print(f"    ID: {field.id}")
                if field.description:
                    print(f"    Description: {field.description}")
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def export_table(api: Api, args) -> None:
    """Export table to CSV or JSON."""
    try:
        table = api.table(args.base_id, args.table_name)
        records = table.all()
        
        if not records:
            print("No records to export")
            return
        
        # Determine format
        format = args.format or 'json'
        if args.output and args.output.endswith('.csv'):
            format = 'csv'
        
        if format == 'json':
            output = json.dumps([r for r in records], indent=2)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Exported {len(records)} records to {args.output}")
            else:
                print(output)
        else:  # CSV
            # Collect all field names
            all_fields = set()
            for record in records:
                all_fields.update(record.get('fields', {}).keys())
            
            fieldnames = ['id', 'createdTime'] + sorted(list(all_fields))
            
            if args.output:
                with open(args.output, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for record in records:
                        row = {'id': record['id'], 'createdTime': record['createdTime']}
                        row.update(record.get('fields', {}))
                        writer.writerow(row)
                print(f"Exported {len(records)} records to {args.output}")
            else:
                writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
                writer.writeheader()
                for record in records:
                    row = {'id': record['id'], 'createdTime': record['createdTime']}
                    row.update(record.get('fields', {}))
                    writer.writerow(row)
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Airtable CLI - Manage your Airtable bases from the command line',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  airtable bases                                    # List all bases
  airtable base appXXXXXX                          # Show base details
  airtable list appXXXXXX "Table Name"             # List records
  airtable get appXXXXXX "Table Name" recXXXXXX    # Get specific record
  airtable create appXXXXXX "Table Name" --data '{"Name": "Test"}'
  airtable export appXXXXXX "Table Name" --output data.csv
        """
    )
    
    parser.add_argument('--token', help='API token (overrides AIRTABLE_API_KEY)')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Common arguments for all subcommands
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # bases command
    bases_parser = subparsers.add_parser('bases', help='List all accessible bases', parents=[common_parser])
    
    # base command
    base_parser = subparsers.add_parser('base', help='Show base details', parents=[common_parser])
    base_parser.add_argument('base_id', help='Base ID (e.g., appXXXXXX)')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List records from a table', parents=[common_parser])
    list_parser.add_argument('base_id', help='Base ID')
    list_parser.add_argument('table_name', help='Table name')
    list_parser.add_argument('--limit', type=int, help='Maximum records to return')
    list_parser.add_argument('--view', help='View name to use')
    list_parser.add_argument('--sort', help='Field to sort by')
    list_parser.add_argument('--filter', help='Simple filter (field=value)')
    
    # get command
    get_parser = subparsers.add_parser('get', help='Get a specific record', parents=[common_parser])
    get_parser.add_argument('base_id', help='Base ID')
    get_parser.add_argument('table_name', help='Table name')
    get_parser.add_argument('record_id', help='Record ID')
    
    # create command
    create_parser = subparsers.add_parser('create', help='Create a new record', parents=[common_parser])
    create_parser.add_argument('base_id', help='Base ID')
    create_parser.add_argument('table_name', help='Table name')
    create_parser.add_argument('--data', required=True, help='JSON data for fields')
    
    # update command
    update_parser = subparsers.add_parser('update', help='Update a record', parents=[common_parser])
    update_parser.add_argument('base_id', help='Base ID')
    update_parser.add_argument('table_name', help='Table name')
    update_parser.add_argument('record_id', help='Record ID')
    update_parser.add_argument('--data', required=True, help='JSON data for fields to update')
    
    # delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a record', parents=[common_parser])
    delete_parser.add_argument('base_id', help='Base ID')
    delete_parser.add_argument('table_name', help='Table name')
    delete_parser.add_argument('record_id', help='Record ID')
    delete_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    # schema command
    schema_parser = subparsers.add_parser('schema', help='Show table schema', parents=[common_parser])
    schema_parser.add_argument('base_id', help='Base ID')
    schema_parser.add_argument('table_name', help='Table name')
    
    # export command
    export_parser = subparsers.add_parser('export', help='Export table data', parents=[common_parser])
    export_parser.add_argument('base_id', help='Base ID')
    export_parser.add_argument('table_name', help='Table name')
    export_parser.add_argument('--output', help='Output file (extension determines format)')
    export_parser.add_argument('--format', choices=['json', 'csv'], help='Export format')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Get API key
    api_key = args.token if hasattr(args, 'token') and args.token else get_api_key()
    api = Api(api_key)
    
    # Route to appropriate function
    commands = {
        'bases': list_bases,
        'base': show_base,
        'list': list_records,
        'get': get_record,
        'create': create_record,
        'update': update_record,
        'delete': delete_record,
        'schema': show_schema,
        'export': export_table,
    }
    
    command_func = commands.get(args.command)
    if command_func:
        command_func(api, args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()