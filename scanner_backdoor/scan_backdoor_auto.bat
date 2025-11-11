@echo off
chcp 65001 >nul
cls

echo SCANNER DE BACKDOOR - Modo Automatico
echo Desenvolvido por RYU GARAGE
echo.
echo [ATENCAO] Deletara arquivos automaticamente sem perguntar!
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

if not exist "%SCRIPT_DIR%scan_backdoor_auto_delete.py" (
    echo [ERRO] Arquivo scan_backdoor_auto_delete.py nao encontrado!
    pause
    exit /b 1
)

echo Diretorio: %CD%
echo Iniciando varredura automatica...
echo.

python "%SCRIPT_DIR%scan_backdoor_auto_delete.py"

echo.
echo Processo concluido!
pause
