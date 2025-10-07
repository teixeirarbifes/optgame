# -*- coding: utf-8 -*-
"""
Otimizador de Produção usando PuLP
Calcula a solução ótima para maximizar lucro dadas as restrições de recursos
"""

try:
    from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus, value
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False
    print("AVISO: PuLP não instalado. Funcionalidade de otimização não disponível.")
    print("Instale com: pip install pulp")

from config.constants import GameConfig


class ProductionOptimizer:
    """Otimizador de produção para maximizar lucro"""
    
    def __init__(self):
        self.produtos = GameConfig.PRODUTOS
        self.custos_recursos = GameConfig.CUSTOS_UNITARIOS_RECURSOS
    
    def otimizar_producao(self, recursos_disponiveis: dict) -> dict:
        """
        Calcula a produção ótima para maximizar o lucro
        
        Args:
            recursos_disponiveis: Dict com recursos disponíveis da empresa
                {
                    'dinheiro': float,
                    'materia_prima': float,
                    'energia': float,
                    'trabalhadores': float
                }
        
        Returns:
            dict: Resultado da otimização
                {
                    'sucesso': bool,
                    'status': str,
                    'producao_otima': {produto: quantidade, ...},
                    'lucro_esperado': float,
                    'recursos_utilizados': {recurso: quantidade, ...},
                    'recursos_restantes': {recurso: quantidade, ...},
                    'detalhes': dict
                }
        """
        if not PULP_AVAILABLE:
            return {
                'sucesso': False,
                'status': 'ERRO',
                'mensagem': 'PuLP não está instalado. Execute: pip install pulp'
            }
        
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
            prob = LpProblem("Maximizar_Lucro_Producao", LpMaximize)
            
            # Variáveis de decisão: quantidade a produzir de cada produto
            produtos_vars = {}
            for produto_nome in self.produtos.keys():
                # Variável não-negativa, inteira
                var_nome = self._sanitize_name(produto_nome)
                produtos_vars[produto_nome] = LpVariable(
                    var_nome, 
                    lowBound=0, 
                    cat='Integer'
                )
            
            # Função Objetivo: Maximizar lucro líquido
            # Lucro = Receita - Custos dos recursos consumidos
            receita = lpSum([
                produtos_vars[prod] * self.produtos[prod]['preco_venda']
                for prod in self.produtos.keys()
            ])
            
            # Custos dos recursos consumidos
            custo_materia = lpSum([
                produtos_vars[prod] * self.produtos[prod]['consumo_materia']
                * self.custos_recursos['materia_prima']
                for prod in self.produtos.keys()
            ])
            
            custo_energia = lpSum([
                produtos_vars[prod] * self.produtos[prod]['consumo_energia']
                * self.custos_recursos['energia']
                for prod in self.produtos.keys()
            ])
            
            custo_trabalho = lpSum([
                produtos_vars[prod] * self.produtos[prod]['consumo_trabalhadores']
                * self.custos_recursos['trabalhadores']
                for prod in self.produtos.keys()
            ])
            
            # Lucro líquido
            lucro_liquido = receita - custo_materia - custo_energia - custo_trabalho
            prob += lucro_liquido, "Lucro_Liquido"
            
            # Restrições de recursos
            
            # 1. Matéria-prima disponível
            prob += (
                lpSum([
                    produtos_vars[prod] * self.produtos[prod]['consumo_materia']
                    for prod in self.produtos.keys()
                ]) <= recursos_disponiveis['materia_prima'],
                "Restricao_Materia_Prima"
            )
            
            # 2. Energia disponível
            prob += (
                lpSum([
                    produtos_vars[prod] * self.produtos[prod]['consumo_energia']
                    for prod in self.produtos.keys()
                ]) <= recursos_disponiveis['energia'],
                "Restricao_Energia"
            )
            
            # 3. Trabalhadores disponíveis
            prob += (
                lpSum([
                    produtos_vars[prod] * self.produtos[prod]['consumo_trabalhadores']
                    for prod in self.produtos.keys()
                ]) <= recursos_disponiveis['trabalhadores'],
                "Restricao_Trabalhadores"
            )
            
            # 4. Restrição de dinheiro (custos totais não podem exceder dinheiro disponível)
            custos_totais = custo_materia + custo_energia + custo_trabalho
            prob += (
                custos_totais <= recursos_disponiveis['dinheiro'],
                "Restricao_Dinheiro"
            )
            
            # Resolver o problema
            prob.solve()
            
            # Extrair resultados
            status = LpStatus[prob.status]
            
            if status != 'Optimal':
                return {
                    'sucesso': False,
                    'status': status,
                    'mensagem': f'Otimização não encontrou solução ótima. Status: {status}'
                }
            
            # Solução ótima
            producao_otima = {}
            for produto, var in produtos_vars.items():
                quantidade = int(value(var))
                if quantidade > 0:
                    producao_otima[produto] = quantidade
            
            # Calcular recursos utilizados
            recursos_utilizados = {
                'materia_prima': 0,
                'energia': 0,
                'trabalhadores': 0,
                'dinheiro': 0
            }
            
            for produto, quantidade in producao_otima.items():
                recursos_utilizados['materia_prima'] += (
                    quantidade * self.produtos[produto]['consumo_materia']
                )
                recursos_utilizados['energia'] += (
                    quantidade * self.produtos[produto]['consumo_energia']
                )
                recursos_utilizados['trabalhadores'] += (
                    quantidade * self.produtos[produto]['consumo_trabalhadores']
                )
            
            # Custos em dinheiro
            recursos_utilizados['dinheiro'] = (
                recursos_utilizados['materia_prima'] * self.custos_recursos['materia_prima'] +
                recursos_utilizados['energia'] * self.custos_recursos['energia'] +
                recursos_utilizados['trabalhadores'] * self.custos_recursos['trabalhadores']
            )
            
            # Recursos restantes
            recursos_restantes = {
                recurso: recursos_disponiveis[recurso] - recursos_utilizados[recurso]
                for recurso in recursos_utilizados.keys()
            }
            
            # Lucro esperado
            lucro_esperado = value(prob.objective)
            
            # DEBUG: Log da solução ótima
            print("\n" + "="*80)
            print("✅ OTIMIZADOR - Solução Ótima Encontrada:")
            print(f"   💵 Lucro Esperado: R$ {lucro_esperado:,.2f}")
            print(f"   📊 Produção:")
            for produto, qtd in producao_otima.items():
                print(f"      • {produto}: {qtd} unidades")
            print(f"   📦 Recursos Utilizados:")
            print(f"      • Matéria-prima: {recursos_utilizados['materia_prima']:,.2f}")
            print(f"      • Energia: {recursos_utilizados['energia']:,.2f}")
            print(f"      • Trabalhadores: {recursos_utilizados['trabalhadores']:,.2f}")
            print(f"      • Dinheiro (custos): R$ {recursos_utilizados['dinheiro']:,.2f}")
            print("="*80 + "\n")
            
            # Detalhes adicionais
            detalhes = {
                'receita_bruta': sum([
                    producao_otima.get(prod, 0) * self.produtos[prod]['preco_venda']
                    for prod in self.produtos.keys()
                ]),
                'custo_total': recursos_utilizados['dinheiro'],
                'total_produtos': sum(producao_otima.values()),
                'produtos_utilizados': len(producao_otima)
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
                'detalhes': detalhes
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
    
    def formatar_resultado_legivel(self, resultado: dict) -> str:
        """
        Formata o resultado da otimização de forma legível
        
        Args:
            resultado: Dict retornado por otimizar_producao()
        
        Returns:
            str: Texto formatado
        """
        if not resultado['sucesso']:
            return f"❌ {resultado.get('mensagem', 'Erro na otimização')}"
        
        texto = "✅ SOLUÇÃO ÓTIMA ENCONTRADA\n\n"
        texto += "📊 PRODUÇÃO RECOMENDADA:\n"
        
        for produto, quantidade in resultado['producao_otima'].items():
            emoji = self.produtos[produto].get('emoji', '')
            preco = self.produtos[produto]['preco_venda']
            receita = quantidade * preco
            texto += f"  {emoji} {produto}: {quantidade} unidades (R$ {receita:,.2f})\n"
        
        texto += f"\n💰 LUCRO ESPERADO: R$ {resultado['lucro_esperado']:,.2f}\n"
        texto += f"📦 TOTAL DE PRODUTOS: {resultado['detalhes']['total_produtos']} unidades\n"
        texto += f"💵 RECEITA BRUTA: R$ {resultado['detalhes']['receita_bruta']:,.2f}\n"
        texto += f"💸 CUSTO TOTAL: R$ {resultado['detalhes']['custo_total']:,.2f}\n"
        
        texto += "\n📈 RECURSOS UTILIZADOS:\n"
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
