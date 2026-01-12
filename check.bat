@echo off
REM Quick validation shortcut

set ROOT=%~dp0

IF EXIST "%ROOT%.venv\Scripts\python.exe" (
	"%ROOT%.venv\Scripts\python.exe" "%ROOT%scripts\check_all.py" %*
	EXIT /B %ERRORLEVEL%
)

python "%ROOT%scripts\check_all.py" %*
