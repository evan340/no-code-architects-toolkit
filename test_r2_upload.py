#!/usr/bin/env python3
"""
Simple R2 Upload Test Script
Tests Cloudflare R2 connection and upload functionality
"""

import os
import sys
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up environment variables from .env.test
from dotenv import load_dotenv
load_dotenv('.env.test')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our cloud storage module
from services.cloud_storage import upload_file, get_storage_provider

def create_test_file():
    """Create a small test file to upload"""
    test_file_path = '/tmp/r2_test_upload.txt'
    with open(test_file_path, 'w') as f:
        f.write('This is a test file for R2 upload verification.\n')
        f.write(f'Timestamp: {os.popen("date").read().strip()}\n')
    logger.info(f"Created test file: {test_file_path}")
    return test_file_path

def test_r2_connection():
    """Test R2 connection and provider detection"""
    logger.info("=" * 60)
    logger.info("R2 CONNECTION TEST")
    logger.info("=" * 60)

    # Check environment variables
    logger.info("\nEnvironment Configuration:")
    logger.info(f"  S3_ENDPOINT_URL: {os.getenv('S3_ENDPOINT_URL')}")
    logger.info(f"  S3_REGION: {os.getenv('S3_REGION')}")
    logger.info(f"  S3_BUCKET_NAME: {os.getenv('S3_BUCKET_NAME')}")
    logger.info(f"  S3_ACCESS_KEY: {os.getenv('S3_ACCESS_KEY')[:10]}..." if os.getenv('S3_ACCESS_KEY') else "  S3_ACCESS_KEY: Not set")

    # Test provider detection
    logger.info("\nTesting storage provider detection...")
    try:
        provider = get_storage_provider()
        logger.info(f"✓ Provider detected successfully: {type(provider).__name__}")
    except Exception as e:
        logger.error(f"✗ Provider detection failed: {e}")
        return False

    return True

def test_r2_upload():
    """Test file upload to R2"""
    logger.info("\n" + "=" * 60)
    logger.info("R2 UPLOAD TEST")
    logger.info("=" * 60)

    # Create test file
    test_file = create_test_file()

    # Upload to R2
    logger.info("\nUploading test file to R2...")
    try:
        file_url = upload_file(test_file)
        logger.info(f"✓ Upload successful!")
        logger.info(f"  File URL: {file_url}")

        # Clean up local test file
        os.remove(test_file)
        logger.info(f"  Cleaned up local test file")

        return file_url
    except Exception as e:
        logger.error(f"✗ Upload failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def main():
    """Run all R2 tests"""
    logger.info("\n🚀 Starting R2 Integration Tests\n")

    # Test 1: Connection and provider detection
    if not test_r2_connection():
        logger.error("\n❌ R2 connection test failed!")
        sys.exit(1)

    # Test 2: File upload
    file_url = test_r2_upload()
    if not file_url:
        logger.error("\n❌ R2 upload test failed!")
        sys.exit(1)

    # Success!
    logger.info("\n" + "=" * 60)
    logger.info("✅ ALL TESTS PASSED!")
    logger.info("=" * 60)
    logger.info(f"\nR2 integration is working correctly.")
    logger.info(f"Test file uploaded to: {file_url}")
    logger.info("\nYou can now safely deploy to production!\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
