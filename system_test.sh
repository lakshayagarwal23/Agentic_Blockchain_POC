#!/bin/bash
echo "🧪 RWA Tokenization System Test"
echo "================================"

echo "1. Environment Check..."
if [ -d "venv" ] && [ -f "app/main.py" ] && [ -f "requirements.txt" ]; then
  echo "✅ Project structure OK"
else
  echo "❌ Project structure incomplete"
  exit 1
fi

# Test 2: Dependencies check
echo "2. Dependencies Check..."
. venv/Scripts/activate
python tests/test_basic.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Dependencies OK"
else
    echo "❌ Dependencies failed"
    exit 1
fi


echo "3. Database Check..."
python init_db.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Database OK"
else
  echo "❌ Database failed"
  exit 1
fi

echo "4. Application Startup..."
python app/main.py &
APP_PID=$!
sleep 5

echo "5. Health Check..."
./health_check.sh > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Application health OK"
else
  echo "❌ Application health failed"
  kill $APP_PID 2>/dev/null
  exit 1
fi

echo "6. Performance Check..."
python performance_test.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Performance OK"
else
  echo "⚠ Performance issues detected"
fi

kill $APP_PID 2>/dev/null
wait $APP_PID 2>/dev/null

echo ""
echo "🎉 System test completed successfully!"
echo "🚀 Your RWA Tokenization POC is ready to use!"
echo ""
echo "Next steps:"
echo "1. Start the application: ./run.sh"
echo "2. Open browser: http://localhost:5000"
echo "3. Begin tokenizing assets!"
