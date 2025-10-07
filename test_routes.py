#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Teste de rotas da aplicação"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

print("Testando importação...")

try:
    from web_app import create_app
    print("✓ Importação bem-sucedida!")
    
    app = create_app()
    print("✓ App criada!")
    
    print("\nRotas registradas:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"  {rule.endpoint:30s} {methods:20s} {rule.rule}")
    
    print("\nBluePrints registrados:")
    for bp_name, bp in app.blueprints.items():
        print(f"  - {bp_name}")
    
    print("\n✅ Tudo OK! Servidor pode ser iniciado.")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
