#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste rápido da economia do jogo"""

import sys
sys.path.append('src')

from config.constants import GameConfig

def analisar_economia():
    produtos = GameConfig.get_produtos_inicializados()
    custos = GameConfig.CUSTOS_UNITARIOS_RECURSOS
    
    print("=== ANÁLISE ECONÔMICA ATUAL ===\n")
    
    for nome, dados in produtos.items():
        # Calcular custos por produto
        custo_materia = dados['custo_materia'] * custos['materia_prima']
        custo_energia = dados['custo_energia'] * custos['energia']
        custo_trabalhadores = dados['custo_trabalhadores'] * custos['trabalhadores']
        custo_total = custo_materia + custo_energia + custo_trabalhadores
        
        # Calcular lucro
        preco = dados['preco_venda']
        lucro = preco - custo_total
        margem = (lucro / preco) * 100 if preco > 0 else 0
        
        print(f"{dados['emoji']} {nome}:")
        print(f"  Preço de venda: ${preco:,.2f}")
        print(f"  Custos detalhados:")
        print(f"    - Matéria-prima: {dados['custo_materia']} × ${custos['materia_prima']} = ${custo_materia:,.2f}")
        print(f"    - Energia: {dados['custo_energia']} × ${custos['energia']} = ${custo_energia:,.2f}")
        print(f"    - Trabalhadores: {dados['custo_trabalhadores']} × ${custos['trabalhadores']} = ${custo_trabalhadores:,.2f}")
        print(f"  CUSTO TOTAL: ${custo_total:,.2f}")
        print(f"  LUCRO: ${lucro:,.2f} ({margem:+.1f}%)")
        
        if lucro > 0:
            print("  ✅ LUCRATIVO")
        else:
            print("  ❌ PREJUÍZO")
        print()

if __name__ == "__main__":
    analisar_economia()