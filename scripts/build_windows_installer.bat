@echo off
setlocal EnableExtensions

title Chef Pricing - Build Windows EXE

rem ==================================================
rem Configuracao principal
rem ==================================================

set "SCRIPT_DIR=%~dp0"

rem Se este .bat estiver dentro de scripts, a raiz e a pasta acima.
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI"

rem Se por algum motivo o .bat estiver na raiz, usa a propria pasta.
if not exist "%ROOT%\pyproject.toml" (
  for %%I in ("%SCRIPT_DIR%.") do set "ROOT=%%~fI"
)

set "LOG_DIR=%ROOT%\logs"
set "LOG=%LOG_DIR%\build_windows_exe.log"
set "OUT=%TEMP%\chef_pricing_build_step_output.txt"

set "VENV_DIR=%ROOT%\.venv-windows"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

set "LAST_STEP=Inicializacao"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1

> "%LOG%" echo ==================================================
>> "%LOG%" echo Chef Pricing - Build Windows EXE
>> "%LOG%" echo Started: %DATE% %TIME%
>> "%LOG%" echo Script dir: %SCRIPT_DIR%
>> "%LOG%" echo Root dir: %ROOT%
>> "%LOG%" echo Log file: %LOG%
>> "%LOG%" echo ==================================================

echo.
echo ==================================================
echo Chef Pricing - Build Windows EXE
echo ==================================================
echo Root:
echo "%ROOT%"
echo.
echo Log:
echo "%LOG%"
echo.

cd /d "%ROOT%" || (
  echo ERROR: Nao foi possivel acessar a raiz do projeto:
  echo "%ROOT%"
  pause
  exit /b 1
)

if not exist "%ROOT%\pyproject.toml" (
  echo ERROR: pyproject.toml nao encontrado.
  echo.
  echo O .bat precisa estar dentro da pasta scripts do projeto ou na raiz do projeto.
  echo Pasta atual detectada:
  echo "%ROOT%"
  echo.
  pause
  exit /b 1
)

rem ==================================================
rem Limpa ambiente virtual criado no lugar errado
rem ==================================================

if exist "%ROOT%\scripts\.venv-windows" (
  echo.
  echo Encontrado ambiente virtual antigo no lugar errado:
  echo "%ROOT%\scripts\.venv-windows"
  echo Removendo...
  rmdir /s /q "%ROOT%\scripts\.venv-windows" >nul 2>&1
)

rem ==================================================
rem Detecta Python
rem ==================================================

set "PYTHON_EXE="

rem Prioridade 1: caminho conhecido da sua maquina
if exist "C:\Users\giull\AppData\Local\Programs\Python\Python314\python.exe" (
  set "PYTHON_EXE=C:\Users\giull\AppData\Local\Programs\Python\Python314\python.exe"
)

