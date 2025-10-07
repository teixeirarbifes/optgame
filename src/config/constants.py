# -*- coding: utf-8 -*-
"""
Configuracoes e constantes do jogo
"""

class GameConfig:
    """Configuracao do jogo"""
    
    MAX_ITERACOES = 12
    MAX_TURNOS = 12
    
    WINDOW_TITLE = "PLANEJADOR DE PRODUCAO OTIMIZADO - MULTI-EMPRESAS"
    WINDOW_GEOMETRY = (50, 50, 1400, 800)
    WINDOW_MIN_SIZE = (1000, 600)

    PORTAL_ENABLED = True
    PORTAL_HOST = "0.0.0.0"
    PORTAL_PORT = 8050
    PORTAL_TITLE = "Portal Educacional de Producao"
    PORTAL_PASSWORD_SIZE = 8
    
    RECURSOS_BASE = {
        "dinheiro": 50000,
        "materia_prima": 20000,
        "energia": 15000,
        "trabalhadores": 600
    }
    
    CUSTOS_UNITARIOS_RECURSOS = {
        "materia_prima": 1.20,
        "energia": 0.65,
        "trabalhadores": 22.00
    }
    
    PRODUTOS = {
        "Smartphone": {
            "consumo_materia": 12,
            "consumo_energia": 7,
            "consumo_trabalhadores": 0.5,
            "preco_venda": 95,
            "cor": "#E74C3C",
            "emoji": ""
        },
        "Laptop": {
            "consumo_materia": 30,
            "consumo_energia": 15,
            "consumo_trabalhadores": 0.8,
            "preco_venda": 165,
            "cor": "#3498DB",
            "emoji": ""
        },
        "Desktop": {
            "consumo_materia": 45,
            "consumo_energia": 22,
            "consumo_trabalhadores": 1.2,
            "preco_venda": 220,
            "cor": "#9B59B6",
            "emoji": ""
        },
        "Smartwatch": {
            "consumo_materia": 8,
            "consumo_energia": 4,
            "consumo_trabalhadores": 0.35,
            "preco_venda": 58,
            "cor": "#1ABC9C",
            "emoji": ""
        },
        "Impressora": {
            "consumo_materia": 25,
            "consumo_energia": 18,
            "consumo_trabalhadores": 0.6,
            "preco_venda": 135,
            "cor": "#34495E",
            "emoji": ""
        },
        "Camera": {
            "consumo_materia": 18,
            "consumo_energia": 9,
            "consumo_trabalhadores": 0.7,
            "preco_venda": 110,
            "cor": "#E67E22",
            "emoji": ""
        }
    }
    
    MAPEAMENTO_CONSUMO = {
        'materia_prima': 'consumo_materia',
        'energia': 'consumo_energia',
        'trabalhadores': 'consumo_trabalhadores'
    }
    
    MAPEAMENTO_CUSTO = {
        'materia_prima': 'consumo_materia',
        'energia': 'consumo_energia',
        'trabalhadores': 'consumo_trabalhadores'
    }
    
    EMOJI_RECURSO = {
        "dinheiro": "", 
        "materia_prima": "", 
        "energia": "", 
        "trabalhadores": ""
    }
    
    NOMES_RECURSOS = {
        "dinheiro": "Dinheiro", 
        "materia_prima": "Materia-prima", 
        "energia": "Energia", 
        "trabalhadores": "Equipe"
    }
    
    CORES_ACENTO = {
        "dinheiro": "#1ABC9C",
        "materia_prima": "#E67E22",
        "energia": "#F39C12",
        "trabalhadores": "#9B59B6"
    }
    
    @classmethod
    def get_produtos_inicializados(cls):
        return cls.PRODUTOS.copy()
    
    @classmethod
    def calcular_custo_produto(cls, produto_nome, quantidade):
        if produto_nome not in cls.PRODUTOS:
            return {}
        
        produto = cls.PRODUTOS[produto_nome]
        
        return {
            'consumo_materia': produto.get('consumo_materia', 0) * quantidade,
            'consumo_energia': produto.get('consumo_energia', 0) * quantidade,
            'consumo_trabalhadores': produto.get('consumo_trabalhadores', 0) * quantidade,
            'custo_monetario': (
                produto.get('consumo_materia', 0) * quantidade * cls.CUSTOS_UNITARIOS_RECURSOS['materia_prima'] +
                produto.get('consumo_energia', 0) * quantidade * cls.CUSTOS_UNITARIOS_RECURSOS['energia'] +
                produto.get('consumo_trabalhadores', 0) * quantidade * cls.CUSTOS_UNITARIOS_RECURSOS['trabalhadores']
            ),
            'receita': produto.get('preco_venda', 0) * quantidade
        }
    
    @classmethod
    def validar_decisao(cls, decisoes, recursos_disponiveis):
        consumo_total = {
            'materia_prima': 0,
            'energia': 0,
            'trabalhadores': 0,
            'dinheiro': 0
        }
        
        for produto, quantidade in decisoes.items():
            if quantidade <= 0:
                continue
            if produto not in cls.PRODUTOS:
                continue
                
            dados = cls.PRODUTOS[produto]
            consumo_total['materia_prima'] += dados.get('consumo_materia', 0) * quantidade
            consumo_total['energia'] += dados.get('consumo_energia', 0) * quantidade
            consumo_total['trabalhadores'] += dados.get('consumo_trabalhadores', 0) * quantidade
            consumo_total['dinheiro'] += (
                dados.get('consumo_materia', 0) * quantidade * cls.CUSTOS_UNITARIOS_RECURSOS['materia_prima'] +
                dados.get('consumo_energia', 0) * quantidade * cls.CUSTOS_UNITARIOS_RECURSOS['energia'] +
                dados.get('consumo_trabalhadores', 0) * quantidade * cls.CUSTOS_UNITARIOS_RECURSOS['trabalhadores']
            )
        
        violacoes = []
        for recurso in ['dinheiro', 'materia_prima', 'energia', 'trabalhadores']:
            necessario = consumo_total[recurso]
            disponivel = recursos_disponiveis.get(recurso, 0)
            if necessario > disponivel:
                violacoes.append({
                    'recurso': recurso,
                    'necessario': necessario,
                    'disponivel': disponivel,
                    'deficit': necessario - disponivel
                })
        
        return (len(violacoes) == 0, violacoes)
