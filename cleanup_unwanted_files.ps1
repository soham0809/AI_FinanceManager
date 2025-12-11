# Cleanup Script for Final Year Project
# This script identifies and optionally removes unwanted files

Write-Host "=== Final Year Project Cleanup Script ===" -ForegroundColor Green

$projectRoot = "c:\Users\soham\Desktop\BASIC_CODES\final_year\final_year"

# Files that can be safely removed
$unwantedFiles = @(
    "$projectRoot\Docs\main.log",
    "$projectRoot\test_complete_flow.py",
    "$projectRoot\test_cloudflare.py", 
    "$projectRoot\test_chatbot.py",
    "$projectRoot\test_auth.py"
)

# Directories that can be cleaned (build artifacts)
$buildDirs = @(
    "$projectRoot\mobile_app\build"
)

Write-Host "`n=== Unwanted Files Found ===" -ForegroundColor Yellow
$filesToRemove = @()
foreach ($file in $unwantedFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "  $file ($([math]::Round($size/1KB, 2)) KB)" -ForegroundColor Red
        $filesToRemove += $file
    }
}

Write-Host "`n=== Build Directories Found ===" -ForegroundColor Yellow
$dirsToClean = @()
foreach ($dir in $buildDirs) {
    if (Test-Path $dir) {
        $size = (Get-ChildItem $dir -Recurse | Measure-Object -Property Length -Sum).Sum
        Write-Host "  $dir ($([math]::Round($size/1MB, 2)) MB)" -ForegroundColor Red
        $dirsToClean += $dir
    }
}

$totalFiles = $filesToRemove.Count
$totalDirs = $dirsToClean.Count

Write-Host "`n=== Summary ===" -ForegroundColor Green
Write-Host "Files to remove: $totalFiles"
Write-Host "Build directories to clean: $totalDirs"

if ($totalFiles -eq 0 -and $totalDirs -eq 0) {
    Write-Host "No unwanted files found. Project is clean!" -ForegroundColor Green
    exit 0
}

Write-Host "`nTo remove these files, run:" -ForegroundColor Cyan
Write-Host "  .\cleanup_unwanted_files.ps1 -Execute" -ForegroundColor White

# Check if -Execute parameter was passed
param([switch]$Execute)

if ($Execute) {
    Write-Host "`n=== Removing Files ===" -ForegroundColor Red
    
    foreach ($file in $filesToRemove) {
        try {
            Remove-Item $file -Force
            Write-Host "  Removed: $file" -ForegroundColor Green
        } catch {
            Write-Host "  Failed to remove: $file - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    foreach ($dir in $dirsToClean) {
        try {
            Remove-Item $dir -Recurse -Force
            Write-Host "  Cleaned: $dir" -ForegroundColor Green
        } catch {
            Write-Host "  Failed to clean: $dir - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Write-Host "`nCleanup completed!" -ForegroundColor Green
}
