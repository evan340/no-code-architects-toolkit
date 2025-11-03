#!/usr/bin/env python3
"""
Debug R2 Authentication
Tests different R2 configurations to identify permission issues
"""

import boto3
import logging
import os
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Credentials from environment variables
ACCESS_KEY = os.environ.get('S3_ACCESS_KEY', 'your_access_key_here')
SECRET_KEY = os.environ.get('S3_SECRET_KEY', 'your_secret_key_here')
BUCKET = os.environ.get('S3_BUCKET_NAME', 'your-bucket-name')

# Get endpoints from environment or use defaults
R2_ENDPOINT = os.environ.get('R2_ENDPOINT', 'https://your-account-id.r2.cloudflarestorage.com')
CUSTOM_DOMAIN = os.environ.get('S3_ENDPOINT_URL', 'https://cdn.example.com')

# Test both endpoints
# You can override these with environment variables:
# - R2_ENDPOINT: Your official R2 endpoint
# - S3_ENDPOINT_URL: Your custom domain (if configured)
# - S3_REGION: R2 region (auto, wnam, enam, weur, eeur, apac)
endpoints = [
    ("Official R2", R2_ENDPOINT, "auto"),
    ("Custom Domain", CUSTOM_DOMAIN, os.environ.get('S3_REGION', 'auto'))
]

for name, endpoint, region in endpoints:
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Endpoint: {endpoint}")
    print(f"Region: {region}")
    print(f"{'='*60}\n")

    try:
        # Create client
        client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=region
        )

        # Test 1: List buckets
        print("Test 1: List buckets...")
        try:
            response = client.list_buckets()
            print(f"✓ List buckets successful")
            print(f"  Buckets: {[b['Name'] for b in response.get('Buckets', [])]}")
        except ClientError as e:
            print(f"✗ List buckets failed: {e.response['Error']['Code']}")

        # Test 2: Head bucket
        print(f"\nTest 2: Head bucket '{BUCKET}'...")
        try:
            client.head_bucket(Bucket=BUCKET)
            print(f"✓ Bucket exists and is accessible")
        except ClientError as e:
            print(f"✗ Head bucket failed: {e.response['Error']['Code']}")

        # Test 3: List objects
        print(f"\nTest 3: List objects in bucket...")
        try:
            response = client.list_objects_v2(Bucket=BUCKET, MaxKeys=5)
            count = response.get('KeyCount', 0)
            print(f"✓ List objects successful")
            print(f"  Objects in bucket: {count}")
            if count > 0:
                print(f"  Sample files: {[obj['Key'] for obj in response.get('Contents', [])[:3]]}")
        except ClientError as e:
            print(f"✗ List objects failed: {e.response['Error']['Code']}")

        # Test 4: Put object (simple)
        print(f"\nTest 4: Upload test object...")
        test_key = "test_upload_debug.txt"
        test_content = b"R2 upload test from debug script"

        try:
            client.put_object(
                Bucket=BUCKET,
                Key=test_key,
                Body=test_content
            )
            print(f"✓ Upload successful!")
            print(f"  File: {test_key}")
            print(f"  URL: {endpoint}/{BUCKET}/{test_key}")

            # Try to delete the test file
            try:
                client.delete_object(Bucket=BUCKET, Key=test_key)
                print(f"  Cleaned up test file")
            except:
                pass

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            print(f"✗ Upload failed: {error_code}")
            print(f"  Message: {error_msg}")

            # Check specific error details
            if error_code == 'AccessDenied':
                print(f"  Issue: Token lacks write permissions")
            elif error_code == 'NoSuchBucket':
                print(f"  Issue: Bucket '{BUCKET}' doesn't exist")
            elif error_code == 'SignatureDoesNotMatch':
                print(f"  Issue: Invalid credentials")

    except Exception as e:
        print(f"✗ Unexpected error: {e}")

print(f"\n{'='*60}")
print("Debug complete")
print(f"{'='*60}")
