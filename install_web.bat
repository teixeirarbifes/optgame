@echo off
REM Script de instalação rápida para Windows

echo ============================================================
echo  INSTALACAO DO JOGO DE PRODUCAO - VERSAO WEB
echo ============================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado! Instale Python 3.9+ primeiro.
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Instalar dependências
echo Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install -r requirements_web.txt

if errorlevel 1 (
    echo.
    echo [ERRO] Falha na instalacao das dependencias
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  INSTALACAO CONCLUIDA COM SUCESSO!
echo ============================================================
echo.
echo Proximos passos:
echo.
echo 1. Configure empresas de demonstracao:
echo    python setup_demo.py
echo.
echo 2. Inicie o servidor web:
echo    python web_server.py
echo.
echo 3. Acesse no navegador:
echo    http://localhost:5000
echo.
echo ============================================================
pause
