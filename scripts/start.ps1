# ==============================================================================
# SIH26263 APAAR Platform - Service Starter Script (PowerShell)
# Starts FastAPI backend (port 8000) and Vite frontend (port 8080)
# ==============================================================================
[CmdletBinding()]
param(
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path "$PSScriptRoot\..").Path
Set-Location -Path $ProjectRoot

# Banner
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   APAAR ID-Based Student Data Platform - AICTE Institutions    " -ForegroundColor White
Write-Host "                    System Startup Manager                      " -ForegroundColor DarkCyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

# Helper to find PID listening on a specific TCP port
function Get-ListeningProcessId([int]$Port) {
    try {
        $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($conns) {
            return ($conns | Select-Object -ExpandProperty OwningProcess -Unique | Select-Object -First 1)
        }
    } catch {
        # Fallback to netstat if Get-NetTCPConnection is unavailable
        $lines = netstat -ano -p tcp | Select-String ":$Port\s+.*LISTENING\s+(\d+)"
        if ($lines -and $lines[0].Line -match ":$Port\s+.*LISTENING\s+(\d+)") {
            return [int]$matches[1]
        }
    }
    return $null
}

# Directories and paths
$VenvPython = Join-Path $ProjectRoot "backend\.venv\Scripts\python.exe"
$NodeModules = Join-Path $ProjectRoot "node_modules"
$DbFile = Join-Path $ProjectRoot "apaar.db"
$RunDir = Join-Path $ProjectRoot ".run"
$BackendPidFile = Join-Path $RunDir "backend.pid"
$FrontendPidFile = Join-Path $RunDir "frontend.pid"
$BackendPortPidFile = Join-Path $RunDir "backend_port.pid"
$FrontendPortPidFile = Join-Path $RunDir "frontend_port.pid"

# --- 1. Pre-flight Checks ---
Write-Host "[1/4] Running pre-flight environment checks..." -ForegroundColor Yellow

# Verify Python Virtual Environment
if (-not (Test-Path -LiteralPath $VenvPython)) {
    Write-Host "[ERROR] Python virtual environment was not found at:" -ForegroundColor Red
    Write-Host "        $VenvPython" -ForegroundColor Red
    Write-Host ""
    Write-Host "To set up the backend virtual environment, run:" -ForegroundColor Yellow
    Write-Host "  python -m venv backend\.venv" -ForegroundColor White
    Write-Host "  backend\.venv\Scripts\activate" -ForegroundColor White
    Write-Host "  pip install fastapi uvicorn[standard] pydantic sqlalchemy alembic pyjwt cryptography bcrypt python-multipart" -ForegroundColor White
    exit 1
}
Write-Host "  [+] Python virtual environment detected: $VenvPython" -ForegroundColor Green

# Verify Frontend Dependencies
if (-not (Test-Path -LiteralPath $NodeModules)) {
    Write-Host "[ERROR] Frontend node_modules directory not found." -ForegroundColor Red
    Write-Host "Please install frontend dependencies first using 'bun install' or 'npm install'." -ForegroundColor Yellow
    exit 1
}
Write-Host "  [+] Frontend node_modules directory detected." -ForegroundColor Green

# Detect Frontend Package Manager
$PackageManager = "npm"
$BunPath = (Get-Command bun -ErrorAction SilentlyContinue)
if ($BunPath) {
    $PackageManager = "bun"
    Write-Host "  [+] Package manager detected: bun ($($BunPath.Source))" -ForegroundColor Green
} else {
    Write-Host "  [+] Package manager detected: npm" -ForegroundColor Green
}

# Check Database
if (Test-Path -LiteralPath $DbFile) {
    Write-Host "  [+] Database verified: apaar.db (preserving existing data)" -ForegroundColor Green
} else {
    Write-Host "  [!] Database (apaar.db) not found. Initializing schema and seed data..." -ForegroundColor DarkYellow
    & $VenvPython -m alembic upgrade head
    & $VenvPython -m backend.app.seed.seed_data
    Write-Host "  [+] Database initialized with synthetic demo data." -ForegroundColor Green
}

# Ensure .run directory exists
if (-not (Test-Path -LiteralPath $RunDir)) {
    New-Item -ItemType Directory -Path $RunDir -Force | Out-Null
}

# --- 2. Check for Already Running Instances ---
Write-Host ""
Write-Host "[2/4] Checking ports and running processes..." -ForegroundColor Yellow

$BackendRunning = $false
$FrontendRunning = $false

$backendPortPid = Get-ListeningProcessId 8000
if ($backendPortPid) {
    Write-Host "  [!] Port 8000 is already active (PID: $backendPortPid)." -ForegroundColor DarkYellow
    Write-Host "      Reusing existing backend instance." -ForegroundColor DarkCyan
    $BackendRunning = $true
    $backendPortPid | Out-File -FilePath $BackendPortPidFile -Encoding ascii -Force
}

$frontendPortPid = Get-ListeningProcessId 8080
if ($frontendPortPid) {
    Write-Host "  [!] Port 8080 is already active (PID: $frontendPortPid)." -ForegroundColor DarkYellow
    Write-Host "      Reusing existing frontend instance." -ForegroundColor DarkCyan
    $FrontendRunning = $true
    $frontendPortPid | Out-File -FilePath $FrontendPortPidFile -Encoding ascii -Force
}

# --- 3. Launch Services ---
Write-Host ""
Write-Host "[3/4] Launching project services..." -ForegroundColor Yellow

