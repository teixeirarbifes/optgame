@echo off
echo ========================================
echo  Jogo de Producao - Web Portal
echo ========================================
echo.
echo Iniciando servidor web...
echo.
echo Acesse no navegador:
echo   - Admin: http://localhost:5000/admin/login
echo   - Aluno: http://localhost:5000/aluno/login
echo.
echo Senha Admin: admin123
echo.
echo Pressione Ctrl+C para parar o servidor
echo ========================================
echo.

cd /d "%~dp0"
poetry run python web_server.py

pause
