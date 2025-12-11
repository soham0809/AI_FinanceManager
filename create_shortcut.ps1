# Create Desktop Shortcut for AI Finance Manager
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\AI Finance Manager.lnk")
$Shortcut.TargetPath = "$PSScriptRoot\start_system.bat"
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "Start AI Finance Manager System"
$Shortcut.IconLocation = "shell32.dll,25"  # Computer icon
$Shortcut.Save()

Write-Host "✅ Desktop shortcut created: 'AI Finance Manager'" -ForegroundColor Green
Write-Host "📍 Location: $Home\Desktop\AI Finance Manager.lnk" -ForegroundColor Gray
