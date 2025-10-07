#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Teste de conectividade com o servidor"""

import urllib.request
import urllib.error

urls_teste = [
    'http://localhost:5000/',
    'http://localhost:5000/admin',
    'http://localhost:5000/admin/login',
    'http://localhost:5000/aluno',
    'http://localhost:5000/aluno/login',
    'http://localhost:5000/api/status',
]

print("\n" + "="*60)
print("TESTE DE CONECTIVIDADE")
print("="*60 + "\n")

for url in urls_teste:
    try:
        response = urllib.request.urlopen(url, timeout=5)
        status = response.getcode()
        content_type = response.headers.get('Content-Type', '')
        print(f"✓ {url}")
        print(f"  Status: {status}")
        print(f"  Type: {content_type}")
        print()
    except urllib.error.HTTPError as e:
        print(f"✗ {url}")
        print(f"  Erro HTTP: {e.code} - {e.reason}")
        print()
    except urllib.error.URLError as e:
        print(f"✗ {url}")
        print(f"  Erro URL: {e.reason}")
        print()
    except Exception as e:
        print(f"✗ {url}")
        print(f"  Erro: {e}")
        print()

print("="*60 + "\n")
