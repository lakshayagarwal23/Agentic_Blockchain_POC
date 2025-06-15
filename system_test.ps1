Write-Host "🧪 RWA Tokenization System Test"
Write-Host "================================"

# 1. Environment check
Write-Host "1. Environment Check..."
if (Test-Path "venv" -and Test-Path "app\main.py" -and Test-Path "requirements.txt") {
    Write-Host "✅ Project structure OK"
} else {
    Write-Host "❌ Project structure incomplete"
    exit 1
}

# 2. Dependencies check
Write-Host "2. Dependencies Check..."
& "venv\Scripts\Activate.ps1"
pip install -r requirements.txt
python tests\test_basic.py > $null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies OK"
} else {
    Write-Host "❌ Dependencies failed"
    exit 1
}

# 3. Database check
Write-Host "3. Database Check..."
python init_db.py > $null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database OK"
} else {
    Write-Host "❌ Database failed"
    exit 1
}

# 4. Application startup
Write-Host "4. Application Startup..."
$process = Start-Process -FilePath "python" -ArgumentList "app\main.py" -PassThru
Start-Sleep -Seconds 5

# 5. Health check
Write-Host "5. Health Check..."
try {
    & ".\health_check.bat" > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Application health OK"
    } else {
        Write-Host "❌ Application health failed"
        Stop-Process -Id $process.Id -Force
        exit 1
    }
} catch {
    Write-Host "❌ Health check script failed"
    Stop-Process -Id $process.Id -Force
    exit 1
}

# 6. Performance check
Write-Host "6. Performance Check..."
python performance_test.py > $null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Performance OK"
} else {
    Write-Host "⚠ Performance issues detected"
}

# Clean up
Stop-Process -Id $process.Id -Force
Write-Host ""
Write-Host "🎉 System test completed successfully!"
Write-Host "🚀 Your RWA Tokenization POC is ready to use!"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Start the application: ./run.ps1"
Write-Host "2. Open browser: http://localhost:5000"
Write-Host "3. Begin tokenizing assets!"
