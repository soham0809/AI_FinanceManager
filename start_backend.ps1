#!/usr/bin/env pwsh
# Backend Startup Script for Financial Copilot
# This script starts all necessary services

Write-Host "🚀 Starting Financial Copilot Backend Services" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan

# Start Ollama service
Write-Host "`n📦 Starting Ollama service..." -ForegroundColor Yellow
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized
Start-Sleep -Seconds 3

# Navigate to backend directory
Set-Location -Path "backend"

# Start FastAPI backend
Write-Host "`n🌐 Starting FastAPI backend on port 8000..." -ForegroundColor Yellow
Write-Host "   Backend will be available at: http://localhost:8000" -ForegroundColor Gray

# Run uvicorn with reload for development
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Write-Host "`n✅ Backend services started successfully!" -ForegroundColor Green
