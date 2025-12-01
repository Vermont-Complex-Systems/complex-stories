#!/usr/bin/env python3
"""
Google Scholar Venues Data Import Script

This script reads a parquet file and sends the data to the backend API for import.
Follows best practices by separating data parsing from storage.
"""

import pandas as pd
import requests
import sys
from pathlib import Path
from typing import List, Dict, Any
import argparse
import os
from dotenv import load_dotenv

load_dotenv()

def send_to_api(records: List[Dict[str, Any]], jwt_token, api_base_url: str, clear_existing: bool = True) -> Dict[str, Any]:
    """Send parsed records to the backend API."""
    url = f"{api_base_url}/admin/datasets/google-scholar-venues/import"

    # Send records as the main payload with clear_existing as query parameter
    params = {
        "clear_existing": clear_existing
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {jwt_token}'  # 👈 JWT token here
    }

    try:
        response = requests.post(url, json=records, params=params, headers=headers, timeout=300, verify=False)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {e}")

def main():
    parser = argparse.ArgumentParser(description='Import Google Scholar venues data')
    parser.add_argument('--parquet-file',
                       help='Path to Parquet file.')
    parser.add_argument('--api-base',
                       default='https://api.complexstories.uvm.edu',
                       help='API base URL (default: https://api.complexstories.uvm.edu)')
    parser.add_argument('--no-clear',
                       action='store_true',
                       help='Do not clear existing data before import')
    parser.add_argument('--dry-run',
                       action='store_true',
                       help='Parse CSV but do not send to API')

    args = parser.parse_args()

    # Resolve CSV path relative to script directory
    script_dir = Path(__file__).parent
    parquet_path = script_dir / args.parquet_file
    jwt_token = os.getenv("JWT_TOKEN")

    try:
        print(f"📄 Parsing parquet file: {parquet_path}")
        records = pd.read_parquet(parquet_path).to_dict(orient="records")
        print(f"✅ Parsed {len(records)} records")

        if args.dry_run:
            print("🔍 Dry run - showing first 3 records:")
            for i, record in enumerate(records[:3]):
                print(f"  Record {i+1}: {record}")
            return

        print(f"📤 Sending data to API: {args.api_base}")
        result = send_to_api(records, jwt_token, args.api_base, clear_existing=not args.no_clear)

        print(f"✅ {result['message']}")
        print(f"📊 Records received: {result['records_received']}")
        print(f"📊 Records imported: {result['imported_count']}")

        if result['records_received'] != result['imported_count']:
            print(f"⚠️  Warning: {result['records_received'] - result['imported_count']} records were skipped")

        # Show user sync results if available
        if 'user_sync' in result:
            user_sync = result['user_sync']
            print(f"👥 {user_sync['message']}")
            if 'users' in user_sync and user_sync['users']:
                print(f"   New users created:")
                for user in user_sync['users']:
                    print(f"   - {user['username']} ({user['payroll_name']})")
            else:
                print(f"   No new users needed to be created")

    except Exception as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()