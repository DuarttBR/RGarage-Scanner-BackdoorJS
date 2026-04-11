@echo off
chcp 65001 >nul
cls

echo ================================================================================
echo   SCANNER DE BACKDOOR - FiveM
echo   Detecta e Remove XOR Backdoors / Injecoes em fxmanifest.lua
echo ================================================================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Baixe em: https://www.python.org/downloads/
    echo Marque "Add Python to PATH" na instalacao.
    echo.
    pause
    exit /b 1
)

set "SCANNER=%~dp0scan_backdoor.py"

if not exist "%SCANNER%" (
    echo [ERRO] scan_backdoor.py nao encontrado na pasta!
    pause
    exit /b 1
)

echo  [1] Varredura completa com confirmacao antes de limpar
echo  [2] Apenas relatorio - nao altera nada
echo  [3] Limpeza automatica - apaga tudo sem perguntar
echo  [4] Sair
echo.
set /p OPCAO="Escolha uma opcao: "

if "%OPCAO%"=="1" goto SCAN_NORMAL
if "%OPCAO%"=="2" goto SCAN_DRYRUN
if "%OPCAO%"=="3" goto SCAN_AUTO
if "%OPCAO%"=="4" exit /b 0

echo Opcao invalida.
pause
exit /b 1

:SCAN_NORMAL
cls
echo Iniciando varredura...
echo.
python -X utf8 "%SCANNER%"
goto FIM

:SCAN_DRYRUN
cls
echo Iniciando varredura em modo relatorio (nenhum arquivo sera alterado)...
echo.
python -X utf8 "%SCANNER%" --dry-run
goto FIM

:SCAN_AUTO
cls
echo [ATENCAO] Limpeza automatica - arquivos maliciosos serao deletados sem confirmacao!
echo.
python -X utf8 "%SCANNER%" --auto
goto FIM

:FIM
echo.
echo ================================================================================
echo   Processo concluido.
echo ================================================================================
pause
