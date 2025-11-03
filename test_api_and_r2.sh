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

# Test 1: API Health Check
echo "Test 1: API Health Check"
echo "Command: POST /v1/toolkit/test"
echo ""

response=$(curl -s -X POST "$API_URL/v1/toolkit/test" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json")

if echo "$response" | grep -q "success\|working"; then
    echo "✅ API is working!"
    echo "Response: $response" | head -c 200
    echo ""
else
    echo "❌ API test failed"
    echo "Response: $response"
    exit 1
fi

echo ""
echo "=========================================="
echo ""

# Test 2: Video Thumbnail (R2 Upload Test)
echo "Test 2: Video Thumbnail → R2 Upload"
echo "Command: POST /v1/video/thumbnail"
echo ""

thumbnail_response=$(curl -s -X POST "$API_URL/v1/video/thumbnail" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://cdn01.evan.cx/c729f79e-6985-4228-a678-1151c350c3d0_output_0.mp4",
    "time": "00:00:02"
  }')

if echo "$thumbnail_response" | grep -q "thumbnail_url\|cdn01.evan.cx"; then
    echo "✅ Thumbnail generated and uploaded to R2!"
    thumbnail_url=$(echo "$thumbnail_response" | grep -o 'https://[^"]*\.jpg' | head -1)
    echo "📸 Thumbnail URL: $thumbnail_url"
    echo ""

    # Verify file is accessible
    echo "Verifying file is accessible..."
    if curl -s -I "$thumbnail_url" | grep -q "200\|HTTP/2 200"; then
        echo "✅ File is publicly accessible!"
    else
        echo "⚠️  File uploaded but may not be public"
    fi
else
    echo "❌ Thumbnail generation failed"
    echo "Response: $thumbnail_response"
fi

echo ""
echo "=========================================="
echo "✅ Test Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Check server logs for: 'Detected Cloudflare R2 storage provider'"
echo "2. Verify files in Cloudflare R2 dashboard: bucket 'media-cdn-jsnews'"
echo "3. Run verify_r2_uploads.py to list recent uploads"