rem Prioridade 2: Python Launcher tentando Python 3.14 x64
if not defined PYTHON_EXE (
  for /f "delims=" %%P in ('py -3.14-64 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_EXE=%%P"
)

rem Prioridade 3: Python Launcher tentando Python 3.12 x64
if not defined PYTHON_EXE (
  for /f "delims=" %%P in ('py -3.12-64 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_EXE=%%P"
)

rem Prioridade 4: comando python do PATH
if not defined PYTHON_EXE (
  for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_EXE=%%P"
)

if not defined PYTHON_EXE (
  echo ERROR: Nenhum Python valido foi encontrado.
  echo.
  echo Instale Python 3.12 ou superior, 64 bits.
  echo.
  pause
  exit /b 1
)

call :run "1/8 Validando Python escolhido" "%PYTHON_EXE%" -c "import sys, struct; print('Executable:', sys.executable); print('Version:', sys.version); print('Architecture:', struct.calcsize('P') * 8, 'bits'); raise SystemExit(0 if sys.version_info >= (3, 12) and struct.calcsize('P') * 8 == 64 else 1)"
if errorlevel 1 (
  echo.
  echo ERROR: O Python detectado nao e valido.
  echo Precisa ser Python 3.12 ou superior, 64 bits.
  goto :fail
)

rem ==================================================
rem Valida ou recria ambiente virtual
rem ==================================================

if exist "%VENV_PYTHON%" (
  call :run "2/8 Validando ambiente virtual existente" "%VENV_PYTHON%" -c "import sys, struct; print('Executable:', sys.executable); print('Version:', sys.version); print('Architecture:', struct.calcsize('P') * 8, 'bits'); raise SystemExit(0 if sys.version_info >= (3, 12) and struct.calcsize('P') * 8 == 64 else 1)"
  if errorlevel 1 (
    echo.
    echo Ambiente virtual invalido. Removendo para recriar...
    rmdir /s /q "%VENV_DIR%" >nul 2>&1
  )
) else (
  echo.
  echo 2/8 Ambiente virtual ainda nao existe. Sera criado.
  >> "%LOG%" echo.
  >> "%LOG%" echo 2/8 Ambiente virtual ainda nao existe. Sera criado.
)

if not exist "%VENV_PYTHON%" (
  call :run "3/8 Criando ambiente virtual .venv-windows" "%PYTHON_EXE%" -m venv "%VENV_DIR%"
  if errorlevel 1 goto :fail
) else (
  call :info "3/8 Ambiente virtual pronto: %VENV_DIR%"
)

call :run "4/8 Atualizando pip, setuptools e wheel" "%VENV_PYTHON%" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :fail

call :run "5/8 Instalando dependencias do projeto" "%VENV_PYTHON%" -m pip install -e ".[dev,build]"
if errorlevel 1 goto :fail

rem ==================================================
rem Verifica Inno Setup
rem ==================================================

call :detect_inno

if not defined INNO_SETUP_COMPILER (
  echo.
  echo Inno Setup 6 nao encontrado.
  echo Tentando instalar via winget...
  echo.

  where winget >nul 2>nul
  if errorlevel 1 (
    echo ERROR: winget nao encontrado.
    echo.
    echo Instale o Inno Setup 6 manualmente e rode este .bat de novo.
    echo Depois de instalado, o arquivo esperado normalmente fica em:
    echo "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    goto :fail
  )

  call :run "6/8 Instalando Inno Setup 6 via winget" winget install -e --id JRSoftware.InnoSetup
  if errorlevel 1 (
    echo.
    echo ERROR: Nao foi possivel instalar o Inno Setup automaticamente.
    echo Instale o Inno Setup 6 manualmente e rode este .bat de novo.
    goto :fail
  )

  call :detect_inno
)

if not defined INNO_SETUP_COMPILER (
  echo.
  echo ERROR: Inno Setup 6 ainda nao foi encontrado.
  echo.
  echo Instale o Inno Setup 6 manualmente ou defina a variavel:
  echo INNO_SETUP_COMPILER=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
  goto :fail
)

call :info "6/8 Inno Setup encontrado: %INNO_SETUP_COMPILER%"

rem ==================================================
rem Gera EXE / Installer
rem ==================================================

call :run "7/8 Gerando EXE e instalador" "%VENV_PYTHON%" "%ROOT%\scripts\build_windows_exe.py"
if errorlevel 1 goto :fail

echo.
echo ==================================================
echo 8/8 Build finalizado com sucesso
echo ==================================================
echo.

if exist "%ROOT%\dist\installer" (
  echo Instaladores gerados:
  dir /b "%ROOT%\dist\installer\*.exe" 2>nul
  echo.
)

echo Log completo:
echo "%LOG%"
echo.
pause
exit /b 0


rem ==================================================
rem Funcoes
rem ==================================================

:detect_inno
set "INNO_SETUP_COMPILER="

where ISCC.exe > "%TEMP%\chef_pricing_iscc_path.txt" 2>nul
if not errorlevel 1 (
  for /f "delims=" %%I in (%TEMP%\chef_pricing_iscc_path.txt) do (
    if not defined INNO_SETUP_COMPILER set "INNO_SETUP_COMPILER=%%I"
  )
)

if not defined INNO_SETUP_COMPILER (
  if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "INNO_SETUP_COMPILER=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
  )
)

if not defined INNO_SETUP_COMPILER (
  if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "INNO_SETUP_COMPILER=%ProgramFiles%\Inno Setup 6\ISCC.exe"
  )
)

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