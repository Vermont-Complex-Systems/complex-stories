#!/usr/bin/env python3
"""
Scrapes UVM payroll PDF and saves to input/ stage.

Following PDP principles:
- Only downloads raw PDF data
- No parsing - that happens in import/ stage via run-olmo.sh
"""

import requests
from pathlib import Path
import sys

# UVM_PAYROLL_URL = "https://uvmd10.drup2.uvm.edu/d10-files/documents/2024-07/Final_FY24_Base_Pay.pdf"
# UVM_PAYROLL_URL = "https://uvmd10.drup2.uvm.edu/d10-files/documents/2024-07/Final_FY23_Base_Pay.pdf"
UVM_PAYROLL_URL = "https://www.uvm.edu/d10-files/documents/2024-12/2024-2025-Base-Pay.pdf"

def download_pdf(url, output_path):
    """Download PDF from URL to local path."""
    print(f"📥 Downloading PDF from {url}")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Downloaded to {output_path}")
    return output_path

def main():
    """Main scraping function - downloads PDF only."""
    script_dir = Path(__file__).parent

    # Extract filename from URL
    pdf_filename = UVM_PAYROLL_URL.split("/")[-1]
    pdf_path = script_dir / pdf_filename

    try:
        download_pdf(UVM_PAYROLL_URL, pdf_path)

        print(f"\n🎉 Download complete!")
        print(f"   Raw PDF: {pdf_path}")
        print(f"   Next: run import/parse.py to process via run-olmo.sh")

        return True

    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)