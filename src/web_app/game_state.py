# -*- coding: utf-8 -*-
"""Gerenciamento do estado do jogo para a versão web"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from config.constants import GameConfig

class GameState:
    """Gerencia o estado global do jogo"""
    
    def __init__(self):
        self.admin_password = "admin1064*"  # Senha admin - definir ANTES de reset
        self.session_version = 1  # Incrementa quando sessões devem ser invalidadas
        self.auto_save_enabled = False  # Auto-save após cada iteração
        self.calcular_otimo_ao_criar = False  # Calcular solução ótima ao criar empresa (padrão: False)
        self.modelo_default = None  # Modelo default para novas empresas (otimizador inverso)
        self.reset_game()
        
    def reset_game(self):
        """Resetar o jogo para estado inicial (apaga tudo, incluindo empresas)"""
        self.iteracao_atual = 1
        self.max_iteracoes = GameConfig.MAX_ITERACOES
        self.empresas: Dict[str, dict] = {}
        self.iteracao_aberta = True  # Alunos podem enviar decisões
        self.historico_global: List[dict] = []
        self.produtos = GameConfig.get_produtos_inicializados()
        # Não resetar a senha admin nem modelo_default
    
    def resetar_progresso(self):
        """Resetar apenas o progresso do jogo (mantém empresas cadastradas)
        
        Zera:
        - Iteração atual volta para 1
        - Históricos de todas empresas
        - Lucros
        - Decisões
        - Recursos voltam ao estado base
        
        Mantém:
        - Empresas cadastradas
        - Senhas
        - Nomes e equipes
        """
        self.iteracao_atual = 1
        self.iteracao_aberta = True
        self.historico_global = []
        
        # Resetar progresso de cada empresa
        for empresa in self.empresas.values():
            empresa['recursos_disponiveis'] = empresa['recursos_base'].copy()
            empresa['decisao_atual'] = {}
            empresa['decisao_confirmada'] = False
            empresa['historico'] = []
            empresa['historico_decisoes'] = []
            empresa['historico_recursos'] = {
                'turnos': [],
                'dinheiro': [],
                'materia_prima': [],
                'energia': [],
                'trabalhadores': [],
                'chips_processamento': [],
                'engenheiros_senior': []
            }
            empresa['lucro_total'] = 0
            empresa['lucro_ultimo_turno'] = 0
            empresa['iteracao_criacao'] = 1  # Resetar para iteração 1
            
            # Resetar histórico de lucros se existir
            if 'historico_lucros' in empresa:
                empresa['historico_lucros'] = {'turnos': [], 'valores': []}
        
        # Invalidar sessões para forçar novo login
        self.invalidar_todas_sessoes()
        
        print(f"Progresso resetado! {len(self.empresas)} empresa(s) mantida(s).")
        
    def adicionar_empresa(self, nome: str, equipe: str, senha: str) -> bool:
        """Adicionar nova empresa ao jogo"""
        if nome in self.empresas:
            return False
        
        # Determinar recursos base (usar modelo default se disponível)
        if self.modelo_default and self.modelo_default.get('ativo', False):
            recursos_base = self.modelo_default['recursos_base'].copy()
            decisao_inicial = self.modelo_default.get('producao_sugerida', {}).copy()
            custos_customizados = self.modelo_default.get('custos_produtos_otimizados')
        else:
            recursos_base = GameConfig.RECURSOS_BASE.copy()
            decisao_inicial = {}
            custos_customizados = None
            
        self.empresas[nome] = {
            'nome': nome,
            'equipe': equipe,
            'senha': senha,
            'recursos_base': recursos_base,  # Recursos iniciais (não mudam)
            'recursos_disponiveis': recursos_base.copy(),  # Recursos disponíveis (sempre resetam ao base)
            'decisao_atual': decisao_inicial,  # Decisão pendente da iteração atual (pode ter sugestão do modelo)
            'decisao_confirmada': False,  # Se já confirmou a decisão
            'historico': [],  # Histórico completo com violações
            'historico_decisoes': [],
            'historico_recursos': {
                'turnos': [],
                'dinheiro': [],
                'materia_prima': [],
                'energia': [],
                'trabalhadores': [],
                'chips_processamento': [],
                'engenheiros_senior': []
            },
            'lucro_total': 0,
            'lucro_ultimo_turno': 0,
            'iteracao_criacao': self.iteracao_atual,  # Iteração em que foi criada
            'criada_em': datetime.now().isoformat(),
            'solucao_otima': None,  # Solução ótima calculada (guardada, não mostrada)
            'lucro_otimo': 0,  # Lucro máximo possível
            'gap_percentual': None,  # GAP% entre lucro atual e ótimo
            'modelo_aplicado': self.modelo_default if self.modelo_default and self.modelo_default.get('ativo') else None,  # Modelo usado na criação
            'produtos_customizados': custos_customizados.copy() if custos_customizados else None  # Custos de produtos customizados
        }
        
        # Calcular solução ótima automaticamente se flag ativada
        if self.calcular_otimo_ao_criar:
            self._calcular_e_guardar_otimo(nome)
        
        return True
        
    def autenticar_empresa(self, nome: str, senha: str) -> bool:
        """Verificar credenciais da empresa"""
        empresa = self.empresas.get(nome)
        if not empresa:
            return False
        return empresa['senha'] == senha
        
    def registrar_decisao(self, nome_empresa: str, decisoes: Dict[str, float], force: bool = False) -> bool:
        """Registrar decisão de produção da empresa
        
        Args:
            nome_empresa: Nome da empresa
            decisoes: Dicionário com decisões de produção (valores podem ser decimais)
            force: Se True, ignora verificação de iteracao_aberta (para admin aplicar solução ótima)
        """
        if not force and not self.iteracao_aberta:
            return False
            
        empresa = self.empresas.get(nome_empresa)
        if not empresa:
            return False
            
        # Validar decisões
        if not self._validar_decisoes(empresa, decisoes):
            return False
            
        empresa['decisao_atual'] = decisoes
        empresa['decisao_confirmada'] = True
        return True
        
    def _validar_decisoes(self, empresa: dict, decisoes: Dict[str, float]) -> bool:
        """Validar se as decisões são viáveis com recursos disponíveis"""
        from mecanicas.mechanics import GameMechanics
        
        # Usar produtos customizados se disponíveis para esta empresa
        produtos_para_calculo = self.produtos.copy()
        if empresa.get('produtos_customizados'):
            # Sobrescrever com custos customizados
            for produto, custos_custom in empresa['produtos_customizados'].items():
                if produto in produtos_para_calculo:
                    produtos_para_calculo[produto].update(custos_custom)
        
        # Calcular consumo com produtos (possivelmente customizados)
        consumo = GameMechanics.calcular_consumo_recursos(produtos_para_calculo, decisoes)
        recursos = empresa['recursos_disponiveis']
        
        # Verificar se tem recursos suficientes
        for recurso, necessario in consumo.items():
            disponivel = recursos.get(recurso, 0)
            if necessario > disponivel:
                return False
                
        return True
    
    def _calcular_trade_offs_decisao(self, decisoes: Dict[str, float], produtos: Dict) -> Dict:
        """Calcular trade-offs ativados por uma decisão (simplificado para dashboard)"""
        trade_offs = {
            'sinergias_ativas': [],
            'recursos_especializados': {}
        }
        
        # Definição de sinergias (mesmas do otimizador)
        grupos_sinergia = [
            {
                'produtos': ['Smartphone', 'Smartwatch'],
                'bonus': 1.15,
                'threshold_min': 10,
                'descricao': 'Ecossistema Móvel'
            },
            {
                'produtos': ['Desktop', 'Laptop'],
                'bonus': 1.10,
                'threshold_min': 10,
                'descricao': 'Linha de Computação'
            },
            {
                'produtos': ['Camera', 'Smartphone'],
                'bonus': 1.12,
                'threshold_min': 5,
                'descricao': 'Fotografia Integrada'
            }
        ]
        
        # Verificar sinergias ativas
        for grupo in grupos_sinergia:
            produtos_do_grupo = [p for p in grupo['produtos'] if decisoes.get(p, 0) >= grupo['threshold_min']]
            if len(produtos_do_grupo) >= 2:
                trade_offs['sinergias_ativas'].append({
                    'produtos': produtos_do_grupo,
                    'bonus': grupo['bonus'],
                    'descricao': grupo['descricao'],
                    'beneficio': f"+{(grupo['bonus']-1)*100:.1f}% margem"
                })
        
        # Calcular uso de recursos especializados (agora vem direto do GameConfig)
        # Chips de Processamento
        consumo_chips = sum([
            decisoes.get(produto, 0) * produtos.get(produto, {}).get('consumo_chips_processamento', 0)
            for produto in decisoes.keys()
        ])
        if consumo_chips > 0:
            trade_offs['recursos_especializados']['chips_processamento'] = {
                'nome': GameConfig.NOMES_RECURSOS['chips_processamento'],
                'emoji': GameConfig.EMOJI_RECURSO['chips_processamento'],
                'consumo': round(consumo_chips, 2),
                'capacidade': GameConfig.RECURSOS_BASE['chips_processamento'],
                'utilizacao_percentual': round((consumo_chips / GameConfig.RECURSOS_BASE['chips_processamento']) * 100, 1),
                'disponivel': round(GameConfig.RECURSOS_BASE['chips_processamento'] - consumo_chips, 2)
            }
        
        # Engenheiros Sênior
        consumo_engenheiros = sum([
            decisoes.get(produto, 0) * produtos.get(produto, {}).get('consumo_engenheiros_senior', 0)
            for produto in decisoes.keys()
        ])
        if consumo_engenheiros > 0:
            trade_offs['recursos_especializados']['engenheiros_senior'] = {
                'nome': GameConfig.NOMES_RECURSOS['engenheiros_senior'],
                'emoji': GameConfig.EMOJI_RECURSO['engenheiros_senior'],
                'consumo': round(consumo_engenheiros, 2),
                'capacidade': GameConfig.RECURSOS_BASE['engenheiros_senior'],
                'utilizacao_percentual': round((consumo_engenheiros / GameConfig.RECURSOS_BASE['engenheiros_senior']) * 100, 1),
                'disponivel': round(GameConfig.RECURSOS_BASE['engenheiros_senior'] - consumo_engenheiros, 2)
            }
        
        return trade_offs
    
    def _calcular_bonus_sinergias(self, decisoes: Dict[str, float], produtos: Dict) -> float:
        """Calcular bônus monetário das sinergias ativas"""
        bonus_total = 0.0
        
        # Definição de sinergias (mesmas do otimizador)
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
                        
                        # Calcular custo unitário (mesma lógica do otimizador)
                        custo_unitario = (
                            dados_produto.get('consumo_materia', 0) * GameConfig.CUSTOS_UNITARIOS_RECURSOS['materia_prima'] +
                            dados_produto.get('consumo_energia', 0) * GameConfig.CUSTOS_UNITARIOS_RECURSOS['energia'] +
                            dados_produto.get('consumo_trabalhadores', 0) * GameConfig.CUSTOS_UNITARIOS_RECURSOS['trabalhadores']
                        )
                        
                        margem_base = preco - custo_unitario
                        bonus_margem = qtd_minima * margem_base * (grupo['bonus'] - 1)
                        bonus_total += bonus_margem
        
        return bonus_total
    
    def processar_turno(self) -> Dict[str, any]:
        """Processar turno (chamado pelo admin)"""
        if not self.iteracao_aberta:
            return {'sucesso': False, 'mensagem': 'Iteração já processada'}
            
        from mecanicas.mechanics import GameMechanics
        
        resultados = []
        
        for nome, empresa in self.empresas.items():
            # Pular empresas criadas após a iteração atual
            iteracao_criacao = empresa.get('iteracao_criacao', 0)
            if iteracao_criacao > self.iteracao_atual:
                resultados.append({
                    'empresa': nome,
                    'status': 'aguardando',
                    'mensagem': f'Empresa entra no turno {iteracao_criacao}'
                })
                continue
            
            # Se não confirmou decisão, usar última decisão do histórico
            if not empresa['decisao_confirmada']:
                historico = empresa.get('historico', [])
                if historico:
                    # Copiar última decisão
                    ultima_decisao = historico[-1].get('decisao', {})
                    empresa['decisao_atual'] = ultima_decisao.copy()
                    empresa['decisao_confirmada'] = True
                    print(f"[AUTO-REPEAT] Empresa {nome} usando última decisão: {ultima_decisao}")
                else:
                    # Primeira iteração, usar decisão vazia (zeros)
                    empresa['decisao_atual'] = {}
                    empresa['decisao_confirmada'] = True
                    print(f"[AUTO-REPEAT] Empresa {nome} primeira iteração, usando zeros")
            
            # Verificar se ainda não confirmou (caso não tenha histórico nem decisão)
            if not empresa['decisao_confirmada']:
                resultados.append({
                    'empresa': nome,
                    'status': 'pendente',
                    'mensagem': 'Aguardando decisão'
                })
                continue
                
            decisoes = empresa['decisao_atual']
            
            # Usar produtos customizados se disponíveis para esta empresa
            produtos_para_calculo = self.produtos.copy()
            if empresa.get('produtos_customizados'):
                # Sobrescrever com custos customizados
                for produto, custos_custom in empresa['produtos_customizados'].items():
                    if produto in produtos_para_calculo:
                        produtos_para_calculo[produto].update(custos_custom)
            
            # Calcular consumo de recursos e métricas
            consumo = GameMechanics.calcular_consumo_recursos(produtos_para_calculo, decisoes)
            metricas = GameMechanics.calcular_metricas_plano(produtos_para_calculo, decisoes)
            
            receita_total = metricas['receita']
            custo_total = metricas['custo']
            lucro_turno = metricas['lucro']
            
            # APLICAR BÔNUS DE SINERGIAS AO LUCRO
            bonus_sinergias_total = self._calcular_bonus_sinergias(decisoes, produtos_para_calculo)
            lucro_turno += bonus_sinergias_total
            
            # Verificar violações de recursos FÍSICOS (não incluir dinheiro ainda)
            recursos_disponiveis = empresa['recursos_disponiveis']
            violacoes = []
            
            # DEBUG: Log da validação
            print(f"\n=== VALIDANDO EMPRESA: {nome} ===")
            print(f"Decisao: {decisoes}")
            print(f"Consumo calculado: {consumo}")
            print(f"Recursos disponiveis: {recursos_disponiveis}")
            
            # Verificar recursos físicos (incluindo recursos especializados)
            # Usar tolerância para evitar erros de arredondamento (ex: 600.0000001 > 600)
            EPSILON = 1e-6
            recursos_fisicos = ['materia_prima', 'energia', 'trabalhadores', 'chips_processamento', 'engenheiros_senior']
            for recurso in recursos_fisicos:
                necessario = consumo.get(recurso, 0)
                disponivel = recursos_disponiveis.get(recurso, 0)
                print(f"  {recurso}: necessario={necessario}, disponivel={disponivel}")
                # Só considera violação se exceder a capacidade por mais que EPSILON
                if necessario > disponivel + EPSILON:
                    print(f"    VIOLACAO! Deficit: {necessario - disponivel}")
                    violacoes.append({
                        'recurso': recurso,
                        'necessario': necessario,
                        'disponivel': disponivel,
                        'deficit': necessario - disponivel
                    })
            
            # Verificar dinheiro (receita - custo_monetario + saldo_atual)
            saldo_apos_operacao = recursos_disponiveis.get('dinheiro', 0) + receita_total - consumo.get('dinheiro', 0)
            if saldo_apos_operacao < 0:
                violacoes.append({
                    'recurso': 'dinheiro',
                    'necessario': consumo.get('dinheiro', 0),
                    'disponivel': recursos_disponiveis.get('dinheiro', 0) + receita_total,
                    'deficit': abs(saldo_apos_operacao)
                })
            
            # Se há violações, não executa e lucro = 0
            trade_offs_info = None
            if violacoes:
                lucro_turno = 0
                receita_total = 0
                custo_total = 0
                detalhes = [{
                    'status': 'violação',
                    'mensagem': 'Decisão não executada por recursos insuficientes'
                }]
                # Recursos permanecem nos valores BASE (não muda nada)
                empresa['recursos_disponiveis'] = empresa['recursos_base'].copy()
            else:
                # EXECUÇÃO BEM-SUCEDIDA
                # Calcula os recursos APÓS a execução (para mostrar no histórico)
                recursos_apos = empresa['recursos_base'].copy()
                recursos_apos['materia_prima'] -= consumo.get('materia_prima', 0)
                recursos_apos['energia'] -= consumo.get('energia', 0)
                recursos_apos['trabalhadores'] -= consumo.get('trabalhadores', 0)
                recursos_apos['dinheiro'] += receita_total
                recursos_apos['dinheiro'] -= consumo.get('dinheiro', 0)
                
                # Atualiza recursos disponíveis (mas na próxima iteração voltam ao base)
                empresa['recursos_disponiveis'] = recursos_apos.copy()
                
                detalhes = []
                for produto, quantidade in decisoes.items():
                    if quantidade > 0:
                        dados_produto = produtos_para_calculo.get(produto, {})
                        receita_prod = quantidade * dados_produto.get('preco_venda', 0)
                        custo_prod = quantidade * dados_produto.get('custo_dinheiro', 0)
                        lucro_prod = receita_prod - custo_prod
                        detalhes.append({
                            'produto': produto,
                            'quantidade': quantidade,
                            'receita': receita_prod,
                            'custo': custo_prod,
                            'lucro': lucro_prod
                        })
                
                # CALCULAR TRADE-OFFS para mostrar no dashboard
                trade_offs_info = self._calcular_trade_offs_decisao(decisoes, produtos_para_calculo)
            
            # Adicionar ao histórico simplificado para o dashboard
            historico_entry = {
                'turno': self.iteracao_atual,
                'decisao': decisoes.copy(),
                'receita': receita_total,
                'custo': custo_total,
                'lucro': lucro_turno,
                'consumo': consumo.copy(),
                'violacoes': violacoes if violacoes else None,
                'recursos_apos': empresa['recursos_disponiveis'].copy()
            }
            
            # Adicionar trade-offs ao histórico se houver
            if trade_offs_info:
                historico_entry['trade_offs'] = trade_offs_info
            
            empresa.setdefault('historico', []).append(historico_entry)
            
            # Registrar histórico de recursos para gráficos
            empresa.setdefault('historico_recursos', {
                'turnos': [],
                'dinheiro': [],
                'materia_prima': [],
                'energia': [],
                'trabalhadores': [],
                'chips_processamento': [],
                'engenheiros_senior': []
            })
            empresa['historico_recursos']['turnos'].append(self.iteracao_atual)
            empresa['historico_recursos']['dinheiro'].append(empresa['recursos_disponiveis']['dinheiro'])
            empresa['historico_recursos']['materia_prima'].append(empresa['recursos_disponiveis']['materia_prima'])
            empresa['historico_recursos']['energia'].append(empresa['recursos_disponiveis']['energia'])
            empresa['historico_recursos']['trabalhadores'].append(empresa['recursos_disponiveis']['trabalhadores'])
            empresa['historico_recursos']['chips_processamento'].append(empresa['recursos_disponiveis']['chips_processamento'])
            empresa['historico_recursos']['engenheiros_senior'].append(empresa['recursos_disponiveis']['engenheiros_senior'])
            
            # Lucro do último turno (NÃO acumulado)
            empresa['lucro_ultimo_turno'] = lucro_turno
            
            # Acumular lucro total (soma de todos os turnos)
            empresa['lucro_total'] += lucro_turno
            
            # Registrar histórico de lucros para gráfico de evolução (lucro POR ITERAÇÃO, não acumulado)
            empresa.setdefault('historico_lucros', {'turnos': [], 'valores': []})
            empresa['historico_lucros']['turnos'].append(self.iteracao_atual)
            empresa['historico_lucros']['valores'].append(lucro_turno)  # LUCRO DA ITERAÇÃO, não total acumulado
            
            print(f"  Lucro deste turno: R$ {lucro_turno:.2f}")
            print(f"  Lucro acumulado: R$ {empresa['lucro_total']:.2f}")
            print(f"  Receita: R$ {receita_total:.2f}")
            print(f"  Custo: R$ {custo_total:.2f}")
            print(f"  Violacoes: {len(violacoes) if violacoes else 0}")
            
            # Limpa decisão atual
            empresa['decisao_confirmada'] = False
            empresa['decisao_atual'] = {}
            
            resultados.append({
                'empresa': nome,
                'status': 'processado',
                'lucro': lucro_turno,
                'detalhes': detalhes
            })
        
        # Avançar turno
        self.iteracao_atual += 1
        self.iteracao_aberta = False
        
        print(f"\n=== TURNO PROCESSADO ===")
        print(f"Iteracao atual: {self.iteracao_atual}")
        print(f"Iteracao aberta: {self.iteracao_aberta}")
        print(f"Total de empresas processadas: {len(resultados)}")
        
        self.historico_global.append({
            'turno': self.iteracao_atual - 1,
            'timestamp': datetime.now().isoformat(),
            'resultados': resultados
        })
        
        # Recalcular GAP% para todas as empresas que já tem solução ótima calculada
        print("\n=== ATUALIZANDO GAP% ===")
        for nome_empresa, empresa in self.empresas.items():
            if empresa.get('lucro_otimo', 0) > 0:
                lucro_atual = empresa.get('lucro_ultimo_turno', 0)
                lucro_otimo = empresa['lucro_otimo']
                
                if lucro_otimo > 0:
                    gap = ((lucro_otimo - lucro_atual) / lucro_otimo) * 100
                    empresa['gap_percentual'] = max(0, gap)
                    print(f"  {nome_empresa}: GAP atualizado para {empresa['gap_percentual']:.1f}%")
        
        # Auto-save se habilitado (sempre no mesmo arquivo)
        if self.auto_save_enabled and hasattr(self, 'ultimo_arquivo_salvo'):
            try:
                sucesso, mensagem, _ = self.salvar_estado_arquivo(self.ultimo_arquivo_salvo)
                if sucesso:
                    print(f"Auto-save realizado: {mensagem}")
            except Exception as e:
                print(f"Erro no auto-save: {e}")
        
        return {
            'sucesso': True,
            'turno_processado': self.iteracao_atual - 1,
            'proximo_turno': self.iteracao_atual,
            'resultados': resultados,
            'jogo_finalizado': self.iteracao_atual > self.max_iteracoes
        }
        
    def abrir_proxima_iteracao(self):
        """Abrir próxima iteração para envio de decisões"""
        self.iteracao_aberta = True
        
        # RESETAR recursos para valores base (cada iteração é uma nova tentativa independente)
        for empresa in self.empresas.values():
            empresa['decisao_confirmada'] = False
            
            # IMPORTANTE: Recursos voltam aos valores BASE
            # Cada iteração é uma nova tentativa de plano, não acumula consumo!
            empresa['recursos_disponiveis'] = empresa['recursos_base'].copy()
            
            # Se tem histórico, copiar última decisão
            if empresa.get('historico') and len(empresa['historico']) > 0:
                ultima_decisao = empresa['historico'][-1].get('decisao', {})
                empresa['decisao_atual'] = ultima_decisao.copy()
            else:
                # Primeira iteração - zerar tudo
                empresa['decisao_atual'] = {produto: 0 for produto in self.produtos.keys()}
        
    def get_ranking(self) -> List[dict]:
        """Obter ranking de empresas por lucro da ÚLTIMA ITERAÇÃO (não acumulado)"""
        ranking = []
        for nome, empresa in self.empresas.items():
            # Pegar o lucro da última iteração (mais recente)
            lucro_ultima_iteracao = empresa.get('lucro_ultimo_turno', 0)
            
            ranking.append({
                'nome': nome,
                'equipe': empresa['equipe'],
                'lucro_ultimo_turno': lucro_ultima_iteracao,  # Lucro da última iteração apenas
                'gap_percentual': empresa.get('gap_percentual'),  # GAP%
                'recursos': empresa['recursos_disponiveis']
            })
        
        # Ordenar pelo lucro da ÚLTIMA ITERAÇÃO (melhor desempenho atual)
        ranking.sort(key=lambda x: x['lucro_ultimo_turno'], reverse=True)
        return ranking
        
    def get_estatisticas_gerais(self) -> dict:
        """Obter estatísticas gerais do jogo"""
        total_empresas = len(self.empresas)
        empresas_confirmadas = sum(1 for e in self.empresas.values() if e['decisao_confirmada'])
        
        lucros = [e['lucro_total'] for e in self.empresas.values()]
        media_lucro = sum(lucros) / len(lucros) if lucros else 0
        
        return {
            'total_empresas': total_empresas,
            'empresas_confirmadas': empresas_confirmadas,
            'empresas_pendentes': total_empresas - empresas_confirmadas,
            'iteracao_atual': self.iteracao_atual,
            'max_iteracoes': self.max_iteracoes,
            'iteracao_aberta': self.iteracao_aberta,
            'media_lucro': media_lucro,
            'progresso': (self.iteracao_atual / self.max_iteracoes) * 100
        }
        
    def salvar_estado(self, filepath: str):
        """Salvar estado do jogo em arquivo JSON"""
        estado = {
            'iteracao_atual': self.iteracao_atual,
            'max_iteracoes': self.max_iteracoes,
            'empresas': self.empresas,
            'iteracao_aberta': self.iteracao_aberta,
            'historico_global': self.historico_global,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)
            
    def obter_estado(self) -> dict:
        """Obter estado atual do jogo como dicionário
        
        Returns:
            dict: Estado completo do jogo
        """
        return {
            'iteracao_atual': self.iteracao_atual,
            'max_iteracoes': self.max_iteracoes,
            'empresas': self.empresas,
            'iteracao_aberta': self.iteracao_aberta,
            'historico_global': self.historico_global,
            'produtos': self.produtos,
            'auto_save_enabled': self.auto_save_enabled
        }
    
    def carregar_estado(self, estado: dict) -> bool:
        """Carregar estado do jogo de dicionário
        
        Args:
            estado: Dicionário com o estado do jogo
            
        Returns:
            bool: True se carregou com sucesso
        """
        try:
            self.iteracao_atual = estado['iteracao_atual']
            self.max_iteracoes = estado['max_iteracoes']
            self.empresas = estado['empresas']
            self.iteracao_aberta = estado['iteracao_aberta']
            self.historico_global = estado.get('historico_global', [])
            self.produtos = estado.get('produtos', GameConfig.get_produtos_inicializados())
            self.auto_save_enabled = estado.get('auto_save_enabled', False)
            
            # Backward compatibility: adicionar campos novos para saves antigos
            for empresa in self.empresas.values():
                if 'iteracao_criacao' not in empresa:
                    empresa['iteracao_criacao'] = 1  # Assume que foi criada no início
                if 'lucro_ultimo_turno' not in empresa:
                    empresa['lucro_ultimo_turno'] = 0
                if 'solucao_otima' not in empresa:
                    empresa['solucao_otima'] = None
                if 'lucro_otimo' not in empresa:
                    empresa['lucro_otimo'] = 0
                if 'gap_percentual' not in empresa:
                    empresa['gap_percentual'] = None
            
            return True
        except Exception as e:
            print(f"Erro ao carregar estado: {e}")
            return False
    
    def invalidar_todas_sessoes(self):
        """Invalida todas as sessões de empresas (força novo login)"""
        self.session_version += 1
        print(f"Sessões invalidadas. Nova versão: {self.session_version}")
    
    def set_auto_save(self, enabled: bool) -> bool:
        """Ativar ou desativar auto-save
        
        Args:
            enabled: True para ativar, False para desativar
            
        Returns:
            bool: Novo estado do auto-save
        """
        self.auto_save_enabled = enabled
        status = "ativado" if enabled else "desativado"
        print(f"Auto-save {status}")
        return self.auto_save_enabled
    
    def get_auto_save_status(self) -> bool:
        """Obter status atual do auto-save
        
        Returns:
            bool: True se auto-save está ativado
        """
        return self.auto_save_enabled
    
    def calcular_solucao_otima(self, nome_empresa: str) -> dict:
        """Calcular a solução ótima de produção para uma empresa
        
        Args:
            nome_empresa: Nome da empresa
            
        Returns:
            dict: Resultado da otimização (ver ProductionOptimizer.otimizar_producao)
        """
        if nome_empresa not in self.empresas:
            return {
                'sucesso': False,
                'mensagem': 'Empresa não encontrada'
            }
        
        try:
            from web_app.optimizer import ProductionOptimizer
            
            empresa = self.empresas[nome_empresa]
            # IMPORTANTE: Usar recursos_base (que resetam a cada iteração)
            # NÃO usar recursos_disponiveis (que podem estar após consumo)
            recursos = empresa['recursos_base'].copy()
            
            print(f"\n[CALCULAR OTIMO] {nome_empresa}")
            print(f"  Recursos usados para otimização: {recursos}")
            
            # Usar produtos customizados se disponíveis para esta empresa
            produtos_para_otimizacao = self.produtos.copy()
            if empresa.get('produtos_customizados'):
                print(f"  Usando custos customizados para {nome_empresa}")
                # Sobrescrever com custos customizados
                for produto, custos_custom in empresa['produtos_customizados'].items():
                    if produto in produtos_para_otimizacao:
                        produtos_para_otimizacao[produto].update(custos_custom)
                        print(f"    {produto}: {custos_custom}")
            
            optimizer = ProductionOptimizer()
            resultado = optimizer.otimizar_producao(recursos, produtos_customizados=produtos_para_otimizacao)
            
            # Guardar solução ótima na empresa (SEM MOSTRAR NA TELA)
            if resultado.get('sucesso'):
                empresa['solucao_otima'] = resultado['producao_otima']
                empresa['lucro_otimo'] = resultado['lucro_esperado']
                
                # Calcular GAP% corretamente
                # GAP = (Ótimo - Atual) / Ótimo * 100
                # Se atual é negativo ou zero, distância é maior (pode passar de 100%)
                # GAP nunca é negativo (mínimo 0% quando atual >= ótimo)
                lucro_atual = empresa.get('lucro_ultimo_turno', 0)
                lucro_otimo = empresa['lucro_otimo']
                
                if lucro_otimo > 0:
                    gap = ((lucro_otimo - lucro_atual) / lucro_otimo) * 100
                    # GAP não pode ser negativo (se atual > ótimo, GAP = 0%)
                    empresa['gap_percentual'] = max(0, gap)
                else:
                    # Se lucro ótimo for 0, GAP é 0 (não há o que melhorar)
                    empresa['gap_percentual'] = 0
                
                print(f"  Lucro Último Turno: R$ {lucro_atual:.2f}")
                print(f"  Lucro Ótimo: R$ {lucro_otimo:.2f}")
                print(f"  GAP%: {empresa['gap_percentual']:.1f}%")
            
            return resultado
            
        except ImportError as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao importar otimizador: {str(e)}'
            }
        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao calcular solução ótima: {str(e)}'
            }
    
    def enviar_solucao_para_empresa(self, nome_empresa: str) -> dict:
        """Envia solução ótima para a tela da empresa (SEM confirmar)
        A empresa pode ver os valores e modificar antes de confirmar
        
        Args:
            nome_empresa: Nome da empresa
            
        Returns:
            dict: Resultado com a solução ótima para preencher o formulário
        """
        if nome_empresa not in self.empresas:
            return {
                'sucesso': False,
                'mensagem': 'Empresa não encontrada'
            }
        
        # Calcular solução ótima
        resultado_otimizacao = self.calcular_solucao_otima(nome_empresa)
        
        if not resultado_otimizacao['sucesso']:
            return resultado_otimizacao
        
        # Pegar produção ótima
        producao_otima = resultado_otimizacao['producao_otima']
        
        # Preencher decisao_atual SEM confirmar (para o aluno ver e modificar)
        empresa = self.empresas[nome_empresa]
        empresa['decisao_atual'] = producao_otima.copy()
        empresa['decisao_confirmada'] = False  # NÃO confirma automaticamente
        
        return {
            'sucesso': True,
            'mensagem': f'Solução ótima enviada para {nome_empresa}! A empresa pode modificar antes de confirmar.',
            'producao_otima': producao_otima,
            'lucro_esperado': resultado_otimizacao['lucro_esperado'],
            'detalhes': resultado_otimizacao['detalhes']
        }
    
    def aplicar_solucao_otima(self, nome_empresa: str) -> dict:
        """Calcula e aplica automaticamente a solução ótima para uma empresa (CONFIRMADA)
        
        Args:
            nome_empresa: Nome da empresa
            
        Returns:
            dict: Resultado da operação com status e detalhes
        """
        if nome_empresa not in self.empresas:
            return {
                'sucesso': False,
                'mensagem': 'Empresa não encontrada'
            }
        
        # Calcular solução ótima
        resultado_otimizacao = self.calcular_solucao_otima(nome_empresa)
        
        if not resultado_otimizacao['sucesso']:
            return resultado_otimizacao
        
        # Aplicar a solução como decisão da empresa
        producao_otima = resultado_otimizacao['producao_otima']
        
        # Converter para formato de decisões (usar nomes de produtos sem emojis)
        decisoes = {}
        for produto_completo, quantidade in producao_otima.items():
            # Encontrar o produto correspondente
            decisoes[produto_completo] = quantidade
        
        # Aplicar diretamente SEM VALIDAÇÃO (a solução ótima já é válida por definição)
        empresa = self.empresas[nome_empresa]
        
        # Reset recursos_disponiveis para recursos_base
        empresa['recursos_disponiveis'] = empresa['recursos_base'].copy()
        
        # Aplicar decisões diretamente E CONFIRMAR AUTOMATICAMENTE
        empresa['decisao_atual'] = decisoes
        empresa['decisao_confirmada'] = True  # Confirmada automaticamente pelo admin
        
        return {
            'sucesso': True,
            'mensagem': f'Solução ótima aplicada e confirmada automaticamente para {nome_empresa}!',
            'producao_otima': producao_otima,
            'lucro_esperado': resultado_otimizacao['lucro_esperado'],
            'detalhes': resultado_otimizacao['detalhes']
        }
    
    def _calcular_e_guardar_otimo(self, nome_empresa: str) -> bool:
        """Calcular e guardar solução ótima internamente (método auxiliar privado)
        
        Args:
            nome_empresa: Nome da empresa
            
        Returns:
            bool: True se calculou com sucesso
        """
        if nome_empresa not in self.empresas:
            return False
        
        try:
            from web_app.optimizer import ProductionOptimizer
            
            empresa = self.empresas[nome_empresa]
            # IMPORTANTE: Usar recursos_base (que resetam a cada iteração)
            recursos = empresa['recursos_base'].copy()
            
            optimizer = ProductionOptimizer()
            resultado = optimizer.otimizar_producao(recursos)
            
            if resultado.get('sucesso'):
                empresa['solucao_otima'] = resultado['producao_otima']
                empresa['lucro_otimo'] = resultado['lucro_esperado']
                
                # Calcular GAP% corretamente
                lucro_atual = empresa.get('lucro_ultimo_turno', 0)
                lucro_otimo = empresa['lucro_otimo']
                
                if lucro_otimo > 0:
                    gap = ((lucro_otimo - lucro_atual) / lucro_otimo) * 100
                    # GAP não pode ser negativo (mínimo 0%)
                    empresa['gap_percentual'] = max(0, gap)
                else:
                    empresa['gap_percentual'] = 0
                
                print(f"[OTIMO] {nome_empresa}: GAP = {empresa['gap_percentual']:.1f}% (Último: R$ {lucro_atual:.2f})")
                return True
            
            return False
            
        except Exception as e:
            print(f"[ERRO] Falha ao calcular ótimo para {nome_empresa}: {e}")
            return False
    
    def calcular_otimo_sem_mostrar(self, nome_empresa: str) -> dict:
        """Calcular solução ótima e guardar internamente (SEM MOSTRAR solução na tela)
        Retorna apenas o GAP% e informações resumidas
        
        Args:
            nome_empresa: Nome da empresa
            
        Returns:
            dict: Resultado com GAP% e informações resumidas (sem mostrar a solução)
        """
        if nome_empresa not in self.empresas:
            return {
                'sucesso': False,
                'mensagem': 'Empresa não encontrada'
            }
        
        sucesso = self._calcular_e_guardar_otimo(nome_empresa)
        
        if sucesso:
            empresa = self.empresas[nome_empresa]
            return {
                'sucesso': True,
                'empresa': nome_empresa,
                'lucro_atual': empresa.get('lucro_ultimo_turno', 0),
                'lucro_otimo': empresa['lucro_otimo'],
                'gap_percentual': empresa['gap_percentual'],
                'mensagem': f'Solução ótima calculada! GAP: {empresa["gap_percentual"]:.1f}%'
            }
        else:
            return {
                'sucesso': False,
                'mensagem': 'Erro ao calcular solução ótima'
            }
    
    def calcular_otimo_todas_empresas(self) -> dict:
        """Calcular solução ótima para TODAS as empresas (sem mostrar soluções)
        
        Returns:
            dict: Resultado com resumo de todas as empresas
        """
        resultados = []
        total_sucesso = 0
        total_falhas = 0
        
        for nome_empresa in self.empresas.keys():
            resultado = self.calcular_otimo_sem_mostrar(nome_empresa)
            resultados.append(resultado)
            
            if resultado['sucesso']:
                total_sucesso += 1
            else:
                total_falhas += 1
        
        return {
            'sucesso': True,
            'total_empresas': len(self.empresas),
            'calculados': total_sucesso,
            'falhas': total_falhas,
            'resultados': resultados,
            'mensagem': f'Cálculo concluído: {total_sucesso} empresas processadas'
        }
    
    def enviar_otimo_todas_empresas(self) -> dict:
        """Enviar solução ótima para TODAS as empresas (SEM confirmar)
        Empresas podem modificar antes de confirmar
        
        Returns:
            dict: Resultado com resumo da operação
        """
        resultados = []
        total_sucesso = 0
        total_falhas = 0
        
        for nome_empresa in self.empresas.keys():
            resultado = self.enviar_solucao_para_empresa(nome_empresa)
            resultados.append({
                'empresa': nome_empresa,
                'sucesso': resultado['sucesso'],
                'mensagem': resultado.get('mensagem', '')
            })
            
            if resultado['sucesso']:
                total_sucesso += 1
            else:
                total_falhas += 1
        
        return {
            'sucesso': True,
            'total_empresas': len(self.empresas),
            'enviados': total_sucesso,
            'falhas': total_falhas,
            'resultados': resultados,
            'mensagem': f'Solução ótima enviada para {total_sucesso} empresas (podem modificar)'
        }
    
    def aplicar_otimo_todas_empresas(self) -> dict:
        """Aplicar E CONFIRMAR solução ótima em TODAS as empresas (GAP 0% para todos)
        
        Returns:
            dict: Resultado com resumo da operação
        """
        resultados = []
        total_sucesso = 0
        total_falhas = 0
        
        for nome_empresa in self.empresas.keys():
            resultado = self.aplicar_solucao_otima(nome_empresa)
            resultados.append({
                'empresa': nome_empresa,
                'sucesso': resultado['sucesso'],
                'mensagem': resultado.get('mensagem', '')
            })
            
            if resultado['sucesso']:
                total_sucesso += 1
            else:
                total_falhas += 1
        
        return {
            'sucesso': True,
            'total_empresas': len(self.empresas),
            'aplicados': total_sucesso,
            'falhas': total_falhas,
            'resultados': resultados,
            'mensagem': f'Solução ótima aplicada e confirmada em {total_sucesso} empresas (GAP 0%)'
        }
    
    def salvar_estado_arquivo(self, nome_arquivo: str = None) -> tuple:
        """Salvar estado do jogo em arquivo JSON
        
        Args:
            nome_arquivo: Nome do arquivo (sem extensão). Se None, usa data/hora atual
            
        Returns:
            tuple: (sucesso: bool, mensagem: str, caminho_arquivo: str)
        """
        try:
            # Criar pasta de saves se não existir
            saves_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saves')
            os.makedirs(saves_dir, exist_ok=True)
            
            # Gerar nome do arquivo se não fornecido
            if not nome_arquivo:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nome_arquivo = f"save_{timestamp}"
            
            # Garantir extensão .json
            if not nome_arquivo.endswith('.json'):
                nome_arquivo += '.json'
            
            # Caminho completo do arquivo
            caminho_arquivo = os.path.join(saves_dir, nome_arquivo)
            
            # Obter estado atual
            estado = self.obter_estado()
            
            # Adicionar metadados
            estado['_metadata'] = {
                'versao': '2.1',
                'data_save': datetime.now().isoformat(),
                'total_empresas': len(self.empresas),
                'iteracao_atual': self.iteracao_atual
            }
            
            # Salvar arquivo
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(estado, f, indent=2, ensure_ascii=False)
            
            # Guardar nome do arquivo para auto-save futuro
            self.ultimo_arquivo_salvo = nome_arquivo.replace('.json', '')
            
            return True, f"Save '{nome_arquivo}' criado com sucesso!", nome_arquivo
            
        except Exception as e:
            return False, f"Erro ao salvar: {str(e)}", None
    
    def listar_saves(self) -> list:
        """Listar todos os saves disponíveis
        
        Returns:
            list: Lista de dicts com informações dos saves
        """
        try:
            saves_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saves')
            
            if not os.path.exists(saves_dir):
                return []
            
            saves = []
            for arquivo in os.listdir(saves_dir):
                if arquivo.endswith('.json'):
                    caminho_completo = os.path.join(saves_dir, arquivo)
                    
                    # Ler metadados do arquivo
                    try:
                        with open(caminho_completo, 'r', encoding='utf-8') as f:
                            dados = json.load(f)
                        
                        metadata = dados.get('_metadata', {})
                        
                        saves.append({
                            'nome': arquivo,
                            'tamanho': os.path.getsize(caminho_completo),
                            'data_modificacao': datetime.fromtimestamp(os.path.getmtime(caminho_completo)).isoformat(),
                            'data_save': metadata.get('data_save', 'N/A'),
                            'versao': metadata.get('versao', 'N/A'),
                            'total_empresas': metadata.get('total_empresas', 0),
                            'iteracao_atual': metadata.get('iteracao_atual', 0)
                        })
                    except:
                        # Se falhar ao ler, adicionar info básica
                        saves.append({
                            'nome': arquivo,
                            'tamanho': os.path.getsize(caminho_completo),
                            'data_modificacao': datetime.fromtimestamp(os.path.getmtime(caminho_completo)).isoformat(),
                            'data_save': 'N/A',
                            'versao': 'Desconhecida',
                            'total_empresas': 0,
                            'iteracao_atual': 0
                        })
            
            # Ordenar por data de modificação (mais recente primeiro)
            saves.sort(key=lambda x: x['data_modificacao'], reverse=True)
            return saves
            
        except Exception as e:
            print(f"Erro ao listar saves: {e}")
            return []
    
    def carregar_estado_arquivo(self, nome_arquivo: str) -> tuple:
        """Carregar estado do jogo de um arquivo JSON
        
        Args:
            nome_arquivo: Nome do arquivo a carregar
            
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        try:
            saves_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saves')
            caminho_arquivo = os.path.join(saves_dir, nome_arquivo)
            
            if not os.path.exists(caminho_arquivo):
                return False, "Arquivo não encontrado!"
            
            # Ler arquivo
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                estado = json.load(f)
            
            # Validar estrutura básica
            campos_obrigatorios = ['empresas', 'iteracao_atual', 'max_iteracoes', 'produtos']
            for campo in campos_obrigatorios:
                if campo not in estado:
                    return False, f"Save inválido: campo '{campo}' não encontrado!"
            
            # Validar versão (opcional, mas avisa)
            metadata = estado.get('_metadata', {})
            versao = metadata.get('versao', 'antiga')
            
            # Carregar estado
            sucesso = self.carregar_estado(estado)
            
            if sucesso:
                # Guardar nome do arquivo para auto-save futuro
                self.ultimo_arquivo_salvo = nome_arquivo.replace('.json', '')
                
                # Invalidar todas as sessões após carregar
                self.invalidar_todas_sessoes()
                return True, f"Save '{nome_arquivo}' carregado com sucesso! (Versão: {versao})"
            else:
                return False, "Erro ao aplicar o estado do save!"
                
        except json.JSONDecodeError:
            return False, "Arquivo JSON inválido!"
        except Exception as e:
            return False, f"Erro ao carregar save: {str(e)}"
    
    def excluir_save(self, nome_arquivo: str) -> tuple:
        """Excluir um save específico
        
        Args:
            nome_arquivo: Nome do arquivo a excluir
            
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        try:
            saves_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saves')
            caminho_arquivo = os.path.join(saves_dir, nome_arquivo)
            
            if not os.path.exists(caminho_arquivo):
                return False, "Arquivo não encontrado!"
            
            os.remove(caminho_arquivo)
            return True, f"Save '{nome_arquivo}' excluído com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao excluir save: {str(e)}"
    
    def excluir_todos_saves(self) -> tuple:
        """Excluir todos os saves
        
        Returns:
            tuple: (sucesso: bool, mensagem: str, quantidade: int)
        """
        try:
            saves_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saves')
            
            if not os.path.exists(saves_dir):
                return True, "Nenhum save para excluir!", 0
            
            count = 0
            for arquivo in os.listdir(saves_dir):
                if arquivo.endswith('.json'):
                    os.remove(os.path.join(saves_dir, arquivo))
                    count += 1
            
            return True, f"{count} save(s) excluído(s) com sucesso!", count
            
        except Exception as e:
            return False, f"Erro ao excluir saves: {str(e)}", 0
    
    def obter_caminho_save(self, nome_arquivo: str) -> str:
        """Obter caminho completo de um save
        
        Args:
            nome_arquivo: Nome do arquivo
            
        Returns:
            str: Caminho completo ou None se não existir
        """
        saves_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saves')
        caminho_arquivo = os.path.join(saves_dir, nome_arquivo)
        
        if os.path.exists(caminho_arquivo):
            return caminho_arquivo
        return None
    
    def validar_save_upload(self, dados_json: dict) -> tuple:
        """Validar dados de um save antes de carregar
        
        Args:
            dados_json: Dados do JSON carregado
            
        Returns:
            tuple: (valido: bool, mensagem: str)
        """
        try:
            # Verificar campos obrigatórios
            campos_obrigatorios = ['empresas', 'iteracao_atual', 'max_iteracoes', 'produtos']
            for campo in campos_obrigatorios:
                if campo not in dados_json:
                    return False, f"Campo obrigatório ausente: '{campo}'"
            
            # Validar tipos
            if not isinstance(dados_json['empresas'], dict):
                return False, "Campo 'empresas' deve ser um dicionário"
            
            if not isinstance(dados_json['iteracao_atual'], int):
                return False, "Campo 'iteracao_atual' deve ser um número inteiro"
            
            if not isinstance(dados_json['max_iteracoes'], int):
                return False, "Campo 'max_iteracoes' deve ser um número inteiro"
            
            if not isinstance(dados_json['produtos'], dict):
                return False, "Campo 'produtos' deve ser um dicionário"
            
            # Validar estrutura de empresas
            for nome_empresa, empresa in dados_json['empresas'].items():
                if not isinstance(empresa, dict):
                    return False, f"Empresa '{nome_empresa}' tem estrutura inválida"
                
                campos_empresa = ['recursos_base', 'recursos_disponiveis', 'lucro_total']
                for campo in campos_empresa:
                    if campo not in empresa:
                        return False, f"Empresa '{nome_empresa}': campo '{campo}' ausente"
            
            return True, "Save válido!"
            
        except Exception as e:
            return False, f"Erro na validação: {str(e)}"

# Instância global do estado do jogo
game_state = GameState()
