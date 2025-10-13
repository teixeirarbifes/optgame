# -*- coding: utf-8 -*-
"""
Teste do otimizador com dados do Turno 3 (onde PCTEC bateu o otimizador)
"""
import sys
sys.path.insert(0, 'src')

from web_app.optimizer import ProductionOptimizer
from config.constants import GameConfig

# Recursos disponíveis no Turno 3 (do JSON)
recursos_turno3 = {
    'dinheiro': 50000,
    'materia_prima': 20000,
    'energia': 15000,
    'trabalhadores': 600,
    'chips_processamento': 1800,
    'engenheiros_senior': 350
}

print("="*80)
print("🧪 TESTE: Otimizador vs PCTEC (Turno 3)")
print("="*80)
print("\n📊 Recursos Disponíveis:")
for recurso, valor in recursos_turno3.items():
    print(f"   {recurso}: {valor:,.2f}")

print("\n💰 Produtos disponíveis:")
for produto, dados in GameConfig.PRODUTOS.items():
    preco = dados['preco_venda']
    materia = dados['consumo_materia']
    energia = dados['consumo_energia']
    trabalhadores = dados['consumo_trabalhadores']
    chips = dados.get('consumo_chips_processamento', 0)
    engenheiros = dados.get('consumo_engenheiros_senior', 0)
    
    # Calcular custo
    custo = (
        materia * GameConfig.CUSTOS_UNITARIOS_RECURSOS['materia_prima'] +
        energia * GameConfig.CUSTOS_UNITARIOS_RECURSOS['energia'] +
        trabalhadores * GameConfig.CUSTOS_UNITARIOS_RECURSOS['trabalhadores']
    )
    margem = preco - custo
    
    print(f"\n   {produto}:")
    print(f"      Preço: R$ {preco:.2f}")
    print(f"      Custo: R$ {custo:.2f}")
    print(f"      Margem: R$ {margem:.2f}")
    print(f"      Chips: {chips:.1f} | Engenheiros: {engenheiros:.2f}")

print("\n" + "="*80)
print("🚀 Executando Otimizador...")
print("="*80)

optimizer = ProductionOptimizer()
resultado = optimizer.otimizar_producao(recursos_turno3)

if resultado['sucesso']:
    print("\n✅ OTIMIZAÇÃO CONCLUÍDA")
    print(f"   Status: {resultado['status']}")
    print(f"   💵 Lucro Esperado: R$ {resultado['lucro_esperado']:,.2f}")
    
    print("\n📦 Produção Ótima:")
    for produto, qtd in resultado['producao_otima'].items():
        if qtd > 0.01:
            print(f"   {produto}: {qtd:.2f} unidades")
    
    print("\n📊 Recursos Utilizados:")
    for recurso, qtd in resultado['recursos_utilizados'].items():
        disponivel = recursos_turno3.get(recurso, 0)
        percentual = (qtd / disponivel * 100) if disponivel > 0 else 0
        print(f"   {recurso}: {qtd:,.2f} / {disponivel:,.2f} ({percentual:.1f}%)")
    
    print("\n📊 Recursos Restantes:")
    for recurso, qtd in resultado['recursos_restantes'].items():
        disponivel = recursos_turno3.get(recurso, 0)
        print(f"   {recurso}: {qtd:,.2f} / {disponivel:,.2f}")
    
    print("\n" + "="*80)
    print("🎯 COMPARAÇÃO:")
    print("="*80)
    print(f"   PCTEC (alunos):       R$ 82,707.35")
    print(f"   Otimizador (atual):   R$ {resultado['lucro_esperado']:,.2f}")
    
    diferenca = resultado['lucro_esperado'] - 82707.35
    percentual = (diferenca / 82707.35) * 100
    
    if diferenca > 0:
        print(f"   ✅ Otimizador GANHOU: +R$ {diferenca:,.2f} (+{percentual:.2f}%)")
    else:
        print(f"   ❌ Otimizador PERDEU: R$ {abs(diferenca):,.2f} ({percentual:.2f}%)")
    
else:
    print(f"\n❌ ERRO: {resultado.get('mensagem', 'Desconhecido')}")
    print(f"   Status: {resultado.get('status', 'N/A')}")

print("\n" + "="*80)
