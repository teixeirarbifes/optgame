#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script de teste para verificar configuração"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.web_app.game_state import game_state

print("\n" + "="*50)
print("TESTE DE CONFIGURAÇÃO")
print("="*50)

print(f"\n✓ Senha Admin: '{game_state.admin_password}'")
print(f"✓ Tipo: {type(game_state.admin_password)}")
print(f"✓ Tamanho: {len(game_state.admin_password)} caracteres")
print(f"✓ Iteração Atual: {game_state.iteracao_atual}")
print(f"✓ Max Iterações: {game_state.max_iteracoes}")
print(f"✓ Empresas: {len(game_state.empresas)}")
print(f"✓ Produtos: {len(game_state.produtos)}")

print("\n" + "="*50)
print("TESTE DE COMPARAÇÃO DE SENHA")
print("="*50)

teste_senhas = ["admin123", " admin123", "admin123 ", "Admin123", "ADMIN123"]
for senha in teste_senhas:
    match = senha == game_state.admin_password
    print(f"'{senha}' == '{game_state.admin_password}' ? {match}")

print("\n" + "="*50)
print("✅ Configuração OK!")
print("="*50 + "\n")
