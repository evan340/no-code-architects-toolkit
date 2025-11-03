#!/bin/bash
# Comprehensive R2 Integration Test Script
# Run this from an environment that can access nca1.evan.cx

set -e

API_URL="https://nca1.evan.cx"
API_KEY="48LKJUHkkhf44t"

echo "========================================"
echo "R2 Integration Test - No-Code Architects Toolkit"
echo "========================================"
echo ""
echo "API URL: $API_URL"
echo "Testing R2 bucket: media-cdn-jsnews"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Authentication
echo "========================================"
echo "Test 1: Authentication"
echo "========================================"
echo "Endpoint: GET /v1/toolkit/authenticate"
echo ""

auth_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/v1/toolkit/authenticate" \
  -H "X-API-Key: $API_KEY")

http_code=$(echo "$auth_response" | tail -n1)
body=$(echo "$auth_response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Authentication PASSED${NC}"
    echo "Response: $body"
else
    echo -e "${RED}✗ Authentication FAILED${NC}"
    echo "HTTP Code: $http_code"
    echo "Response: $body"
    echo ""
    echo -e "${YELLOW}Note: If you get 403, check Cloudflare Access settings${NC}"
    exit 1
fi

echo ""

# Test 2: File Upload to R2
echo "========================================"
echo "Test 2: File Upload to R2"
echo "========================================"
echo "Endpoint: GET /v1/toolkit/test"
echo ""

test_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/v1/toolkit/test" \
  -H "X-API-Key: $API_KEY")

http_code=$(echo "$test_response" | tail -n1)
body=$(echo "$test_response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ File upload PASSED${NC}"
    echo "Response: $body"

    # Extract URL if it's a direct URL response
    file_url=$(echo "$body" | grep -o 'https://[^"]*' | head -1)

    if [ -n "$file_url" ]; then
        echo ""
        echo "Uploaded file URL: $file_url"

        # Verify file is accessible
        echo "Verifying file accessibility..."
        if curl -s -I "$file_url" | grep -q "200\|HTTP/2 200"; then
            echo -e "${GREEN}✓ File is publicly accessible!${NC}"
        else
            echo -e "${YELLOW}⚠ File uploaded but not publicly accessible (check R2 bucket settings)${NC}"
        fi
    fi
else
    echo -e "${RED}✗ File upload FAILED${NC}"
    echo "HTTP Code: $http_code"
    echo "Response: $body"
    exit 1
fi

echo ""

# Test 3: Video Thumbnail (R2 Upload)
echo "========================================"
echo "Test 3: Video Thumbnail Generation"
echo "========================================"
echo "Endpoint: POST /v1/video/thumbnail"
echo ""

thumbnail_response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/v1/video/thumbnail" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://cdn01.evan.cx/c729f79e-6985-4228-a678-1151c350c3d0_output_0.mp4",
    "second": 2
  }')

http_code=$(echo "$thumbnail_response" | tail -n1)
body=$(echo "$thumbnail_response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Thumbnail generation PASSED${NC}"
    echo "Response: $body"

    # Extract thumbnail URL
    thumbnail_url=$(echo "$body" | grep -o 'https://[^"]*\.jpg' | head -1)

    if [ -n "$thumbnail_url" ]; then
        echo ""
        echo "Thumbnail URL: $thumbnail_url"

        # Verify thumbnail is accessible
        echo "Verifying thumbnail accessibility..."
        if curl -s -I "$thumbnail_url" | grep -q "200\|HTTP/2 200"; then
            echo -e "${GREEN}✓ Thumbnail is publicly accessible!${NC}"
        else
            echo -e "${YELLOW}⚠ Thumbnail uploaded but not publicly accessible${NC}"
        fi
    fi
else
    echo -e "${RED}✗ Thumbnail generation FAILED${NC}"
    echo "HTTP Code: $http_code"
    echo "Response: $body"
    exit 1
fi

echo ""
echo "========================================"
echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
echo "========================================"
echo ""
echo "R2 Integration is working correctly!"
echo ""
echo "Next steps:"
echo "1. Check server logs for: 'Detected Cloudflare R2 storage provider'"
echo "2. Check server logs for: 'Uploaded to R2 bucket (no ACL)'"
echo "3. Verify files in Cloudflare R2 dashboard: bucket 'media-cdn-jsnews'"
echo ""
echo "Log check commands:"
echo "  grep 'Detected Cloudflare R2' /var/log/your-app.log"
echo "  grep 'Uploaded to R2 bucket' /var/log/your-app.log"
echo ""
