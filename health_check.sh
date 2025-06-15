#!/bin/bash
BASE_URL="http://localhost:5000"
echo "🏥 RWA Tokenization Health Check"
echo "================================"

# Test 1: Health endpoint
echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "$BASE_URL/api/health")
if echo "$HEALTH_RESPONSE" | grep -q '"status": "healthy"'; then
  echo "✅ Health endpoint: OK"
else
  echo "❌ Health endpoint: FAILED"
  echo "Response: $HEALTH_RESPONSE"
fi

# Test 2: Main page
echo "Testing main page..."
MAIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
if [ "$MAIN_RESPONSE" = "200" ]; then
  echo "✅ Main page: OK"
else
  echo "❌ Main page: FAILED (HTTP $MAIN_RESPONSE)"
fi

# Test 3: Static files
echo "Testing static files..."
CSS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/static/css/style.css")
JS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/static/js/app.js")
if [ "$CSS_RESPONSE" = "200" ] && [ "$JS_RESPONSE" = "200" ]; then
  echo "✅ Static files: OK"
else
  echo "❌ Static files: FAILED (CSS: $CSS_RESPONSE, JS: $JS_RESPONSE)"
fi

# Test 4: Database connectivity
echo "Testing database connectivity..."
STATS_RESPONSE=$(curl -s "$BASE_URL/api/stats")
if echo "$STATS_RESPONSE" | grep -q '"total_assets"'; then
  echo "✅ Database: OK"
else
  echo "❌ Database: FAILED"
  echo "Response: $STATS_RESPONSE"
fi

# Summary
echo -e "\n📊 System Status Summary:"
echo "Time: $(date)"
echo "Application URL: $BASE_URL"