if (-not $BackendRunning) {
    Write-Host "  Starting FastAPI Backend on port 8000 in a separate window..." -ForegroundColor White
    $backendTitle = "APAAR Backend - FastAPI (Port 8000)"
    $backendCmd = "title $backendTitle && `"$VenvPython`" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"
    $bProc = Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $backendCmd -WorkingDirectory $ProjectRoot -PassThru
    $bProc.Id | Out-File -FilePath $BackendPidFile -Encoding ascii -Force
    Write-Host "  [+] Backend window launched (Window PID: $($bProc.Id))." -ForegroundColor Green
}

if (-not $FrontendRunning) {
    Write-Host "  Starting Frontend on port 8080 in a separate window..." -ForegroundColor White
    $frontendTitle = "APAAR Frontend - Vite (Port 8080)"
    $frontendCmd = if ($PackageManager -eq "bun") {
        "title $frontendTitle && bun run dev"
    } else {
        "title $frontendTitle && npm run dev"
    }
    $fProc = Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $frontendCmd -WorkingDirectory $ProjectRoot -PassThru
    $fProc.Id | Out-File -FilePath $FrontendPidFile -Encoding ascii -Force
    Write-Host "  [+] Frontend window launched (Window PID: $($fProc.Id))." -ForegroundColor Green
}

# --- 4. Health Check & Polling Loop ---
Write-Host ""
Write-Host "[4/4] Verifying services are healthy and responding..." -ForegroundColor Yellow
Write-Host -NoNewline "  Waiting for ports 8000 and 8080 to listen"

$timeoutSeconds = 25
$elapsed = 0
$backendReady = $BackendRunning
$frontendReady = $FrontendRunning

while ($elapsed -lt $timeoutSeconds) {
    if ($backendReady -and $frontendReady) {
        break
    }

    Start-Sleep -Seconds 1
    $elapsed++
    Write-Host -NoNewline "."

    if (-not $backendReady) {
        $bPid = Get-ListeningProcessId 8000
        if ($bPid) {
            $backendReady = $true
            $bPid | Out-File -FilePath $BackendPortPidFile -Encoding ascii -Force
        }
    }

    if (-not $frontendReady) {
        $fPid = Get-ListeningProcessId 8080
        if ($fPid) {
            $frontendReady = $true
            $fPid | Out-File -FilePath $FrontendPortPidFile -Encoding ascii -Force
        }
    }
}
Write-Host ""

if (-not $backendReady) {
    Write-Host ""
    Write-Host "[ERROR] Backend service failed to listen on port 8000 within $timeoutSeconds seconds." -ForegroundColor Red
    Write-Host "        Please check the 'APAAR Backend' terminal window for Python error traces." -ForegroundColor Yellow
}

if (-not $frontendReady) {
    Write-Host ""
    Write-Host "[ERROR] Frontend service failed to listen on port 8080 within $timeoutSeconds seconds." -ForegroundColor Red
    Write-Host "        Please check the 'APAAR Frontend' terminal window for build/Vite errors." -ForegroundColor Yellow
}

if (-not $backendReady -or -not $frontendReady) {
    exit 1
}

Write-Host "  [+] Both backend and frontend services are operational!" -ForegroundColor Green

# Open browser if requested
if (-not $NoBrowser) {
    Write-Host "  [+] Opening browser at http://localhost:8080/login ..." -ForegroundColor Cyan
    Start-Process "http://localhost:8080/login"
}

# Final Display Dashboard
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "               ALL SERVICES STARTED SUCCESSFULLY                 " -ForegroundColor White
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "  Frontend Web UI   : " -NoNewline; Write-Host "http://localhost:8080" -ForegroundColor Cyan
Write-Host "  Direct Login Page : " -NoNewline; Write-Host "http://localhost:8080/login" -ForegroundColor Cyan
Write-Host "  FastAPI Backend   : " -NoNewline; Write-Host "http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  Swagger API Docs  : " -NoNewline; Write-Host "http://127.0.0.1:8000/api/v1/docs" -ForegroundColor Cyan
Write-Host "  ReDoc API Docs    : " -NoNewline; Write-Host "http://127.0.0.1:8000/api/v1/redoc" -ForegroundColor Cyan
Write-Host "  Health Endpoint   : " -NoNewline; Write-Host "http://127.0.0.1:8000/health" -ForegroundColor Cyan
Write-Host "-----------------------------------------------------------------" -ForegroundColor Gray
Write-Host "  Demo Credentials (Password: Password@123):" -ForegroundColor White
Write-Host "   - Institution Admin : priya.nair       (INS-001)" -ForegroundColor DarkCyan
Write-Host "   - Data Entry Officer: k.rao            (INS-001)" -ForegroundColor DarkCyan
Write-Host "   - Central Reviewer  : r.menon          (AICTE Central)" -ForegroundColor DarkCyan
Write-Host "   - Authorized Verifier: s.kulkarni      (INS-001)" -ForegroundColor DarkCyan
Write-Host "   - Tenant Isolation  : admin.ins002     (INS-002)" -ForegroundColor DarkCyan
Write-Host "-----------------------------------------------------------------" -ForegroundColor Gray
Write-Host "  Management Commands:" -ForegroundColor White
Write-Host "   - To stop safely    : run stop.bat" -ForegroundColor Yellow
Write-Host "   - To restart        : run restart.bat" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Green
Write-Host ""
