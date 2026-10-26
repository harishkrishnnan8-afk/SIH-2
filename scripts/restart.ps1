# ==============================================================================
# SIH26263 APAAR Platform - Service Restart Script (PowerShell)
# Stops services safely, verifies port release, and restarts them
# ==============================================================================
[CmdletBinding()]
param(
    [switch]$NoBrowser
)

$ProjectRoot = (Resolve-Path "$PSScriptRoot\..").Path
Set-Location -Path $ProjectRoot

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   APAAR ID-Based Student Data Platform - AICTE Institutions    " -ForegroundColor White
Write-Host "                    System Restart Manager                      " -ForegroundColor DarkCyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[STEP 1/3] Stopping running project services..." -ForegroundColor Yellow
& "$PSScriptRoot\stop.ps1"

Write-Host "[STEP 2/3] Verifying ports are fully released..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# Verify ports are free before restarting
$conns8000 = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
$conns8080 = Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue

if ($conns8000 -or $conns8080) {
    Write-Host "  [!] Ports were not released immediately. Waiting 2 more seconds..." -ForegroundColor DarkYellow
    Start-Sleep -Seconds 2
}

Write-Host "[STEP 3/3] Starting project services..." -ForegroundColor Yellow
if ($NoBrowser) {
    & "$PSScriptRoot\start.ps1" -NoBrowser
} else {
    & "$PSScriptRoot\start.ps1"
}
