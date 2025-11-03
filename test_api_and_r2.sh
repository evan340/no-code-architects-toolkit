#!/bin/bash
# Quick API and R2 Integration Test
# Usage: ./test_api_and_r2.sh

set -e

API_URL="https://nca1.evan.cx"
API_KEY="48LKJUHkkhf44t"

echo "=========================================="
echo "NCA Toolkit API + R2 Integration Test"
echo "=========================================="
echo ""

# Test 1: Authentication Check
echo "Test 1: Authentication Check"
echo "Command: GET /v1/toolkit/authenticate"
echo ""

auth_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X GET "$API_URL/v1/toolkit/authenticate" \
  -H "X-API-Key: $API_KEY")

http_code=$(echo "$auth_response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$auth_response" | grep -v "HTTP_CODE")

if [ "$http_code" = "200" ]; then
    echo "✅ Authentication successful!"
    echo "Response: $body"
else
    echo "❌ Authentication failed"
    echo "HTTP Code: $http_code"
    echo "Response: $body"
    exit 1
fi

echo ""
echo "=========================================="
echo ""

# Test 2: API Health Check (uploads to R2)
echo "Test 2: API Health Check + R2 Upload"
echo "Command: GET /v1/toolkit/test"
echo ""

response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X GET "$API_URL/v1/toolkit/test" \
  -H "X-API-Key: $API_KEY")

http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$response" | grep -v "HTTP_CODE")

if [ "$http_code" = "200" ]; then
    echo "✅ API test passed and file uploaded to R2!"
    echo "Response: $body" | head -c 200
    echo ""

    # Try to extract URL if it's in the response
    file_url=$(echo "$body" | grep -o 'https://[^"]*\.txt' | head -1)
    if [ -z "$file_url" ]; then
        file_url=$(echo "$body" | grep -o 'https://[^"]*success\.txt' | head -1)
    fi

    if [ -n "$file_url" ]; then
        echo "📁 File URL: $file_url"
        echo "Verifying file is accessible..."
        if curl -s -I "$file_url" | grep -q "200\|HTTP/2 200"; then
            echo "✅ File is publicly accessible!"
        else
            echo "⚠️  File uploaded but may not be public"
        fi
    fi
else
    echo "❌ API test failed"
    echo "HTTP Code: $http_code"
    echo "Response: $body"
    exit 1
fi

echo ""
echo "=========================================="
echo ""

# Test 3: Video Thumbnail (R2 Upload Test)
echo "Test 3: Video Thumbnail → R2 Upload"
echo "Command: POST /v1/video/thumbnail"
echo ""

thumbnail_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$API_URL/v1/video/thumbnail" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://cdn01.evan.cx/c729f79e-6985-4228-a678-1151c350c3d0_output_0.mp4",
    "second": 2
  }')

http_code=$(echo "$thumbnail_response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$thumbnail_response" | grep -v "HTTP_CODE")

if [ "$http_code" = "200" ]; then
    echo "✅ Thumbnail generated and uploaded to R2!"
    echo "Response: $body" | head -c 200
    echo ""

    thumbnail_url=$(echo "$body" | grep -o 'https://[^"]*\.jpg' | head -1)
    if [ -n "$thumbnail_url" ]; then
        echo "📸 Thumbnail URL: $thumbnail_url"
        echo "Verifying thumbnail is accessible..."
        if curl -s -I "$thumbnail_url" | grep -q "200\|HTTP/2 200"; then
            echo "✅ Thumbnail is publicly accessible!"
        else
            echo "⚠️  Thumbnail uploaded but may not be public"
        fi
    fi
else
    echo "❌ Thumbnail generation failed"
    echo "HTTP Code: $http_code"
    echo "Response: $body"
fi

echo ""
echo "=========================================="
echo "✅ Test Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Check server logs for: 'Detected Cloudflare R2 storage provider'"
echo "2. Check server logs for: 'Uploaded to R2 bucket (no ACL)'"
echo "3. Verify files in Cloudflare R2 dashboard: bucket 'media-cdn-jsnews'"
echo ""
echo "Log check commands:"
echo "  grep 'Detected Cloudflare R2' /var/log/your-app.log"
echo "  grep 'Uploaded to R2 bucket' /var/log/your-app.log"
