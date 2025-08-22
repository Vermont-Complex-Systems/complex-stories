#!/usr/bin/env python3
"""
Test script for OpenAlex resource
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backend.defs.resources import OpenAlexResource

def test_openalex_resource():
    """Test the OpenAlex resource configuration"""
    
    # Create the resource
    oa_resource = OpenAlexResource(
        email="jonathanstonge7@gmail.com"
    )
    
    # Get the client
    client = oa_resource.get_client()
    
    print(f"✅ OpenAlex client created successfully")
    print(f"📧 Email: {client.email}")
    print(f"🌐 Base URL: {client.base_url}")
    print(f"⚡ Rate limit: {client.max_requests_per_second} req/sec")
    
    try:
        # Test a simple API call
        print("\n🔍 Testing API call...")
        result = client.get_works(filter="author.id:A5078449942", per_page=1)
        
        if 'results' in result:
            print(f"✅ API call successful!")
            print(f"📊 Found {result.get('meta', {}).get('count', 0)} total works")
            if result['results']:
                work = result['results'][0]
                print(f"📄 Sample work: {work.get('title', 'No title')}")
        else:
            print("❌ API call returned unexpected format")
            print(f"Response: {result}")
            
    except Exception as e:
        print(f"❌ API call failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_openalex_resource()