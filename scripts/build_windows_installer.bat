@echo off
setlocal
cd /d "%~dp0\.."

@echo off
setlocal EnableExtensions

title Build Windows EXE

set "ROOT=%~dp0"
cd /d "%ROOT%" || (
  echo ERROR: Could not access project folder: "%ROOT%"
  pause
  exit /b 1
)

set "PYTHON_EXE=C:\Users\giull\AppData\Local\Programs\Python\Python314\python.exe"

set "LOG_DIR=%ROOT%logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1

set "LOG=%LOG_DIR%\build_windows_exe.log"
set "OUT=%TEMP%\build_windows_exe_step_output.txt"
set "LAST_STEP=Inicializacao"

> "%LOG%" echo ==================================================
>> "%LOG%" echo Build started: %DATE% %TIME%
>> "%LOG%" echo Root folder: %CD%
>> "%LOG%" echo Python exe: %PYTHON_EXE%
>> "%LOG%" echo ==================================================

echo.
echo ==================================================
echo Build Windows EXE
echo ==================================================
echo Log completo:
echo "%LOG%"
echo.

if not exist "%PYTHON_EXE%" (
  echo ERROR: Python nao encontrado no caminho:
  echo "%PYTHON_EXE%"
  echo.
  echo Ajuste a variavel PYTHON_EXE dentro deste arquivo .bat.
  pause
  exit /b 1
)

call :run "1/6 Validando Python escolhido" "%PYTHON_EXE%" -c "import sys, struct; print(sys.executable); print(sys.version); print('Architecture:', struct.calcsize('P') * 8, 'bits')"
if errorlevel 1 goto :fail

if not exist ".venv-windows\Scripts\python.exe" (
  call :run "2/6 Criando ambiente virtual .venv-windows" "%PYTHON_EXE%" -m venv .venv-windows
  if errorlevel 1 goto :fail
) else (
  call :info "2/6 Ambiente virtual ja existe: .venv-windows"
)

set "VENV_PYTHON=.venv-windows\Scripts\python.exe"

call :run "3/6 Validando Python da virtualenv" "%VENV_PYTHON%" -c "import sys, struct; print(sys.executable); print(sys.version); print('Architecture:', struct.calcsize('P') * 8, 'bits')"
if errorlevel 1 goto :fail

call :run "4/6 Atualizando pip" "%VENV_PYTHON%" -m pip install --upgrade pip
if errorlevel 1 goto :fail

call :run "5/6 Instalando dependencias do projeto" "%VENV_PYTHON%" -m pip install -e ".[dev,build]"
if errorlevel 1 goto :fail

call :run "6/6 Gerando EXE" "%VENV_PYTHON%" scripts\build_windows_exe.py
if errorlevel 1 goto :fail

echo.
echo ==================================================
echo SUCESSO: build finalizado.
echo ==================================================
echo Log completo:
echo "%LOG%"
echo.
pause
exit /b 0


:run
set "LAST_STEP=%~1"

echo.
echo ==================================================
echo %LAST_STEP%
echo ==================================================

>> "%LOG%" echo.
>> "%LOG%" echo ==================================================
>> "%LOG%" echo %LAST_STEP%
>> "%LOG%" echo Command: %2 %3 %4 %5 %6 %7 %8 %9
>> "%LOG%" echo ==================================================

%2 %3 %4 %5 %6 %7 %8 %9 > "%OUT%" 2>&1
set "ERR=%ERRORLEVEL%"

type "%OUT%"
type "%OUT%" >> "%LOG%"

if not "%ERR%"=="0" (
  echo.
  echo ERROR na etapa:
  echo %LAST_STEP%
  echo.
  echo Codigo de erro: %ERR%
  >> "%LOG%" echo.
  >> "%LOG%" echo ERROR na etapa: %LAST_STEP%
  >> "%LOG%" echo Codigo de erro: %ERR%
  exit /b %ERR%
)

exit /b 0


:info
echo.
echo %~1
>> "%LOG%" echo.
>> "%LOG%" echo %~1
exit /b 0


:fail
echo.
echo ==================================================
echo BUILD FALHOU
echo ==================================================
echo Etapa:
echo %LAST_STEP%
echo.
echo Veja o log completo em:
echo "%LOG%"
echo.
echo O terminal ficara aberto para voce copiar o erro.
echo ==================================================
echo.
pause
exit /b 1