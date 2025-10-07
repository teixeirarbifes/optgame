#!/bin/bash
echo "========================================"
echo " Jogo de Producao - Web Portal"
echo "========================================"
echo ""
echo "Iniciando servidor web..."
echo ""
echo "Acesse no navegador:"
echo "  - Admin: http://localhost:5000/admin/login"
echo "  - Aluno: http://localhost:5000/aluno/login"
echo ""
echo "Senha Admin: admin123"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo "========================================"
echo ""

# Obter o diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Verificar se poetry está instalado
if ! command -v poetry &> /dev/null
then
    echo "❌ Poetry não encontrado!"
    echo ""
    echo "Por favor, instale o Poetry primeiro:"
    echo "  curl -sSL https://install.python-poetry.org | python3 -"
    echo ""
    echo "Ou use pip diretamente:"
    echo "  python3 web_server.py"
    echo ""
    read -p "Pressione Enter para sair..."
    exit 1
fi

# Executar servidor
poetry run python web_server.py

# Caso o servidor pare, pausar antes de fechar
echo ""
read -p "Pressione Enter para sair..."
