#!/usr/bin/env pwsh
# Master Startup Script - Starts Everything
# Run this to start the complete Financial Copilot system

Write-Host "🚀 FINANCIAL COPILOT - COMPLETE STARTUP" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator (recommended for Cloudflare)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠️  Not running as Administrator. Some features may not work properly." -ForegroundColor Yellow
    Write-Host "   Tip: Right-click and 'Run as Administrator' for best results." -ForegroundColor Gray
    Write-Host ""
}

Write-Host "Starting all services..." -ForegroundColor Green
Write-Host ""

# 1. Start Ollama in a new window
Write-Host "1️⃣ Starting Ollama LLM service..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "ollama serve" -WindowStyle Normal
Start-Sleep -Seconds 3

# 2. Start Backend in a new window
Write-Host "2️⃣ Starting FastAPI Backend..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal
Start-Sleep -Seconds 5

# 3. Start Cloudflare Tunnel in a new window
Write-Host "3️⃣ Starting Cloudflare Tunnel..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "C:\cloudflared\cloudflared.exe tunnel run ai-finance" -WindowStyle Normal
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "✅ ALL SERVICES STARTED!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Mobile App Configuration:" -ForegroundColor Cyan
Write-Host "   - URL: https://ai-finance.sohamm.xyz" -ForegroundColor White
Write-Host "   - The app should automatically connect to this URL" -ForegroundColor Gray
Write-Host ""
Write-Host "🖥️ Local Testing:" -ForegroundColor Cyan
Write-Host "   - Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Cyan
Write-Host "   - Ollama: Check the Ollama window for LLM status" -ForegroundColor Gray
Write-Host "   - Backend: Check the FastAPI window for API logs" -ForegroundColor Gray
Write-Host "   - Cloudflare: Check the tunnel window for connection status" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  To stop all services, close each window or press Ctrl+C in each" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
