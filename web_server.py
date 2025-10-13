#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Servidor Web Principal do Jogo de Produção
Execute este arquivo para iniciar o servidor web
"""

import os
import sys

# Adicionar o diretório atual e src ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

# Importar a aplicação
from web_app import create_app

if __name__ == '__main__':
    app = create_app()
    
    print("\n" + "="*60)
    print("🎮 SERVIDOR WEB DO JOGO DE PRODUÇÃO")
    print("="*60)
    print("\n📌 Acesso Local:")
    print("   http://localhost:5000")
    print("\n👨‍🏫 Área Administrativa:")
    print("   http://localhost:5000/admin")
    print("\n👨‍🎓 Área dos Alunos:")
    print("   http://localhost:5000/aluno")
    print("\n" + "="*60 + "\n")
    
    # Executar servidor
    app.run(
        host='0.0.0.0',  # Acessível na rede
        port=5000,
        debug=True,
        threaded=True
    )
