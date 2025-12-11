#!/usr/bin/env pwsh
# Cloudflare Tunnel Startup Script
# This script starts the Cloudflare tunnel for remote access

Write-Host "☁️ Starting Cloudflare Tunnel" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Gray

Write-Host "`n📡 Starting tunnel: ai-finance" -ForegroundColor Yellow
Write-Host "   Your app will be available at: https://ai-finance.sohamm.xyz" -ForegroundColor Green

# Start Cloudflare tunnel
C:\cloudflared\cloudflared.exe tunnel run ai-finance

Write-Host "`n✅ Cloudflare tunnel is running!" -ForegroundColor Green
