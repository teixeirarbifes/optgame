@echo off
REM ========================================
REM  Jogo de Producao - Instalacao Web
REM ========================================

echo.
echo ========================================
echo  Instalando dependencias do Web Portal
echo ========================================
echo.

cd /d "%~dp0"

REM Verificar se Poetry esta instalado
poetry --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Poetry nao encontrado!
    echo.
    echo Instale o Poetry primeiro:
    echo   https://python-poetry.org/docs/#installation
    echo.
    echo Ou com pip:
    echo   pip install poetry
    echo.
    pause
    exit /b 1
)

echo [1/3] Instalando dependencias com Poetry...
poetry install

echo.
echo [2/3] Verificando instalacao...
poetry run python -c "import flask; print('Flask OK')"
poetry run python -c "import flask_session; print('Flask-Session OK')"

echo.
echo [3/3] Testando configuracao...
poetry run python test_config.py

echo.
echo ========================================
echo  Instalacao concluida!
echo ========================================
echo.
echo Para iniciar o servidor, execute:
echo   start_web.bat
echo.
echo Ou manualmente:
echo   poetry run python web_server.py
echo.

pause
