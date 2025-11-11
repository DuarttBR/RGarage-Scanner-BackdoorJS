@echo off
chcp 65001 >nul
cls

echo SCANNER DE BACKDOOR - Deteccao e Remocao de Codigo Malicioso
echo Desenvolvido por RYU GARAGE
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado! Instale Python 3.x
    pause
    exit /b 1
)

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"
cd /d "%~dp0.."

if not exist "%SCRIPT_DIR%scan_backdoor.py" (
    echo [ERRO] Arquivo scan_backdoor.py nao encontrado!
    pause
    exit /b 1
)

echo Diretorio: %CD%
echo Iniciando varredura...
echo.

if "%1"=="--dry-run" (
    python "%SCRIPT_DIR%scan_backdoor.py" --dry-run
) else if "%1"=="-n" (
    python "%SCRIPT_DIR%scan_backdoor.py" -n
) else (
    python "%SCRIPT_DIR%scan_backdoor.py"
)

echo.
echo Processo concluido!
pause
