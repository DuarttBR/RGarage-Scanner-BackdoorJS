@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo 🔍 SCANNER DE BACKDOOR - Modo Automático (Deleta sem perguntar)
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
echo ⚠️  ATENÇÃO: Este script deletará automaticamente todos os arquivos maliciosos!
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
if not exist "%SCRIPT_DIR%scan_backdoor_auto_delete.py" (
    echo ❌ Arquivo scan_backdoor_auto_delete.py não encontrado!
    echo.
    pause
    exit /b 1
)

REM Executa o scanner em modo automático
echo 📁 Diretório a ser escaneado: %CD%
echo.
echo 🔍 Iniciando varredura automática...
echo.

REM Executa o scanner em modo automático
python "%SCRIPT_DIR%scan_backdoor_auto_delete.py"

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

