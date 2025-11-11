@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo 🔍 SCANNER DE BACKDOOR - Detecção e Remoção de Código Malicioso
echo ================================================================================
echo.
echo                    ╔═══════════════════════════════════╗
echo                    ║   🏍️  Desenvolvido por          ║
echo                    ║      RYU GARAGE                  ║
echo                    ║                                  ║
echo                    ║   Proteção e Segurança           ║
echo                    ║   para Servidores FiveM          ║
echo                    ╚═══════════════════════════════════╝
echo.
echo ================================================================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Por favor, instale Python 3.x
    echo.
    pause
    exit /b 1
)

REM Obtém o diretório do script
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Volta um nível para escanear o diretório raiz do projeto
cd /d "%~dp0.."

REM Verifica se o arquivo Python existe
if not exist "%SCRIPT_DIR%scan_backdoor.py" (
    echo ❌ Arquivo scan_backdoor.py não encontrado!
    echo.
    pause
    exit /b 1
)

REM Executa o scanner
echo 📁 Diretório a ser escaneado: %CD%
echo.
echo 🔍 Iniciando varredura...
echo.

REM Verifica se foi passado parâmetro de modo dry-run
if "%1"=="--dry-run" (
    python "%SCRIPT_DIR%scan_backdoor.py" --dry-run
) else if "%1"=="-n" (
    python "%SCRIPT_DIR%scan_backdoor.py" -n
) else (
    python "%SCRIPT_DIR%scan_backdoor.py"
)

echo.
echo ================================================================================
echo ✅ Processo concluído!
echo ================================================================================
echo.
echo                    ╔═══════════════════════════════════╗
echo                    ║   🏍️  RYU GARAGE                 ║
echo                    ║   Desenvolvido com ❤️            ║
echo                    ╚═══════════════════════════════════╝
echo.
pause

