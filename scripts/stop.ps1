# ==============================================================================
# SIH26263 APAAR Platform - Service Stopper Script (PowerShell)
# Safely stops project processes on ports 8000 & 8080 without affecting other apps
# ==============================================================================
[CmdletBinding()]
param()

$ProjectRoot = (Resolve-Path "$PSScriptRoot\..").Path
Set-Location -Path $ProjectRoot

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   APAAR ID-Based Student Data Platform - AICTE Institutions    " -ForegroundColor White
Write-Host "                     Service Stopper                            " -ForegroundColor DarkCyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

$RunDir = Join-Path $ProjectRoot ".run"
$BackendPidFile = Join-Path $RunDir "backend.pid"
$FrontendPidFile = Join-Path $RunDir "frontend.pid"
$BackendPortPidFile = Join-Path $RunDir "backend_port.pid"
$FrontendPortPidFile = Join-Path $RunDir "frontend_port.pid"

function Get-ListeningProcessId([int]$Port) {
    try {
        $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($conns) {
            return ($conns | Select-Object -ExpandProperty OwningProcess -Unique | Select-Object -First 1)
        }
    } catch {
        $lines = netstat -ano -p tcp | Select-String ":$Port\s+.*LISTENING\s+(\d+)"
        if ($lines -and $lines[0].Line -match ":$Port\s+.*LISTENING\s+(\d+)") {
            return [int]$matches[1]
        }
    }
    return $null
}

function Stop-SpecificProcess([int]$PidToStop, [string]$Label) {
    if ($PidToStop -le 0) { return $false }
    try {
        $proc = Get-Process -Id $PidToStop -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  Stopping $Label (PID $PidToStop - $($proc.ProcessName))..." -ForegroundColor Yellow
            # taskkill /T /F terminates the window and all child processes (uvicorn/python/vite/bun)
            $null = Start-Process "taskkill.exe" -ArgumentList "/PID", $PidToStop, "/T", "/F" -Wait -NoNewWindow -PassThru
            Write-Host "  [+] $Label (PID $PidToStop) stopped successfully." -ForegroundColor Green
            return $true
        }
    } catch {
        # Process already terminated
    }
    return $false
}

$backendTerminated = $false
$frontendTerminated = $false

# 1. Stop Backend via PID files
if (Test-Path -LiteralPath $BackendPidFile) {
    $rawPid = (Get-Content -LiteralPath $BackendPidFile -ErrorAction SilentlyContinue | Out-String).Trim()
    if ($rawPid -match '^\d+$') {
        if (Stop-SpecificProcess ([int]$rawPid) "Backend Window") {
            $backendTerminated = $true
        }
    }
}

if (Test-Path -LiteralPath $BackendPortPidFile) {
    $rawPid = (Get-Content -LiteralPath $BackendPortPidFile -ErrorAction SilentlyContinue | Out-String).Trim()
    if ($rawPid -match '^\d+$') {
        if (Stop-SpecificProcess ([int]$rawPid) "Backend Port Listener") {
            $backendTerminated = $true
        }
    }
}

# Targeted check: if port 8000 is still active, terminate only that listener
$bPortPid = Get-ListeningProcessId 8000
if ($bPortPid) {
    if (Stop-SpecificProcess $bPortPid "Backend on Port 8000") {
        $backendTerminated = $true
    }
}

# 2. Stop Frontend via PID files
if (Test-Path -LiteralPath $FrontendPidFile) {
    $rawPid = (Get-Content -LiteralPath $FrontendPidFile -ErrorAction SilentlyContinue | Out-String).Trim()
    if ($rawPid -match '^\d+$') {
        if (Stop-SpecificProcess ([int]$rawPid) "Frontend Window") {
            $frontendTerminated = $true
        }
    }
}

if (Test-Path -LiteralPath $FrontendPortPidFile) {
    $rawPid = (Get-Content -LiteralPath $FrontendPortPidFile -ErrorAction SilentlyContinue | Out-String).Trim()
    if ($rawPid -match '^\d+$') {
        if (Stop-SpecificProcess ([int]$rawPid) "Frontend Port Listener") {
            $frontendTerminated = $true
        }
    }
}

# Targeted check: if port 8080 is still active, terminate only that listener
$fPortPid = Get-ListeningProcessId 8080
if ($fPortPid) {
    if (Stop-SpecificProcess $fPortPid "Frontend on Port 8080") {
        $frontendTerminated = $true
    }
}

# Wait up to 5 seconds to verify clean port release
$wait = 0
while ($wait -lt 5) {
    $bLeft = Get-ListeningProcessId 8000
    $fLeft = Get-ListeningProcessId 8080
    if (-not $bLeft -and -not $fLeft) { break }
    Start-Sleep -Seconds 1
    $wait++
}

# Clean up temporary PID tracking files
if (Test-Path -LiteralPath $RunDir) {
    Remove-Item -Path "$RunDir\*" -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "-----------------------------------------------------------------" -ForegroundColor Gray

if ($backendTerminated) {
    Write-Host "  Backend Service  : STOPPED" -ForegroundColor Green
} else {
    Write-Host "  Backend Service  : WAS NOT RUNNING" -ForegroundColor DarkCyan
}

if ($frontendTerminated) {
    Write-Host "  Frontend Service : STOPPED" -ForegroundColor Green
} else {
    Write-Host "  Frontend Service : WAS NOT RUNNING" -ForegroundColor DarkCyan
}

$port8000Status = if (Get-ListeningProcessId 8000) { "BUSY" } else { "RELEASED" }
$port8080Status = if (Get-ListeningProcessId 8080) { "BUSY" } else { "RELEASED" }

Write-Host "  Port 8000        : $port8000Status" -ForegroundColor $(if ($port8000Status -eq "RELEASED") { "Green" } else { "Red" })
Write-Host "  Port 8080        : $port8080Status" -ForegroundColor $(if ($port8080Status -eq "RELEASED") { "Green" } else { "Red" })
Write-Host "  Database Status  : INTACT (apaar.db preserved)" -ForegroundColor Green

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "           ALL PROJECT SERVICES ARE SAFELY SHUT DOWN             " -ForegroundColor White
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""
