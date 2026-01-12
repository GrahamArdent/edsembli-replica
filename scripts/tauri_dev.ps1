param(
  [int]$Port = 1420
)

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$vgreportDir = Join-Path $repoRoot 'vgreport'

if (-not (Test-Path $vgreportDir)) {
  throw "Expected vgreport directory at: $vgreportDir"
}

Write-Host "Stopping stale app processes (if any)..."
Get-Process vgreport -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process "vgreport-engine-x86_64-pc-windows-msvc" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Freeing port $Port (if needed)..."
$maxAttempts = 10
for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
  $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  if ($null -eq $conns -or $conns.Count -eq 0) {
    break
  }

  $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
  foreach ($pid in $pids) {
    if ($null -eq $pid) { continue }
    try {
      $proc = Get-Process -Id $pid -ErrorAction Stop
      Write-Host "Attempt $attempt/${maxAttempts}: stopping PID $pid ($($proc.ProcessName)) listening on port $Port..."
    } catch {
      Write-Host "Attempt $attempt/${maxAttempts}: stopping PID $pid listening on port $Port..."
    }

    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
  }

  Start-Sleep -Milliseconds 300
}

$remaining = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -ne $remaining) {
  throw "Port $Port is still in use by PID $($remaining.OwningProcess). Close the process and retry."
}

Set-Location $vgreportDir

Write-Host "Starting Tauri dev (will run Vite on port $Port)..."

# Tauri dev spawns the Vite server via beforeDevCommand in src-tauri/tauri.conf.json.
# If you already have Vite running separately, stop it first or change beforeDevCommand.

npm run tauri -- dev
