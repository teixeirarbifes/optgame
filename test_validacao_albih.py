# -*- coding: utf-8 -*-
"""
Teste: Validar decisão da ALBIH que deu R$ 91k
"""
import sys
sys.path.insert(0, 'src')

from web_app.optimizer import ProductionOptimizer
from config.constants import GameConfig
from mecanicas.mechanics import GameMechanics

# Decisão da ALBIH no Turno 3
decisao_albih = {
    'Smartphone': 130,
    'Laptop': 280,
    'Desktop': 140,
    'Smartwatch': 100,
    'Impressora': 100,
    'Camera': 140
}

# Recursos disponíveis
recursos = {
    'dinheiro': 50000,
    'materia_prima': 20000,
    'energia': 15000,
    'trabalhadores': 600,
    'chips_processamento': 1800,
    'engenheiros_senior': 350
}

print("="*80)
print("🔍 VALIDANDO DECISÃO DA ALBIH")
print("="*80)

print(f"\n📦 Decisão:")
for produto, qtd in decisao_albih.items():
    if qtd > 0:
        print(f"   {produto}: {qtd}")

# Calcular consumo de recursos
consumo = GameMechanics.calcular_consumo_recursos(GameConfig.PRODUTOS, decisao_albih)

print(f"\n📊 Consumo de Recursos:")
violacoes = []
for recurso in ['materia_prima', 'energia', 'trabalhadores', 'chips_processamento', 'engenheiros_senior']:
    necessario = consumo.get(recurso, 0)
    disponivel = recursos.get(recurso, 0)
    percentual = (necessario / disponivel * 100) if disponivel > 0 else 0
    status = "✅" if necessario <= disponivel else "❌ VIOLAÇÃO"
    print(f"   {recurso}: {necessario:,.2f} / {disponivel:,.2f} ({percentual:.1f}%) {status}")
    
    if necessario > disponivel:
        violacoes.append({
            'recurso': recurso,
            'deficit': necessario - disponivel
        })

# Calcular lucro
metricas = GameMechanics.calcular_metricas_plano(GameConfig.PRODUTOS, decisao_albih)
lucro_base = metricas['lucro']

# Calcular sinergias manualmente
def calcular_bonus_sinergias(decisoes, produtos):
    bonus_total = 0.0
    grupos_sinergia = [
        {'produtos': ['Smartphone', 'Smartwatch'], 'bonus': 1.15, 'threshold_min': 10},
        {'produtos': ['Desktop', 'Laptop'], 'bonus': 1.10, 'threshold_min': 10},
        {'produtos': ['Camera', 'Smartphone'], 'bonus': 1.12, 'threshold_min': 5}
    ]
    
    for grupo in grupos_sinergia:
        quantidades = []
        for produto in grupo['produtos']:
            qtd = decisoes.get(produto, 0)
            if qtd >= grupo['threshold_min']:
                quantidades.append(qtd)
        
        if len(quantidades) >= 2:
            qtd_minima = min(quantidades)
            for produto in grupo['produtos']:
                if decisoes.get(produto, 0) >= grupo['threshold_min']:
                    dados_produto = produtos.get(produto, {})
                    preco = dados_produto.get('preco_venda', 0)
                    custo_unitario = (
                        dados_produto.get('consumo_materia', 0) * GameConfig.CUSTOS_UNITARIOS_RECURSOS['materia_prima'] +
                        dados_produto.get('consumo_energia', 0) * GameConfig.CUSTOS_UNITARIOS_RECURSOS['energia'] +
                        dados_produto.get('consumo_trabalhadores', 0) * GameConfig.CUSTOS_UNITARIOS_RECURSOS['trabalhadores']
                    )
                    margem_base = preco - custo_unitario
                    bonus_margem = qtd_minima * margem_base * (grupo['bonus'] - 1)
                    bonus_total += bonus_margem
    
    return bonus_total

bonus = calcular_bonus_sinergias(decisao_albih, GameConfig.PRODUTOS)
lucro_total = lucro_base + bonus

print(f"\n💰 Lucro:")
print(f"   Base: R$ {lucro_base:,.2f}")
print(f"   Bônus Sinergia: R$ {bonus:,.2f}")
print(f"   TOTAL: R$ {lucro_total:,.2f}")

if violacoes:
    print(f"\n❌ DECISÃO INVÁLIDA - {len(violacoes)} violação(ões):")
    for v in violacoes:
        print(f"   • {v['recurso']}: deficit de {v['deficit']:.2f}")
    print(f"\n   Lucro real deveria ser: R$ 0.00")
else:
    print(f"\n✅ DECISÃO VÁLIDA")
    print(f"\n🤔 MAS O OTIMIZADOR DISSE QUE O ÓTIMO É R$ 86,225...")
    print(f"   Isso significa que o OTIMIZADOR TEM UM BUG!")

print("\n" + "="*80)
print("🚀 Testando o Otimizador...")
print("="*80)

optimizer = ProductionOptimizer()
resultado = optimizer.otimizar_producao(recursos)

print(f"\n💵 Otimizador calculou: R$ {resultado['lucro_esperado']:,.2f}")
print(f"\n📦 Solução do Otimizador:")
for produto, qtd in resultado['producao_otima'].items():
    if qtd > 0.01:
        print(f"   {produto}: {qtd:.2f}")

print(f"\n🎯 COMPARAÇÃO:")
print(f"   ALBIH conseguiu:       R$ {lucro_total:,.2f}")
print(f"   Otimizador conseguiu:  R$ {resultado['lucro_esperado']:,.2f}")

diferenca = lucro_total - resultado['lucro_esperado']
if diferenca > 0:
    print(f"\n❌ ALBIH BATEU O OTIMIZADOR POR R$ {diferenca:,.2f}!")
    print(f"   Isso indica BUG NO OTIMIZADOR (não está encontrando o ótimo real)")
else:
    print(f"\n✅ Otimizador está correto")

print("\n" + "="*80)
