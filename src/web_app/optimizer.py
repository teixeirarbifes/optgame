# -*- coding: utf-8 -*-
"""
Otimizador de Produção usando PuLP
Calcula a solução ótima para maximizar lucro dadas as restrições de recursos
Trade-off: Sinergias de Mercado
"""

try:
    from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus, value, LpContinuous
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False
    print("AVISO: PuLP não instalado. Funcionalidade de otimização não disponível.")
    print("Instale com: pip install pulp")

from config.constants import GameConfig


def arredondar_producao(valor, decimais=2):
    """
    Arredonda valor de produção/consumo evitando problemas de ponto flutuante.
    Se o valor está muito próximo de um inteiro, arredonda para inteiro.
    """
    arredondado = round(valor, decimais)
    # Se está muito próximo de zero, retorna zero
    if abs(arredondado) < 0.001:
        return 0
    # Se está muito próximo de um inteiro, retorna inteiro
    if abs(arredondado - round(arredondado)) < 0.001:
        return round(arredondado)
    return arredondado


class ProductionOptimizer:
    """Otimizador de produção para maximizar lucro com sinergias de mercado"""
    
    def __init__(self):
        self.produtos = GameConfig.PRODUTOS
        self.custos_recursos = GameConfig.CUSTOS_UNITARIOS_RECURSOS
        self.recursos_base = GameConfig.RECURSOS_BASE
        
        # TRADE-OFF: Sinergias de Mercado
        # Produzir produtos complementares gera bônus de margem
        self.grupos_sinergia = [
            {
                'produtos': ['Smartphone', 'Smartwatch'],
                'bonus': 1.15,  # +15% margem
                'threshold_min': 10,
                'descricao': 'Ecossistema móvel'
            },
            {
                'produtos': ['Desktop', 'Laptop'],
                'bonus': 1.10,  # +10% margem
                'threshold_min': 10,
                'descricao': 'Linha de computação'
            },
            {
                'produtos': ['Camera', 'Smartphone'],
                'bonus': 1.12,  # +12% margem
                'threshold_min': 5,
                'descricao': 'Fotografia integrada'
            }
        ]
    
    def otimizar_producao(self, recursos_disponiveis: dict, produtos_customizados: dict = None) -> dict:
        """
        Calcula a produção ótima para maximizar o lucro com trade-offs avançados
        
        Args:
            recursos_disponiveis: Dict com recursos disponíveis da empresa
                {
                    'dinheiro': float,
                    'materia_prima': float,
                    'energia': float,
                    'trabalhadores': float
                }
            produtos_customizados: Dict com produtos customizados (opcional)
                Se fornecido, usa estes custos ao invés dos padrão
        
        Returns:
            dict: Resultado da otimização
                {
                    'sucesso': bool,
                    'status': str,
                    'producao_otima': {produto: quantidade, ...},
                    'lucro_esperado': float,
                    'recursos_utilizados': {recurso: quantidade, ...},
                    'recursos_restantes': {recurso: quantidade, ...},
                    'detalhes': dict,
                    'trade_offs': dict  # Informações sobre trade-offs ativos
                }
        """
        if not PULP_AVAILABLE:
            return {
                'sucesso': False,
                'status': 'ERRO',
                'mensagem': 'PuLP não está instalado. Execute: pip install pulp'
            }
        
        # Usar produtos customizados se fornecidos, senão usar padrão
        produtos_para_otimizacao = produtos_customizados if produtos_customizados else self.produtos
        
        # DEBUG: Log dos recursos disponíveis
        print("\n" + "="*80)
        print("🔍 OTIMIZADOR - Recursos Disponíveis:")
        print(f"   💰 Dinheiro: R$ {recursos_disponiveis.get('dinheiro', 0):,.2f}")
        print(f"   📦 Matéria-prima: {recursos_disponiveis.get('materia_prima', 0):,.2f}")
        print(f"   ⚡ Energia: {recursos_disponiveis.get('energia', 0):,.2f}")
        print(f"   👷 Trabalhadores: {recursos_disponiveis.get('trabalhadores', 0):,.2f}")
        print("="*80)
        
        try:
            # Criar problema de otimização
            prob = LpProblem("Maximizar_Lucro_Producao_Com_Sinergias", LpMaximize)
            
            # Variáveis de decisão: quantidade a produzir de cada produto (CONTÍNUAS)
            produtos_vars = {}
            for produto_nome in produtos_para_otimizacao.keys():
                var_nome = self._sanitize_name(produto_nome)
                produtos_vars[produto_nome] = LpVariable(
                    var_nome, 
                    lowBound=0, 
                    cat='Continuous'  # Permite valores decimais
                )
            
            # ========================================================================
            # SINERGIAS: Variável para quantidade com bônus (MIN entre produtos)
            # ========================================================================
            vars_sinergia_qtd = {}  # Quantidade que recebe bônus de sinergia
            
            for i, grupo in enumerate(self.grupos_sinergia):
                produtos_grupo = [p for p in grupo['produtos'] if p in produtos_para_otimizacao]
                
                if len(produtos_grupo) >= 2:
                    # Criar variável para quantidade mínima sinérgica
                    var_qtd_minima = LpVariable(
                        f"sinergia_qtd_min_{i}",
                        lowBound=0,
                        cat='Continuous'
                    )
                    vars_sinergia_qtd[i] = {
                        'var': var_qtd_minima,
                        'produtos': produtos_grupo,
                        'grupo': grupo
                    }
                    
                    # Restrições: qtd_minima <= produção de CADA produto
                    for produto in produtos_grupo:
                        prob += (
                            var_qtd_minima <= produtos_vars[produto],
                            f"Sinergia_{i}_Min_{self._sanitize_name(produto)}"
                        )
                    
                    # Restrição: qtd_minima >= threshold para ativar
                    # (Opcional: pode remover se quiser bônus proporcional desde zero)
                    # prob += (
                    #     var_qtd_minima >= grupo['threshold_min'],
                    #     f"Sinergia_{i}_Threshold"
                    # )
            
            # ========================================================================
            # FUNÇÃO OBJETIVO: Maximizar lucro líquido (Receita - Custo + Bônus Sinergia)
            # ========================================================================
            lucro_total = 0
            
            # Lucro base de cada produto
            for produto, produto_info in produtos_para_otimizacao.items():
                qtd = produtos_vars[produto]
                preco_venda = produto_info['preco_venda']
                
                # Custo unitário de produção
                custo_unitario = (
                    produto_info['consumo_materia'] * self.custos_recursos['materia_prima'] +
                    produto_info['consumo_energia'] * self.custos_recursos['energia'] +
                    produto_info['consumo_trabalhadores'] * self.custos_recursos['trabalhadores']
                )
                
                # Lucro = (Preço - Custo) × Quantidade
                margem_unitaria = preco_venda - custo_unitario
                lucro_total += qtd * margem_unitaria
            
            # Aplicar bônus de sinergia (apenas na quantidade mínima comum)
            for i, sinergia_info in vars_sinergia_qtd.items():
                grupo = sinergia_info['grupo']
                qtd_minima = sinergia_info['var']
                produtos_grupo = sinergia_info['produtos']
                
                # Bônus aplicado em CADA produto do grupo, mas só na qtd mínima
                for produto in produtos_grupo:
                    if produto in produtos_para_otimizacao:
                        preco = produtos_para_otimizacao[produto]['preco_venda']
                        
                        # Calcular custo médio da quantidade mínima (usando eficiência média)
                        # Para simplificar, usar eficiência da primeira faixa que tem produção
                        # ou 0.75 se tiver volume alto
                        custo_unitario = (
                            produtos_para_otimizacao[produto]['consumo_materia'] * self.custos_recursos['materia_prima'] +
                            produtos_para_otimizacao[produto]['consumo_energia'] * self.custos_recursos['energia'] +
                            produtos_para_otimizacao[produto]['consumo_trabalhadores'] * self.custos_recursos['trabalhadores']
                        )
                        margem_base = preco - custo_unitario
                        
                        # Bônus na margem (ex: +15% = 0.15 x margem)
                        bonus_margem = qtd_minima * margem_base * (grupo['bonus'] - 1)
                        lucro_total += bonus_margem
            
            prob += lucro_total, "Lucro_Total_Com_TradeOffs"
            
            # ========================================================================
            # RESTRIÇÕES DE RECURSOS
            # ========================================================================
            
            # 1. Matéria-prima disponível
            consumo_materia_total = lpSum([
                produtos_vars[prod] * produtos_para_otimizacao[prod]['consumo_materia']
                for prod in produtos_para_otimizacao.keys()
            ])
            prob += (
                consumo_materia_total <= recursos_disponiveis['materia_prima'],
                "Restricao_Materia_Prima"
            )
            
            # 2. Energia disponível
            consumo_energia_total = lpSum([
                produtos_vars[prod] * produtos_para_otimizacao[prod]['consumo_energia']
                for prod in produtos_para_otimizacao.keys()
            ])
            prob += (
                consumo_energia_total <= recursos_disponiveis['energia'],
                "Restricao_Energia"
            )
            
            # 3. Trabalhadores disponíveis
            consumo_trabalho_total = lpSum([
                produtos_vars[prod] * produtos_para_otimizacao[prod]['consumo_trabalhadores']
                for prod in produtos_para_otimizacao.keys()
            ])
            prob += (
                consumo_trabalho_total <= recursos_disponiveis['trabalhadores'],
                "Restricao_Trabalhadores"
            )
            
            # 4. Restrição de dinheiro (custos totais)
            custos_totais = lpSum([
                produtos_vars[prod] * (
                    produtos_para_otimizacao[prod]['consumo_materia'] * self.custos_recursos['materia_prima'] +
                    produtos_para_otimizacao[prod]['consumo_energia'] * self.custos_recursos['energia'] +
                    produtos_para_otimizacao[prod]['consumo_trabalhadores'] * self.custos_recursos['trabalhadores']
                )
                for prod in produtos_para_otimizacao.keys()
            ])
            prob += (
                custos_totais <= recursos_disponiveis['dinheiro'],
                "Restricao_Dinheiro"
            )
            
            # 5. Chips de Processamento
            if 'chips_processamento' in recursos_disponiveis:
                consumo_chips = lpSum([
                    produtos_vars[prod] * produtos_para_otimizacao[prod].get('consumo_chips_processamento', 0)
                    for prod in produtos_para_otimizacao.keys()
                ])
                prob += (
                    consumo_chips <= recursos_disponiveis['chips_processamento'],
                    "Restricao_Chips_Processamento"
                )
            
            # 6. Engenheiros Sênior
            if 'engenheiros_senior' in recursos_disponiveis:
                consumo_engenheiros = lpSum([
                    produtos_vars[prod] * produtos_para_otimizacao[prod].get('consumo_engenheiros_senior', 0)
                    for prod in produtos_para_otimizacao.keys()
                ])
                prob += (
                    consumo_engenheiros <= recursos_disponiveis['engenheiros_senior'],
                    "Restricao_Engenheiros_Senior"
                )
            
            # ========================================================================
            # RESOLVER O PROBLEMA
            # ========================================================================
            prob.solve()
            
            # Extrair resultados
            status = LpStatus[prob.status]
            
            if status != 'Optimal':
                return {
                    'sucesso': False,
                    'status': status,
                    'mensagem': f'Otimização não encontrou solução ótima. Status: {status}'
                }
            
            # ========================================================================
            # EXTRAIR SOLUÇÃO ÓTIMA
            # ========================================================================
            producao_otima = {}
            for produto, var in produtos_vars.items():
                quantidade = value(var) or 0
                if quantidade > 0.01:  # Threshold para considerar produção
                    producao_otima[produto] = arredondar_producao(quantidade, 2)
            
            # ========================================================================
            # CALCULAR RECURSOS UTILIZADOS E LUCRO
            # ========================================================================
            recursos_utilizados = {
                'materia_prima': 0,
                'energia': 0,
                'trabalhadores': 0,
                'dinheiro': 0
            }
            
            receita_total = 0
            custo_total = 0
            
            for produto, quantidade in producao_otima.items():
                produto_info = produtos_para_otimizacao[produto]
                preco_venda = produto_info['preco_venda']
                
                # Calcular consumo de recursos físicos
                consumo_materia = quantidade * produto_info['consumo_materia']
                consumo_energia = quantidade * produto_info['consumo_energia']
                consumo_trabalho = quantidade * produto_info['consumo_trabalhadores']
                
                recursos_utilizados['materia_prima'] += arredondar_producao(consumo_materia, 2)
                recursos_utilizados['energia'] += arredondar_producao(consumo_energia, 2)
                recursos_utilizados['trabalhadores'] += arredondar_producao(consumo_trabalho, 2)
                
                # Calcular custo monetário
                custo_produto = (
                    consumo_materia * self.custos_recursos['materia_prima'] +
                    consumo_energia * self.custos_recursos['energia'] +
                    consumo_trabalho * self.custos_recursos['trabalhadores']
                )
                
                # Calcular receita
                receita_produto = quantidade * preco_venda
                
                receita_total += receita_produto
                custo_total += custo_produto
            
            # Adicionar bônus de sinergia à receita (aplicado na qtd mínima)
            for i, sinergia_info in vars_sinergia_qtd.items():
                grupo = sinergia_info['grupo']
                qtd_minima_var = sinergia_info['var']
                qtd_minima = value(qtd_minima_var) or 0
                
                if qtd_minima >= grupo['threshold_min']:
                    for produto in sinergia_info['produtos']:
                        if produto in producao_otima:
                            preco = produtos_para_otimizacao[produto]['preco_venda']
                            custo_unitario = (
                                produtos_para_otimizacao[produto]['consumo_materia'] * self.custos_recursos['materia_prima'] +
                                produtos_para_otimizacao[produto]['consumo_energia'] * self.custos_recursos['energia'] +
                                produtos_para_otimizacao[produto]['consumo_trabalhadores'] * self.custos_recursos['trabalhadores']
                            )
                            margem_base = preco - custo_unitario
                            bonus_receita = qtd_minima * margem_base * (grupo['bonus'] - 1)
                            receita_total += bonus_receita
            
            recursos_utilizados['dinheiro'] = arredondar_producao(custo_total, 2)
            
            # Recursos restantes (arredondados para evitar -0.0)
            recursos_restantes = {
                recurso: arredondar_producao(recursos_disponiveis[recurso] - recursos_utilizados[recurso], 2)
                for recurso in recursos_utilizados.keys()
            }
            
            # Lucro esperado
            lucro_esperado = value(prob.objective)
            
            # ========================================================================
            # ANALISAR TRADE-OFFS ATIVOS
            # ========================================================================
            
            # Sinergias ativas
            sinergias_ativas = []
            for i, sinergia_info in vars_sinergia_qtd.items():
                grupo = sinergia_info['grupo']
                produtos_grupo = sinergia_info['produtos']
                qtd_minima_var = sinergia_info['var']
                qtd_minima = value(qtd_minima_var) or 0
                
                # Verificar se tem produção dos produtos no grupo
                producoes_grupo = []
                for produto in produtos_grupo:
                    if produto in producao_otima and producao_otima[produto] >= grupo['threshold_min']:
                        producoes_grupo.append({
                            'produto': produto,
                            'quantidade': producao_otima[produto]
                        })
                
                if len(producoes_grupo) >= 2 and qtd_minima >= grupo['threshold_min']:
                    sinergias_ativas.append({
                        'produtos': [p['produto'] for p in producoes_grupo],
                        'quantidades': {p['produto']: p['quantidade'] for p in producoes_grupo},
                        'quantidade_com_bonus': round(qtd_minima, 1),
                        'bonus': grupo['bonus'],
                        'descricao': grupo['descricao'],
                        'beneficio': f"+{(grupo['bonus']-1)*100:.1f}% margem em {qtd_minima:.1f} un de cada"
                    })
            
            # Economias de escala removidas - apenas sinergias agora
            economias_ativas = []
            
            # Recursos especializados utilizados
            recursos_especializados_uso = {}
            
            # Chips de Processamento
            if 'chips_processamento' in recursos_disponiveis:
                consumo_chips = sum([
                    producao_otima.get(produto, 0) * produtos_para_otimizacao[produto].get('consumo_chips_processamento', 0)
                    for produto in producao_otima.keys()
                ])
                consumo_chips = arredondar_producao(consumo_chips, 2)
                if consumo_chips > 0:
                    disponivel_chips = arredondar_producao(recursos_disponiveis['chips_processamento'] - consumo_chips, 2)
                    recursos_especializados_uso['chips_processamento'] = {
                        'nome': GameConfig.NOMES_RECURSOS['chips_processamento'],
                        'emoji': GameConfig.EMOJI_RECURSO['chips_processamento'],
                        'consumo': consumo_chips,
                        'capacidade': recursos_disponiveis['chips_processamento'],
                        'utilizacao_percentual': round((consumo_chips / recursos_disponiveis['chips_processamento']) * 100, 1),
                        'disponivel': disponivel_chips
                    }
            
            # Engenheiros Sênior
            if 'engenheiros_senior' in recursos_disponiveis:
                consumo_engenheiros = sum([
                    producao_otima.get(produto, 0) * produtos_para_otimizacao[produto].get('consumo_engenheiros_senior', 0)
                    for produto in producao_otima.keys()
                ])
                consumo_engenheiros = arredondar_producao(consumo_engenheiros, 2)
                if consumo_engenheiros > 0:
                    disponivel_eng = arredondar_producao(recursos_disponiveis['engenheiros_senior'] - consumo_engenheiros, 2)
                    recursos_especializados_uso['engenheiros_senior'] = {
                        'nome': GameConfig.NOMES_RECURSOS['engenheiros_senior'],
                        'emoji': GameConfig.EMOJI_RECURSO['engenheiros_senior'],
                        'consumo': consumo_engenheiros,
                        'capacidade': recursos_disponiveis['engenheiros_senior'],
                        'utilizacao_percentual': round((consumo_engenheiros / recursos_disponiveis['engenheiros_senior']) * 100, 1),
                        'disponivel': disponivel_eng
                    }
            
            # DEBUG: Log da solução ótima
            print("\n" + "="*80)
            print("✅ OTIMIZADOR - Solução Ótima Encontrada (COM TRADE-OFFS):")
            print(f"   💵 Lucro Esperado: R$ {lucro_esperado:,.2f}")
            print(f"   📊 Produção:")
            for produto, qtd in producao_otima.items():
                print(f"      • {produto}: {qtd} unidades")
            
            if sinergias_ativas:
                print(f"   🔗 Sinergias Ativas: {len(sinergias_ativas)}")
                for sin in sinergias_ativas:
                    print(f"      • {sin['descricao']}: {' + '.join(sin['produtos'])} ({sin['beneficio']})")
            
            if recursos_especializados_uso:
                print(f"   � Recursos Especializados:")
                for nome, info in recursos_especializados_uso.items():
                    print(f"      • {info['nome']}: {info['consumo']}/{info['capacidade']} ({info['utilizacao_percentual']}%)")
            
            print(f"   📦 Recursos Básicos:")
            print(f"      • Matéria-prima: {recursos_utilizados['materia_prima']:,.2f}")
            print(f"      • Energia: {recursos_utilizados['energia']:,.2f}")
            print(f"      • Trabalhadores: {recursos_utilizados['trabalhadores']:,.2f}")
            print(f"      • Dinheiro (custos): R$ {recursos_utilizados['dinheiro']:,.2f}")
            print("="*80 + "\n")
            
            # Detalhes adicionais
            detalhes = {
                'receita_bruta': round(receita_total, 2),
                'custo_total': round(custo_total, 2),
                'total_produtos': round(sum(producao_otima.values()), 2),
                'produtos_utilizados': len(producao_otima)
            }
            
            # Trade-offs aplicados
            trade_offs = {
                'sinergias_ativas': sinergias_ativas,
                'recursos_especializados': recursos_especializados_uso,
                'modelo_avancado': True
            }
            
            return {
                'sucesso': True,
                'status': status,
                'producao_otima': producao_otima,
                'lucro_esperado': round(lucro_esperado, 2),
                'recursos_utilizados': {
                    k: round(v, 2) for k, v in recursos_utilizados.items()
                },
                'recursos_restantes': {
                    k: round(v, 2) for k, v in recursos_restantes.items()
                },
                'detalhes': detalhes,
                'trade_offs': trade_offs
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'status': 'ERRO',
                'mensagem': f'Erro durante otimização: {str(e)}'
            }
    
    def _sanitize_name(self, name: str) -> str:
        """Remove caracteres especiais do nome para uso no PuLP"""
        # Remove emojis e caracteres especiais
        sanitized = ''.join(c for c in name if c.isalnum() or c == '_')
        return sanitized or 'produto'
    
    def formatar_resultado_legivel(self, resultado: dict, produtos_utilizados: dict = None) -> str:
        """
        Formata o resultado da otimização de forma legível
        
        Args:
            resultado: Dict retornado por otimizar_producao()
            produtos_utilizados: Produtos utilizados na otimização (opcional)
        
        Returns:
            str: Texto formatado
        """
        if not resultado['sucesso']:
            return f"❌ {resultado.get('mensagem', 'Erro na otimização')}"
        
        # Usar produtos fornecidos ou padrão
        produtos_info = produtos_utilizados if produtos_utilizados else self.produtos
        
        texto = "✅ SOLUÇÃO ÓTIMA ENCONTRADA\n\n"
        texto += "📊 PRODUÇÃO RECOMENDADA:\n"
        
        for produto, quantidade in resultado['producao_otima'].items():
            emoji = produtos_info[produto].get('emoji', '')
            preco = produtos_info[produto]['preco_venda']
            receita = quantidade * preco
            texto += f"  {emoji} {produto}: {quantidade} unidades (R$ {receita:,.2f})\n"
        
        texto += f"\n💰 LUCRO ESPERADO: R$ {resultado['lucro_esperado']:,.2f}\n"
        texto += f"📦 TOTAL DE PRODUTOS: {resultado['detalhes']['total_produtos']} unidades\n"
        texto += f"💵 RECEITA BRUTA: R$ {resultado['detalhes']['receita_bruta']:,.2f}\n"
        texto += f"💸 CUSTO TOTAL: R$ {resultado['detalhes']['custo_total']:,.2f}\n"
        
        # Trade-offs ativos
        if resultado.get('trade_offs'):
            trade_offs = resultado['trade_offs']
            
            if trade_offs.get('sinergias_ativas'):
                texto += "\n🔗 SINERGIAS ATIVAS:\n"
                for sinergia in trade_offs['sinergias_ativas']:
                    texto += f"  • {sinergia['descricao']}: {' + '.join(sinergia['produtos'])} ({sinergia['beneficio']})\n"
            
            if trade_offs.get('recursos_especializados'):
                texto += "\n� RECURSOS ESPECIALIZADOS:\n"
                for nome, info in trade_offs['recursos_especializados'].items():
                    texto += f"  • {info['nome']}: {info['consumo']}/{info['capacidade']} ({info['utilizacao_percentual']}% utilizado)\n"
        
        texto += "\n�📈 RECURSOS BÁSICOS UTILIZADOS:\n"
        nomes_recursos = {
            'materia_prima': '📦 Matéria-prima',
            'energia': '⚡ Energia',
            'trabalhadores': '👥 Trabalhadores',
            'dinheiro': '💰 Dinheiro'
        }
        for recurso, quantidade in resultado['recursos_utilizados'].items():
            nome = nomes_recursos.get(recurso, recurso)
            restante = resultado['recursos_restantes'][recurso]
            texto += f"  {nome}: {quantidade:,.2f} (restante: {restante:,.2f})\n"
        
        return texto
