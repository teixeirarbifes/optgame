# -*- coding: utf-8 -*-
"""
Script para corrigir lucros no JSON que foram calculados sem sinergias
"""
import sys
sys.path.insert(0, 'src')
import json

from config.constants import GameConfig
from mecanicas.mechanics import GameMechanics

def calcular_bonus_sinergias(decisoes, produtos):
    """Calcular bônus monetário das sinergias ativas"""
    bonus_total = 0.0
    
    # Definição de sinergias
    grupos_sinergia = [
        {
            'produtos': ['Smartphone', 'Smartwatch'],
            'bonus': 1.15,
            'threshold_min': 10
        },
        {
            'produtos': ['Desktop', 'Laptop'],
            'bonus': 1.10,
            'threshold_min': 10
        },
        {
            'produtos': ['Camera', 'Smartphone'],
            'bonus': 1.12,
            'threshold_min': 5
        }
    ]
    
    # Para cada grupo de sinergia
    for grupo in grupos_sinergia:
        # Encontrar quantidade mínima comum entre produtos do grupo
        quantidades = []
        for produto in grupo['produtos']:
            qtd = decisoes.get(produto, 0)
            if qtd >= grupo['threshold_min']:
                quantidades.append(qtd)
        
        # Se todos os produtos do grupo atingem o threshold
        if len(quantidades) >= 2:
            qtd_minima = min(quantidades)
            
            # Aplicar bônus na quantidade mínima de cada produto
            for produto in grupo['produtos']:
                if decisoes.get(produto, 0) >= grupo['threshold_min']:
                    dados_produto = produtos.get(produto, {})
                    preco = dados_produto.get('preco_venda', 0)
                    
                    # Calcular custo unitário
                    custo_unitario = (
                        dados_produto.get('consumo_materia', 0) * GameConfig.CUSTOS_UNITARIOS_RECURSOS['materia_prima'] +
                        dados_produto.get('consumo_energia', 0) * GameConfig.CUSTOS_UNITARIOS_RECURSOS['energia'] +
                        dados_produto.get('consumo_trabalhadores', 0) * GameConfig.CUSTOS_UNITARIOS_RECURSOS['trabalhadores']
                    )
                    
                    margem_base = preco - custo_unitario
                    bonus_margem = qtd_minima * margem_base * (grupo['bonus'] - 1)
                    bonus_total += bonus_margem
    
    return bonus_total

