# Registra una tarea de Windows que publica las stats de Claude Code cada hora.
# Uso (PowerShell):  .\scripts\install-scheduled-task.ps1
$ErrorActionPreference = "Stop"
$TaskName = "DevJhere-ProfileReadme"
$Script = Join-Path $PSScriptRoot "publish-claude-code.py"
$LogDir = Join-Path $env:LOCALAPPDATA "profile-readme"
New-Item -ItemType Directory -Force $LogDir | Out-Null
$Python = (Get-Command python).Source

$Action = New-ScheduledTaskAction -Execute "cmd.exe" `
  -Argument "/c `"`"$Python`" `"$Script`" >> `"$LogDir\publish.log`" 2>&1`"" `
  -WorkingDirectory $PSScriptRoot
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force | Out-Null
Write-Host "Tarea '$TaskName' instalada (cada hora). Log: $LogDir\publish.log"
