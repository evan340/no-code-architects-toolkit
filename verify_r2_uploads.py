#!/usr/bin/env python3
"""
List recent files in R2 bucket to verify uploads
Usage: python3 verify_r2_uploads.py
"""

import boto3
from datetime import datetime, timedelta

# R2 Configuration
ENDPOINT_URL = "https://cdn01.evan.cx"  # or use the official R2 endpoint
ACCESS_KEY = input("Enter R2 Access Key: ")
SECRET_KEY = input("Enter R2 Secret Key: ")
BUCKET_NAME = "media-cdn-jsnews"
REGION = "auto"  # or "wnam"

# Create client
client = boto3.client(
    's3',
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

print(f"\n📦 Checking R2 bucket: {BUCKET_NAME}")
print(f"🌐 Endpoint: {ENDPOINT_URL}\n")
print("=" * 70)

try:
    # List recent objects
    response = client.list_objects_v2(
        Bucket=BUCKET_NAME,
        MaxKeys=20  # Show last 20 files
    )

    if 'Contents' not in response or len(response['Contents']) == 0:
        print("❌ No files found in bucket")
    else:
        files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)

        print(f"✅ Found {len(files)} files (showing up to 20 most recent):\n")

        # Show files from last 24 hours
        now = datetime.now(files[0]['LastModified'].tzinfo)
        yesterday = now - timedelta(days=1)

        recent_count = 0
        for obj in files:
            # Highlight recent uploads
            if obj['LastModified'] > yesterday:
                recent_count += 1
                marker = "🆕"
            else:
                marker = "  "

            size_mb = obj['Size'] / (1024 * 1024)
            print(f"{marker} {obj['Key']}")
            print(f"   Size: {size_mb:.2f} MB | Uploaded: {obj['LastModified']}")
            print()

        print("=" * 70)
        print(f"📊 Summary:")
        print(f"   Total files shown: {len(files)}")
        print(f"   🆕 Recent uploads (last 24h): {recent_count}")
        print(f"\n💡 Files with 🆕 were uploaded in the last 24 hours")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Make sure you have the correct R2 credentials and permissions")
