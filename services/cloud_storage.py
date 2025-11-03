# Copyright (c) 2025 Stephen G. Pope
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.



import os
import logging
from abc import ABC, abstractmethod
from services.gcp_toolkit import upload_to_gcs
from services.s3_toolkit import upload_to_s3
from config import validate_env_vars
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def parse_s3_url(s3_url):
    """Parse S3 URL to extract bucket name, region, and endpoint URL."""
    parsed_url = urlparse(s3_url)
    
    # Extract bucket name from the host
    bucket_name = parsed_url.hostname.split('.')[0]
    
    # Extract region from the host
    region = parsed_url.hostname.split('.')[1]
    
    return bucket_name, region

class CloudStorageProvider(ABC):
    @abstractmethod
    def upload_file(self, file_path: str) -> str:
        pass

class GCPStorageProvider(CloudStorageProvider):
    def __init__(self):
        self.bucket_name = os.getenv('GCP_BUCKET_NAME')

    def upload_file(self, file_path: str) -> str:
        return upload_to_gcs(file_path, self.bucket_name)

class S3CompatibleProvider(CloudStorageProvider):
    def __init__(self):

        self.endpoint_url = os.getenv('S3_ENDPOINT_URL')
        self.access_key = os.getenv('S3_ACCESS_KEY')
        self.secret_key = os.getenv('S3_SECRET_KEY')
        self.bucket_name = os.environ.get('S3_BUCKET_NAME', '')
        self.region = os.environ.get('S3_REGION', '')
        
        # Check if endpoint is Digital Ocean and bucket name or region is missing
        if (self.endpoint_url and 
            'digitalocean' in self.endpoint_url.lower() and 
            (not self.bucket_name or not self.region)):
            
            logger.info("Digital Ocean endpoint detected with missing bucket or region. Extracting from URL.")
            try:
                # Extract bucket name and region from URL like https://sgp-labs.nyc3.digitaloceanspaces.com
                parsed_url = urlparse(self.endpoint_url)
                hostname_parts = parsed_url.hostname.split('.')
                
                # The first part is the bucket name (sgp-labs)
                if not self.bucket_name:
                    self.bucket_name = hostname_parts[0]
                    logger.info(f"Extracted bucket name from URL: {self.bucket_name}")
                
                # The second part is the region (nyc3)
                if not self.region:
                    self.region = hostname_parts[1]
                    logger.info(f"Extracted region from URL: {self.region}")
                
            except Exception as e:
                logger.warning(f"Failed to parse Digital Ocean URL: {e}. Using provided values.")

    def upload_file(self, file_path: str) -> str:
        return upload_to_s3(file_path, self.endpoint_url, self.access_key, self.secret_key, self.bucket_name, self.region)

def get_storage_provider() -> CloudStorageProvider:
    """Get the appropriate cloud storage provider based on environment variables.

    Supports:
    - Cloudflare R2 (S3-compatible, detected by endpoint or region: auto, wnam, enam, weur, eeur, apac)
    - DigitalOcean Spaces (detected by digitalocean in endpoint)
    - Amazon S3 / MinIO / Generic S3-compatible
    - Google Cloud Storage
    """

    if os.getenv('S3_ENDPOINT_URL'):
        endpoint_url = os.getenv('S3_ENDPOINT_URL').lower()
        region = os.getenv('S3_REGION', '').lower()

        # R2 region codes: auto, wnam (Western North America), enam (Eastern North America),
        # weur (Western Europe), eeur (Eastern Europe), apac (Asia-Pacific)
        r2_regions = ['auto', 'wnam', 'enam', 'weur', 'eeur', 'apac']

        if 'r2.cloudflarestorage.com' in endpoint_url or region in r2_regions:
            # Cloudflare R2 (with or without custom domain)
            validate_env_vars('R2')
            logger.info("Detected Cloudflare R2 storage provider")
        elif 'digitalocean' in endpoint_url:
            # DigitalOcean Spaces
            validate_env_vars('S3_DO')
            logger.info("Detected DigitalOcean Spaces storage provider")
        else:
            # Generic S3-compatible (MinIO, AWS S3, etc.)
            validate_env_vars('S3')
            logger.info("Detected S3-compatible storage provider")

        return S3CompatibleProvider()

    if os.getenv('GCP_BUCKET_NAME'):
        validate_env_vars('GCP')
        logger.info("Detected Google Cloud Storage provider")
        return GCPStorageProvider()

    raise ValueError(f"No cloud storage settings provided.")

def upload_file(file_path: str) -> str:
    provider = get_storage_provider()
    try:
        logger.info(f"Uploading file to cloud storage: {file_path}")
        url = provider.upload_file(file_path)
        logger.info(f"File uploaded successfully: {url}")
        return url
    except Exception as e:
        logger.error(f"Error uploading file to cloud storage: {e}")
        raise
    