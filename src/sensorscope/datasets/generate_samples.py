#!/usr/bin/env python3
"""
Generate sample datasets for SensorScope file upload testing.

This script creates realistic sensor data files that Sita would upload to
Google Cloud Storage for analysis. Run locally to generate CSV files,
then upload to GCS bucket for cloud function processing.

Usage:
    python generate_samples.py
    
Then upload to GCS:
    gsutil cp *.csv gs://your-bucket-name/datasets/
    gsutil cp *_metadata.json gs://your-bucket-name/datasets/
"""

import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from data_validation import create_sample_datasets_directory

def main():
    """Generate sample datasets for GCS upload testing."""
    print("SensorScope Dataset Generator")
    print("=" * 40)
    print()
    print("Generating sample sensor datasets for Sita's analysis...")
    print()
    
    # Create datasets in current directory
    datasets = create_sample_datasets_directory("./")
    
    print("Generated datasets:")
    for name, path in datasets.items():
        file_size = os.path.getsize(path) / 1024  # KB
        with open(path, 'r') as f:
            lines = sum(1 for _ in f) - 1  # Subtract header
        print(f"   {name}: {path} ({file_size:.1f}KB, {lines} readings)")
    
    print()
    print("Upload to Google Cloud Storage:")
    print("   gsutil cp *.csv gs://YOUR_BUCKET_NAME/datasets/")
    print("   gsutil cp *_metadata.json gs://YOUR_BUCKET_NAME/datasets/")
    print()
    print("Test with Cloud Function:")
    print("   curl -X POST https://YOUR_FUNCTION_URL \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print("       \"gcs_bucket\": \"YOUR_BUCKET_NAME\",")
    print("       \"gcs_file_path\": \"datasets/coffee_shop_sensors.csv\",")
    print("       \"n_components\": 5")
    print("     }'")
    print()
    print("Dataset Types:")
    print("   - coffee_shop_sensors.csv: Realistic 20-sensor coffee shop data")
    print("   - basic_sensors.csv: Strong redundancy patterns (good compression)")
    print("   - complex_sensors.csv: Minimal redundancy (limited compression)")

if __name__ == "__main__":
    main()
