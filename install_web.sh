#!/bin/bash
# Script de instalação rápida para Linux/Mac

echo "============================================================"
echo " INSTALAÇÃO DO JOGO DE PRODUÇÃO - VERSÃO WEB"
echo "============================================================"
echo

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python não encontrado! Instale Python 3.9+ primeiro."
    exit 1
fi

echo "[OK] Python encontrado"
echo

# Instalar dependências
echo "Instalando dependências..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements_web.txt

if [ $? -ne 0 ]; then
    echo
    echo "[ERRO] Falha na instalação das dependências"
    exit 1
fi

echo
echo "============================================================"
echo " INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "============================================================"
echo
echo "Próximos passos:"
echo
echo "1. Configure empresas de demonstração:"
echo "   python3 setup_demo.py"
echo
echo "2. Inicie o servidor web:"
echo "   python3 web_server.py"
echo
echo "3. Acesse no navegador:"
echo "   http://localhost:5000"
echo
echo "============================================================"
