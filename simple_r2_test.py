#!/usr/bin/env python3
"""
Simple Standalone R2 Upload Test
Tests R2 connection without importing the full application
"""

import os
import boto3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# R2 Configuration (from your credentials)
S3_ENDPOINT_URL = "https://cdn01.evan.cx"
S3_ACCESS_KEY = "2ddba9eb9048fe1afe2844266a68497b"
S3_SECRET_KEY = "45718a8bcf0567f19f90809540d25a7b1f86fa48e6d4e7d659caf860d0cf9017"
S3_REGION = "wnam"
S3_BUCKET_NAME = "media-cdn-jsnews"

def test_r2_detection():
    """Test R2 detection logic"""
    logger.info("=" * 60)
    logger.info("R2 DETECTION TEST")
    logger.info("=" * 60)

    # Check R2 detection logic
    r2_regions = ['auto', 'wnam', 'enam', 'weur', 'eeur', 'apac']
    is_r2 = ('r2.cloudflarestorage.com' in S3_ENDPOINT_URL.lower() or
             (S3_REGION and S3_REGION.lower() in r2_regions))

    logger.info(f"\nEndpoint: {S3_ENDPOINT_URL}")
    logger.info(f"Region: {S3_REGION}")
    logger.info(f"Is R2: {is_r2}")
    logger.info(f"Detection method: {'Region code (wnam)' if S3_REGION.lower() in r2_regions else 'Endpoint URL'}")

    if is_r2:
        logger.info("✓ R2 detected correctly (custom domain with region-based detection)")
    else:
        logger.warning("✗ R2 not detected - this may cause ACL errors")

    return is_r2

def test_r2_connection():
    """Test connection to R2"""
    logger.info("\n" + "=" * 60)
    logger.info("R2 CONNECTION TEST")
    logger.info("=" * 60)

    try:
        # Create boto3 session
        session = boto3.Session(
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION
        )

        # Create S3 client with R2 endpoint
        client = session.client('s3', endpoint_url=S3_ENDPOINT_URL)

        logger.info("\nR2 client created successfully")
        logger.info(f"Bucket: {S3_BUCKET_NAME}")
        logger.info(f"✓ Connection initialized (upload test will verify credentials)")
        return True

    except Exception as e:
        logger.error(f"✗ Connection failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_r2_upload():
    """Test file upload to R2"""
    logger.info("\n" + "=" * 60)
    logger.info("R2 UPLOAD TEST")
    logger.info("=" * 60)

    # Create test file
    test_filename = f"r2_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    test_file_path = f"/tmp/{test_filename}"

    with open(test_file_path, 'w') as f:
        f.write("R2 Upload Test\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Endpoint: {S3_ENDPOINT_URL}\n")
        f.write(f"Region: {S3_REGION}\n")
        f.write(f"Bucket: {S3_BUCKET_NAME}\n")

    logger.info(f"\nCreated test file: {test_file_path}")

    try:
        # Create boto3 session
        session = boto3.Session(
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION
        )

        # Create S3 client
        client = session.client('s3', endpoint_url=S3_ENDPOINT_URL)

        # Check if R2 (to skip ACL)
        r2_regions = ['auto', 'wnam', 'enam', 'weur', 'eeur', 'apac']
        is_r2 = ('r2.cloudflarestorage.com' in S3_ENDPOINT_URL.lower() or
                 (S3_REGION and S3_REGION.lower() in r2_regions))

        # Upload file
        logger.info(f"Uploading to R2 (ACL: {'skipped' if is_r2 else 'public-read'})...")

        with open(test_file_path, 'rb') as data:
            if is_r2:
                # R2: Upload without ACL
                client.upload_fileobj(data, S3_BUCKET_NAME, test_filename)
                logger.info("✓ Uploaded without ACL (R2 mode)")
            else:
                # S3: Upload with ACL
                client.upload_fileobj(data, S3_BUCKET_NAME, test_filename,
                                    ExtraArgs={'ACL': 'public-read'})
                logger.info("✓ Uploaded with public-read ACL (S3 mode)")

        # Construct file URL
        file_url = f"{S3_ENDPOINT_URL}/{S3_BUCKET_NAME}/{test_filename}"

        logger.info(f"✓ Upload successful!")
        logger.info(f"  File: {test_filename}")
        logger.info(f"  URL: {file_url}")

        # Clean up local file
        os.remove(test_file_path)
        logger.info(f"  Cleaned up local test file")

        return file_url

    except Exception as e:
        logger.error(f"✗ Upload failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def main():
    """Run all tests"""
    logger.info("\n🚀 Starting R2 Integration Tests")
    logger.info(f"Endpoint: {S3_ENDPOINT_URL}")
    logger.info(f"Bucket: {S3_BUCKET_NAME}\n")

    # Test 1: R2 Detection
    is_r2 = test_r2_detection()

    # Test 2: Connection
    if not test_r2_connection():
        logger.error("\n❌ R2 connection test FAILED!")
        logger.error("Please check your credentials and bucket configuration.")
        return 1

    # Test 3: Upload
    file_url = test_r2_upload()
    if not file_url:
        logger.error("\n❌ R2 upload test FAILED!")
        return 1

    # Success!
    logger.info("\n" + "=" * 60)
    logger.info("✅ ALL TESTS PASSED!")
    logger.info("=" * 60)
    logger.info(f"\n✓ R2 detection: {'Working' if is_r2 else 'Not detected'}")
    logger.info(f"✓ R2 connection: Working")
    logger.info(f"✓ R2 upload: Working")
    logger.info(f"\nTest file URL: {file_url}")
    logger.info("\n🎉 R2 integration is fully functional!")
    logger.info("You can now safely deploy to production.\n")

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
