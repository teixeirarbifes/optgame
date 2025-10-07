#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para inicializar o jogo com dados de demonstração
Execute este arquivo para criar empresas de exemplo
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.web_app.game_state import game_state

def setup_demo():
    """Configurar jogo com empresas de demonstração"""
    
    print("\n" + "="*60)
    print("🎮 CONFIGURAÇÃO INICIAL - JOGO DE PRODUÇÃO")
    print("="*60 + "\n")
    
    # Resetar jogo
    game_state.reset_game()
    print("✓ Jogo resetado\n")
    
    # Empresas de demonstração
    empresas_demo = [
        {
            'nome': 'TechCorp',
            'equipe': 'Equipe Alpha',
            'senha': 'TECH2024'
        },
        {
            'nome': 'InnovaTech',
            'equipe': 'Equipe Beta',
            'senha': 'INNO2024'
        },
        {
            'nome': 'GlobalProd',
            'equipe': 'Equipe Gamma',
            'senha': 'GLOB2024'
        },
        {
            'nome': 'MegaFactory',
            'equipe': 'Equipe Delta',
            'senha': 'MEGA2024'
        }
    ]
    
    print("Criando empresas de demonstração:\n")
    
    for empresa in empresas_demo:
        sucesso = game_state.adicionar_empresa(
            nome=empresa['nome'],
            equipe=empresa['equipe'],
            senha=empresa['senha']
        )
        
        if sucesso:
            print(f"✓ {empresa['nome']}")
            print(f"  Equipe: {empresa['equipe']}")
            print(f"  Senha: {empresa['senha']}")
            print()
        else:
            print(f"✗ Erro ao criar {empresa['nome']}\n")
    
    # Salvar estado
    caminho_demo = os.path.join(os.path.dirname(__file__), 'demo_state.json')
    game_state.salvar_estado(caminho_demo)
    print(f"✓ Estado salvo em: {caminho_demo}\n")
    
    print("="*60)
    print("✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("="*60)
    print("\n📋 PRÓXIMOS PASSOS:\n")
    print("1. Execute: python web_server.py")
    print("2. Acesse: http://localhost:5000/admin")
    print("   Senha Admin: admin123")
    print("\n3. Login dos Alunos: http://localhost:5000/aluno")
    print("\n🏢 EMPRESAS CRIADAS:")
    for empresa in empresas_demo:
        print(f"\n   • {empresa['nome']}")
        print(f"     Senha: {empresa['senha']}")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    setup_demo()
