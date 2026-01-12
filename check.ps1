# Quick validation shortcut
# Usage: .\check  or  .\check --quick

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$checkAll = Join-Path $PSScriptRoot "scripts\check_all.py"
if (Test-Path $venvPython) {
	& $venvPython $checkAll @args
	exit $LASTEXITCODE
}

python $checkAll @args
