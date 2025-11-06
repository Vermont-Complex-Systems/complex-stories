#!/usr/bin/env python3
"""
INPUT step: Download raw S2ORC datasets from Semantic Scholar
Follows principled data processing - downloads to input/ directory
"""
import argparse
import sys
from pathlib import Path
import requests
import json
import gzip
from typing import Optional, List
import time
import os

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config

class DownloadError(Exception):
    """Exception raised when download fails"""
    pass


def download_s2_release(
    dataset_name: str,
    release_id: Optional[str] = None,
    clean_slate: bool = False
) -> Path:
    """
    Download Semantic Scolar dataset
    
    Args:
        dataset_name: Name of dataset (papers, authors, etc.)
        release_id: Specific release ID, or None for latest
        clean_slate: Whether to remove existing data first
        
    Returns:
        Path to downloaded dataset directory
    """
    print(f"[INPUT] Downloading S2ORC dataset: {dataset_name}")
    
    # Create output directory structure
    # dataset_name = 'paper-ids'
    dataset_dir = config.s2_data_root / dataset_name
    
    if clean_slate and dataset_dir.exists():
        print(f"[INPUT] Removing existing directory: {dataset_dir}")
        import shutil
        shutil.rmtree(dataset_dir)
    
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup API
    headers = {"x-api-key": config.s2_api_key}
    
    try:
        # 1. Get release information
        print("[INPUT] Fetching release information...")
        releases_url = "https://api.semanticscholar.org/datasets/v1/release/"
        
        response = requests.get(releases_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        releases = response.json()
        if not releases:
            raise DownloadError("No releases found")
        
        # Use specified release or latest
        target_release = release_id if release_id else releases[-1]
        print(f"[INPUT] Target release: {target_release}")
        
        # Save release metadata
        release_metadata = {
            "release_id": target_release,
            "dataset_name": dataset_name,
            "download_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "all_available_releases": releases
        }
        
        # metadata_file = dataset_dir / "release_metadata.json"
        # with open(metadata_file, 'w') as f:
        #     json.dump(release_metadata, f, indent=2)
        # print(f"[INPUT] Saved release metadata to {metadata_file.name}")
        
        # 2. Get dataset files
        dataset_url = f"https://api.semanticscholar.org/datasets/v1/release/{target_release}/dataset/{dataset_name}"
        
        print(f"[INPUT] Fetching dataset files...")
        response = requests.get(dataset_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        dataset_info = response.json()
        
        if 'files' not in dataset_info:
            raise DownloadError(f"No 'files' field found in dataset response")
        
        file_urls = dataset_info['files']
        print(f"[INPUT] Found {len(file_urls)} files to download")
        
        # 3. Download each file
        downloaded_files = []
        for i, url in enumerate(file_urls, 1):
            print(f"[INPUT] Downloading file {i}/{len(file_urls)}")
            
            # Use zero-padded numbering for sorting
            filename = f"{dataset_name}_{i:04d}.json.gz"
            output_file = dataset_dir / filename
            
            try:
                # Download with streaming
                file_response = requests.get(url, timeout=300, stream=True)
                file_response.raise_for_status()
                
                # Save compressed file
                with open(output_file, 'wb') as f:
                    for chunk in file_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size_mb = output_file.stat().st_size / 1024 / 1024
                print(f"[INPUT]   ✓ {output_file.name} ({file_size_mb:.1f} MB)")
                downloaded_files.append(output_file.name)
                
            except requests.RequestException as e:
                print(f"[INPUT]   ✗ Failed: {e}")
                continue
            
            # Be respectful to API
            time.sleep(0.5)
        
        # 4. Verify downloads
        if not downloaded_files:
            raise DownloadError("No files were successfully downloaded")
        
        # Save download manifest
        manifest = {
            "release_id": target_release,
            "dataset_name": dataset_name,
            "total_files": len(downloaded_files),
            "files": downloaded_files,
            "download_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        manifest_file = dataset_dir / "download_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n[INPUT] ✓ Download complete!")
        print(f"[INPUT] Files: {len(downloaded_files)}")
        print(f"[INPUT] Location: {dataset_dir}/")
        print(f"[INPUT] Manifest: {manifest_file.name}")
        
        return dataset_dir
        
    except requests.RequestException as e:
        raise DownloadError(f"API request failed: {e}")
    except Exception as e:
        raise DownloadError(f"Download failed: {e}")


def list_available_datasets(api_key: str) -> List[str]:
    """List all available datasets from S2"""
    headers = {"x-api-key": api_key}
    
    # Get latest release
    releases_url = "https://api.semanticscholar.org/datasets/v1/release/"
    response = requests.get(releases_url, headers=headers)
    response.raise_for_status()
    
    releases = response.json()
    latest_release = releases[-1]
    
    # Get datasets for latest release
    datasets_url = f"https://api.semanticscholar.org/datasets/v1/release/{latest_release}"
    response = requests.get(datasets_url, headers=headers)
    response.raise_for_status()
    
    return response.json().get('datasets', [])


def main():
    parser = argparse.ArgumentParser(
        description="INPUT step: Download raw S2ORC datasets"
    )
    parser.add_argument(
        "dataset_name",
        nargs='?',
        help="Dataset to download (papers, authors, etc.)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("input"),
        help="Output directory (default: input/)"
    )
    parser.add_argument(
        "--release",
        help="Specific release ID (default: latest)"
    )
    parser.add_argument(
        "--clean-slate",
        action="store_true",
        help="Remove existing data before downloading"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available datasets"
    )
    
    args = parser.parse_args()
    
    if args.list:
        try:
            datasets = list_available_datasets(config.s2_api_key)
            print("Available datasets:")
            for dataset in datasets:
                print(f"  - {dataset}")
            return
        except Exception as e:
            print(f"❌ Failed to list datasets: {e}")
            sys.exit(1)
    
    # Download dataset
    if not args.dataset_name:
        parser.print_help()
        sys.exit(1)
    
    try:
        dataset_dir = download_s2_release(
            dataset_name=args.dataset_name,
            release_id=args.release,
            clean_slate=args.clean_slate
        )
        
        print(f"\n🎉 SUCCESS!")
        print(f"📁 Raw data saved to: {dataset_dir}")
        print(f"\n📋 Next steps:")
        print(f"   1. Run 'make import' to parse and validate")
        print(f"   2. Run 'make export' to load into DuckLake")
        
    except DownloadError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()