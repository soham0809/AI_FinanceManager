#!/usr/bin/env pwsh
# Quick Start Script - Corrected Port Configuration

Write-Host "🚀 Starting AI Financial Co-Pilot..." -ForegroundColor Green
Write-Host "=" -repeat 50 -ForegroundColor Blue

# Check if Ollama is running
Write-Host "1. 🤖 Checking Ollama..." -ForegroundColor Yellow
try {
    $ollamaCheck = ollama ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Ollama is running" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Starting Ollama..." -ForegroundColor Yellow
        Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow
        Start-Sleep -Seconds 3
    }
} catch {
    Write-Host "   ❌ Ollama not found. Please install Ollama first." -ForegroundColor Red
    exit 1
}

# Start Backend on Port 8000 (to match Cloudflare)
Write-Host "2. 🖥️  Starting Backend on Port 8000..." -ForegroundColor Yellow
Set-Location "backend"
Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" -NoNewWindow
Set-Location ".."
Start-Sleep -Seconds 5

# Test backend health
Write-Host "3. 🏥 Testing Backend Health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
    Write-Host "   ✅ Backend is healthy: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Backend health check failed: $_" -ForegroundColor Red
    Write-Host "   💡 Make sure backend started successfully on port 8000" -ForegroundColor Yellow
}

# Start Cloudflare Tunnel
Write-Host "4. ☁️  Starting Cloudflare Tunnel..." -ForegroundColor Yellow
Start-Process -FilePath "C:\cloudflared\cloudflared.exe" -ArgumentList "tunnel", "run", "ai-finance" -NoNewWindow
Start-Sleep -Seconds 5

# Test Cloudflare connection
Write-Host "5. 🌐 Testing Cloudflare Connection..." -ForegroundColor Yellow
try {
    $cloudflareHealth = Invoke-RestMethod -Uri "https://ai-finance.sohamm.xyz/health" -TimeoutSec 15
    Write-Host "   ✅ Cloudflare tunnel is working: $($cloudflareHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Cloudflare tunnel might still be connecting..." -ForegroundColor Yellow
    Write-Host "   💡 Wait 30 seconds and try accessing https://ai-finance.sohamm.xyz/health manually" -ForegroundColor Yellow
}

# Prepare Flutter
Write-Host "6. 📱 Preparing Flutter App..." -ForegroundColor Yellow
Set-Location "mobile_app"
flutter clean | Out-Null
flutter pub get | Out-Null
Write-Host "   ✅ Flutter dependencies updated" -ForegroundColor Green

Write-Host "" 
Write-Host "🎉 Startup Complete!" -ForegroundColor Green
Write-Host "=" -repeat 50 -ForegroundColor Blue
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Run 'flutter run' in mobile_app directory" -ForegroundColor White
Write-Host "   2. Backend: http://localhost:8000" -ForegroundColor White  
Write-Host "   3. Cloudflare: https://ai-finance.sohamm.xyz" -ForegroundColor White
Write-Host "   4. Check health: https://ai-finance.sohamm.xyz/health" -ForegroundColor White
Write-Host ""

Set-Location ".."
