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
echo "Senha Admin: admin1064*"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo "========================================"
echo ""

# Obter o diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 não encontrado!"
    echo ""
    echo "Por favor, instale Python 3 primeiro:"
    echo "  Ubuntu/Debian: apt install python3 python3-pip"
    echo "  Fedora/RHEL:   dnf install python3 python3-pip"
    echo ""
    read -p "Pressione Enter para sair..."
    exit 1
fi

# Verificar se poetry está instalado
if command -v poetry &> /dev/null
then
    echo "✅ Usando Poetry..."
    echo ""
    # Instalar dependências se necessário
    poetry install --no-root 2>/dev/null || true
    # Executar servidor
    poetry run python web_server.py
else
    echo "ℹ️  Poetry não encontrado. Usando pip diretamente..."
    echo ""
    
    # Verificar se as dependências estão instaladas
    if ! python3 -c "import flask" &> /dev/null; then
        echo "⚠️  Instalando dependências..."
        echo ""
        pip3 install flask flask-session pulp || pip install flask flask-session pulp
        echo ""
    fi
    
    # Executar servidor
    python3 web_server.py
fi

# Caso o servidor pare, pausar antes de fechar
echo ""
read -p "Pressione Enter para sair..."
