@echo off
setlocal EnableExtensions

title Chef Pricing - Build Windows EXE

rem ==================================================
rem Chef Pricing - Build Windows EXE
rem Este arquivo deve ficar em: scripts\build_windows_installer.bat
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
set "PIP_LOG=%LOG_DIR%\pip_install_verbose.log"
set "OUT=%TEMP%\chef_pricing_build_step_output.txt"

set "VENV_DIR=%ROOT%\.venv-windows"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

set "LAST_STEP=Inicializacao"
set "PYTHON_EXE="

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1

> "%LOG%" echo ==================================================
>> "%LOG%" echo Chef Pricing - Build Windows EXE
>> "%LOG%" echo Started: %DATE% %TIME%
>> "%LOG%" echo Script dir: %SCRIPT_DIR%
>> "%LOG%" echo Root dir: %ROOT%
>> "%LOG%" echo Log file: %LOG%
>> "%LOG%" echo Pip log file: %PIP_LOG%
>> "%LOG%" echo ==================================================

echo.
echo ==================================================
echo Chef Pricing - Build Windows EXE
echo ==================================================
echo Root:
echo "%ROOT%"
echo.
echo Log principal:
echo "%LOG%"
echo.
echo Log detalhado do pip:
echo "%PIP_LOG%"
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
  echo Pasta detectada:
  echo "%ROOT%"
  echo.
  pause
  exit /b 1
)

rem ==================================================
rem Remove ambiente virtual criado no lugar errado
rem ==================================================

if exist "%ROOT%\scripts\.venv-windows" (
  echo.
  echo Encontrado ambiente virtual antigo no lugar errado:
  echo "%ROOT%\scripts\.venv-windows"
  echo Removendo...
  rmdir /s /q "%ROOT%\scripts\.venv-windows" >nul 2>&1

  if exist "%ROOT%\scripts\.venv-windows" (
    echo ERROR: Nao foi possivel remover:
    echo "%ROOT%\scripts\.venv-windows"
    echo.
    echo Feche terminais ou programas usando essa pasta e rode novamente.
    goto :fail
  )
)

rem ==================================================
rem Forca Python 3.12 x64
rem ==================================================

for /f "delims=" %%P in ('py -3.12-64 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_EXE=%%P"

if not defined PYTHON_EXE (
  echo ERROR: Python 3.12 x64 nao foi encontrado pelo Python Launcher.
  echo.
  echo Rode este comando para confirmar:
  echo py -3.12-64 --version
  echo.
  echo Se falhar, reinstale o Python 3.12 x64.
  echo.
  pause
  exit /b 1
)

call :run "1/8 Validando Python 3.12 x64" "%PYTHON_EXE%" -c "import sys, struct; print('Executable:', sys.executable); print('Version:', sys.version); print('Architecture:', struct.calcsize('P') * 8, 'bits'); raise SystemExit(0 if sys.version_info[:2] == (3, 12) and struct.calcsize('P') * 8 == 64 else 1)"
if errorlevel 1 (
  echo.
  echo ERROR: O Python detectado nao e Python 3.12 x64.
  goto :fail
)

>> "%LOG%" echo Python 3.12 executable: %PYTHON_EXE%

rem ==================================================
rem Valida ou recria ambiente virtual
rem ==================================================

if exist "%VENV_PYTHON%" (
  call :run "2/8 Validando ambiente virtual existente" "%VENV_PYTHON%" -c "import sys, struct; print('Executable:', sys.executable); print('Version:', sys.version); print('Architecture:', struct.calcsize('P') * 8, 'bits'); raise SystemExit(0 if sys.version_info[:2] == (3, 12) and struct.calcsize('P') * 8 == 64 else 1)"

  if errorlevel 1 (
    echo.
    echo Ambiente virtual existente nao esta usando Python 3.12 x64.
    echo Removendo para recriar corretamente...
    echo.
    rmdir /s /q "%VENV_DIR%" >nul 2>&1

    if exist "%VENV_DIR%" (
      echo ERROR: Nao foi possivel remover:
      echo "%VENV_DIR%"
      echo.
      echo Feche terminais ou programas usando essa pasta e rode novamente.
      goto :fail
    )
  )
) else (
  echo.
  echo 2/8 Ambiente virtual ainda nao existe. Sera criado.
  >> "%LOG%" echo.
  >> "%LOG%" echo 2/8 Ambiente virtual ainda nao existe. Sera criado.
)

if not exist "%VENV_PYTHON%" (
  call :run "3/8 Criando ambiente virtual .venv-windows com Python 3.12" "%PYTHON_EXE%" -m venv "%VENV_DIR%"
  if errorlevel 1 goto :fail
) else (
  call :info "3/8 Ambiente virtual pronto: %VENV_DIR%"
)

call :run "4/8 Atualizando pip, setuptools e wheel" "%VENV_PYTHON%" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :fail

rem ==================================================
rem Instala dependencias
rem ==================================================

if exist "%PIP_LOG%" del "%PIP_LOG%" >nul 2>&1

call :run "5/8 Instalando dependencias do projeto" "%VENV_PYTHON%" -m pip install -e ".[dev,build]" --verbose --log "%PIP_LOG%"
if errorlevel 1 (
  echo.
  echo ERROR: Falha na instalacao das dependencias.
  echo.
  echo Veja o log detalhado do pip em:
  echo "%PIP_LOG%"
  echo.
  goto :fail
)

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
    echo Caminho esperado normalmente:
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

echo Log principal:
echo "%LOG%"
echo.
echo Log detalhado do pip:
echo "%PIP_LOG%"
echo.
pause
exit /b 0


rem ==================================================
rem Funcoes
rem ==================================================

:detect_inno
set "INNO_SETUP_COMPILER="

for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do (
  if not defined INNO_SETUP_COMPILER set "INNO_SETUP_COMPILER=%%I"
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
shift /1

echo.
echo ==================================================
echo %LAST_STEP%
echo ==================================================

>> "%LOG%" echo.
>> "%LOG%" echo ==================================================
>> "%LOG%" echo %LAST_STEP%
>> "%LOG%" echo Command: %1 %2 %3 %4 %5 %6 %7 %8 %9
>> "%LOG%" echo ==================================================

%1 %2 %3 %4 %5 %6 %7 %8 %9 > "%OUT%" 2>&1
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
echo Log principal:
echo "%LOG%"
echo.
echo Log detalhado do pip:
echo "%PIP_LOG%"
echo.
echo O terminal ficara aberto para voce copiar o erro.
echo ==================================================
echo.
pause
exit /b 1