def corrigir_json(arquivo_entrada, arquivo_saida):
    """Corrige os lucros no JSON adicionando bônus de sinergias"""
    
    print("="*80)
    print("🔧 CORREÇÃO DE LUCROS NO JSON")
    print("="*80)
    
    # Carregar JSON
    print(f"\n📂 Carregando: {arquivo_entrada}")
    with open(arquivo_entrada, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    empresas = dados.get('empresas', {})
    print(f"   Empresas encontradas: {len(empresas)}")
    
    # Processar cada empresa
    for nome_empresa, empresa in empresas.items():
        print(f"\n{'='*80}")
        print(f"🏢 Empresa: {nome_empresa}")
        print(f"{'='*80}")
        
        historico = empresa.get('historico', [])
        if not historico:
            print("   ⚠️  Sem histórico, pulando...")
            continue
        
        # Corrigir cada turno no histórico
        for i, turno in enumerate(historico, 1):
            decisao = turno.get('decisao', {})
            lucro_antigo = turno.get('lucro', 0)
            
            if not decisao or all(v == 0 for v in decisao.values()):
                print(f"   Turno {i}: Sem produção, pulando...")
                continue
            
            # Calcular consumo para validar restrições
            consumo = GameMechanics.calcular_consumo_recursos(GameConfig.PRODUTOS, decisao)
            
            # Validar restrições (incluindo chips e engenheiros)
            recursos_disponiveis = {
                'materia_prima': GameConfig.RECURSOS_BASE['materia_prima'],
                'energia': GameConfig.RECURSOS_BASE['energia'],
                'trabalhadores': GameConfig.RECURSOS_BASE['trabalhadores'],
                'chips_processamento': GameConfig.RECURSOS_BASE['chips_processamento'],
                'engenheiros_senior': GameConfig.RECURSOS_BASE['engenheiros_senior']
            }
            
            violacoes = []
            EPSILON = 1e-6
            for recurso in recursos_disponiveis.keys():
                necessario = consumo.get(recurso, 0)
                disponivel = recursos_disponiveis.get(recurso, 0)
                if necessario > disponivel + EPSILON:
                    violacoes.append({
                        'recurso': recurso,
                        'necessario': necessario,
                        'disponivel': disponivel,
                        'deficit': necessario - disponivel
                    })
            
            # Se violou restrições, lucro = 0
            if violacoes:
                lucro_novo = 0
                print(f"   Turno {i}: ❌ VIOLAÇÃO DE RESTRIÇÕES!")
                for v in violacoes:
                    print(f"      • {v['recurso']}: {v['necessario']:.2f} > {v['disponivel']:.2f} (deficit: {v['deficit']:.2f})")
                print(f"      Lucro ZERADO (era R$ {lucro_antigo:,.2f})")
            else:
                # Calcular lucro base (sem sinergia)
                metricas = GameMechanics.calcular_metricas_plano(GameConfig.PRODUTOS, decisao)
                lucro_base = metricas['lucro']
                
                # Calcular bônus de sinergias
                bonus = calcular_bonus_sinergias(decisao, GameConfig.PRODUTOS)
                
                # Lucro corrigido
                lucro_novo = lucro_base + bonus
            
            # Atualizar no JSON
            turno['lucro'] = round(lucro_novo, 2)
            
            # Mostrar diferença
            diferenca = lucro_novo - lucro_antigo
            if abs(diferenca) > 0.01:
                print(f"   Turno {i}:")
                print(f"      Produção: {decisao}")
                print(f"      Lucro Base: R$ {lucro_base:,.2f}")
                print(f"      Bônus Sinergia: R$ {bonus:,.2f}")
                print(f"      Lucro ANTIGO: R$ {lucro_antigo:,.2f}")
                print(f"      Lucro NOVO: R$ {lucro_novo:,.2f}")
                percentual = (diferenca/lucro_antigo*100) if lucro_antigo != 0 else 0
                print(f"      Diferença: R$ {diferenca:,.2f} ({percentual:.1f}%)")
            else:
                print(f"   Turno {i}: Lucro já estava correto (R$ {lucro_antigo:,.2f})")
        
        # Atualizar lucro_ultimo_turno se existir
        if historico:
            ultimo_turno = historico[-1]
            empresa['lucro_ultimo_turno'] = ultimo_turno.get('lucro', 0)
            print(f"\n   📊 Lucro Último Turno atualizado: R$ {empresa['lucro_ultimo_turno']:,.2f}")
    
    # Salvar JSON corrigido
    print(f"\n{'='*80}")
    print(f"💾 Salvando arquivo corrigido: {arquivo_saida}")
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    
    print(f"✅ CONCLUÍDO!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    import os
    
    # Arquivos
    arquivo_entrada = r"C:\Users\rafae\Downloads\POINT2B.json"
    arquivo_saida = r"C:\Users\rafae\Downloads\POINT2B_CORRIGIDO.json"
    
    if not os.path.exists(arquivo_entrada):
        print(f"❌ ERRO: Arquivo não encontrado: {arquivo_entrada}")
        sys.exit(1)
    
    corrigir_json(arquivo_entrada, arquivo_saida)
    
    print("\n📝 RESUMO:")
    print(f"   Entrada:  {arquivo_entrada}")
    print(f"   Saída:    {arquivo_saida}")
    print(f"\n🎯 Agora você pode carregar o arquivo corrigido no jogo!")
