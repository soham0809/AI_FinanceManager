# AI Finance Manager - System Startup Script
# This script kills existing processes and starts all required services

Write-Host "🚀 Starting AI Finance Manager System..." -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Function to kill processes safely
function Kill-ProcessSafely {
    param($ProcessName)
    try {
        $processes = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
        if ($processes) {
            Write-Host "🔄 Killing existing $ProcessName processes..." -ForegroundColor Yellow
            Stop-Process -Name $ProcessName -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
            Write-Host "✅ $ProcessName processes terminated" -ForegroundColor Green
        } else {
            Write-Host "ℹ️  No existing $ProcessName processes found" -ForegroundColor Gray
        }
    } catch {
        Write-Host "⚠️  Could not kill $ProcessName processes: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Step 1: Kill existing processes
Write-Host "Step 1: Cleaning up existing processes..." -ForegroundColor Cyan
Kill-ProcessSafely "python"
Kill-ProcessSafely "ollama"
Kill-ProcessSafely "cloudflared"

Write-Host ""
Write-Host "⏳ Waiting 3 seconds for processes to fully terminate..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Step 2: Start Ollama
Write-Host "🧠 Step 2: Starting Ollama AI Server..." -ForegroundColor Cyan
try {
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Normal
    Write-Host "✅ Ollama server started" -ForegroundColor Green
    Write-Host "   - Model: llama3.1:latest" -ForegroundColor Gray
    Write-Host "   - Host: http://localhost:11434" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed to start Ollama: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Please ensure Ollama is installed and in PATH" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "⏳ Waiting 5 seconds for Ollama to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 3: Start Backend
Write-Host "⚙️  Step 3: Starting FastAPI Backend..." -ForegroundColor Cyan
try {
    $backendPath = Join-Path $PSScriptRoot "backend"
    Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001" -WorkingDirectory $backendPath -WindowStyle Normal
    Write-Host "✅ Backend server started" -ForegroundColor Green
    Write-Host "   - Host: http://0.0.0.0:8001" -ForegroundColor Gray
    Write-Host "   - API Docs: http://localhost:8001/docs" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed to start backend: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "⏳ Waiting 5 seconds for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 4: Start Cloudflare Tunnel
Write-Host "🌐 Step 4: Starting Cloudflare Tunnel..." -ForegroundColor Cyan
try {
    Start-Process -FilePath "C:\cloudflared\cloudflared.exe" -ArgumentList "tunnel", "run", "ai-finance" -WindowStyle Normal
    Write-Host "✅ Cloudflare tunnel started" -ForegroundColor Green
    Write-Host "   - Tunnel: ai-finance" -ForegroundColor Gray
    Write-Host "   - Global URL: https://ai-finance.sohamm.xyz" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed to start Cloudflare tunnel: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   System will work locally on http://localhost:8001" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "⏳ Waiting 5 seconds for tunnel to connect..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 5: System Status Check
Write-Host "🔍 Step 5: System Status Check..." -ForegroundColor Cyan

# Check Ollama
try {
    $ollamaResponse = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 5
    Write-Host "✅ Ollama: Running" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama: Not responding" -ForegroundColor Red
}

# Check Backend
try {
    $backendResponse = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get -TimeoutSec 5
    Write-Host "✅ Backend: Running" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend: Not responding" -ForegroundColor Red
}

# Check Tunnel (this might take longer to connect)
try {
    $tunnelResponse = Invoke-RestMethod -Uri "https://ai-finance.sohamm.xyz/health" -Method Get -TimeoutSec 10
    Write-Host "✅ Cloudflare Tunnel: Connected" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Cloudflare Tunnel: Still connecting (this is normal)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 System Startup Complete!" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Cyan
Write-Host "   🧠 Ollama AI: http://localhost:11434" -ForegroundColor White
Write-Host "   ⚙️  Backend API: http://localhost:8001" -ForegroundColor White
Write-Host "   🌐 Global Access: https://ai-finance.sohamm.xyz" -ForegroundColor White
Write-Host ""
Write-Host "📱 Flutter App:" -ForegroundColor Cyan
Write-Host "   • Set useCloudflare = true for global access" -ForegroundColor White
Write-Host "   • Set useCloudflare = false for local access" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Batch Processing:" -ForegroundColor Cyan
Write-Host "   • Default batch size: 5 transactions" -ForegroundColor White
Write-Host "   • Delay between batches: 2 seconds" -ForegroundColor White
Write-Host "   • API: POST /v1/batch/process-transactions" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
