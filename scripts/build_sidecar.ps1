# Sidecar Build Script
# Usage: .\scripts\build_sidecar.ps1

$ErrorActionPreference = "Stop"

# 1. Define Paths
$WorkspaceRoot = Resolve-Path "$PSScriptRoot\.."
$TauriSrcDir = "$WorkspaceRoot\vgreport\src-tauri"
$TauriBinDir = "$TauriSrcDir\binaries"
$SidecarSource = "$WorkspaceRoot\sidecar\main.py"
$OutputName = "vgreport-engine"

# 2. Add Target Triple (Windows x64)
# Tauri requires sidecars to include the target triple in the filename
$TargetTriple = "x86_64-pc-windows-msvc"
$FinalBinaryName = "$OutputName-$TargetTriple.exe"

Write-Host "🏗️  Building Python Sidecar..." -ForegroundColor Cyan

# 3. Clean previous builds
if (Test-Path "$WorkspaceRoot\build") { Remove-Item "$WorkspaceRoot\build" -Recurse -Force }
if (Test-Path "$WorkspaceRoot\dist") { Remove-Item "$WorkspaceRoot\dist" -Recurse -Force }
if (Test-Path "$TauriBinDir") {
    # Create dir if not exists
} else {
    New-Item -ItemType Directory -Force -Path $TauriBinDir | Out-Null
}

# 4. Run PyInstaller
# --onefile: Bundle everything into one .exe
# --clean: Clean cache
# --console: MUST have console for stdin/stdout IPC (Tauri hides it anyway)
# --name: Internal name
# --add-data: Bundle templates and lib
& "$WorkspaceRoot\.venv\Scripts\pyinstaller.exe" --console --onefile --clean --name $OutputName --distpath "$WorkspaceRoot\dist" --workpath "$WorkspaceRoot\build" --specpath "$WorkspaceRoot\sidecar" --paths "$WorkspaceRoot" --add-data "$WorkspaceRoot\templates;templates" --add-data "$WorkspaceRoot\lib;lib" --add-data "$WorkspaceRoot\contracts;contracts" "$SidecarSource"


if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller build failed!"
}

# 5. Move and Rename for Tauri
$SourceExe = "$WorkspaceRoot\dist\$OutputName.exe"

# Tauri dev resolution: the CLI may look in `src-tauri/` directly.
# Packaging/bundling: we also keep a copy in `src-tauri/binaries/`.
$DestExeDev = "$TauriSrcDir\$FinalBinaryName"
$DestExeBin = "$TauriBinDir\$FinalBinaryName"

if (Test-Path $SourceExe) {
    foreach ($dest in @($DestExeDev, $DestExeBin)) {
        if (Test-Path $dest) {
            Remove-Item $dest -Force -ErrorAction SilentlyContinue
        }
    }

    # Put the exe where Tauri dev expects it, and also keep the binaries/ copy.
    Copy-Item $SourceExe $DestExeDev -Force
    Copy-Item $SourceExe $DestExeBin -Force
    Remove-Item $SourceExe -Force -ErrorAction SilentlyContinue

    Write-Host "✅ Success! Sidecar built to:" -ForegroundColor Green
    Write-Host "   $DestExeDev" -ForegroundColor Gray
    Write-Host "   $DestExeBin" -ForegroundColor Gray
} else {
    Write-Error "Build finished but output file not found at $SourceExe"
}
