#!/bin/bash
LOG_FILE="logs/app.log"
echo "📊 RWA Tokenization Log Analysis"
echo "================================"
if [ ! -f "$LOG_FILE" ]; then
  echo "❌ Log file not found: $LOG_FILE"
  exit 1
fi
echo "📈 Recent Activity (Last 50 lines):"
tail -50 "$LOG_FILE"

echo -e "\n🔍 Error Summary:"
grep -c "ERROR" "$LOG_FILE" && echo "Total errors found" || echo "No errors found"

echo -e "\n✅ Success Summary:"
grep -c "Asset created successfully" "$LOG_FILE" && echo "Assets created" || echo "No assets"
grep -c "Verification completed" "$LOG_FILE" && echo "Verifications completed" || echo "No verifications"
grep -c "Tokenization completed" "$LOG_FILE" && echo "Tokenizations completed" || echo "No tokenizations"

echo -e "\n🕒 Recent Errors (Last 10):"
grep "ERROR" "$LOG_FILE" | tail -10
