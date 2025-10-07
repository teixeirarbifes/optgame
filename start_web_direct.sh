#!/bin/bash
echo "========================================"
echo " Jogo de Producao - Web Portal"
echo " (Modo direto com pip)"
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

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 não encontrado!"
    echo ""
    echo "Por favor, instale Python 3 primeiro:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Fedora/RHEL:   sudo dnf install python3 python3-pip"
    echo "  Arch:          sudo pacman -S python python-pip"
    echo ""
    read -p "Pressione Enter para sair..."
    exit 1
fi

# Verificar se as dependências estão instaladas
if ! python3 -c "import flask" &> /dev/null; then
    echo "⚠️  Dependências não encontradas. Instalando..."
    echo ""
    pip3 install -r requirements_web.txt
    echo ""
fi

# Executar servidor
python3 web_server.py

# Caso o servidor pare, pausar antes de fechar
echo ""
read -p "Pressione Enter para sair..."
