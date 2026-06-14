@echo off
setlocal
cd /d "%~dp0\.."

where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python Launcher was not found. Install Python 3.12 x64.
  exit /b 1
)

if not exist ".venv-windows\Scripts\python.exe" (
  py -3.12-64 -m venv .venv-windows
  if errorlevel 1 exit /b 1
)

".venv-windows\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

".venv-windows\Scripts\python.exe" -m pip install -e ".[dev,build]"
if errorlevel 1 exit /b 1

".venv-windows\Scripts\python.exe" scripts\build_windows_exe.py
exit /b %errorlevel%
