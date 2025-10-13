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
        "trabalhadores": 600,
        "chips_processamento": 1800,  # REDUZIDO: Recurso mais escasso - força escolha estratégica!
        "engenheiros_senior": 350      # REDUZIDO: Recurso escasso - cria trade-off real
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
            "consumo_chips_processamento": 3.5,   # AUMENTADO: Muito alto (limitante!) - competição por chips
            "consumo_engenheiros_senior": 0.4,    # AUMENTADO: Produto complexo
            "preco_venda": 98,                     # AUMENTADO: Melhor margem base
            "cor": "#E74C3C",
            "emoji": "📱"
        },
        "Laptop": {
            "consumo_materia": 30,
            "consumo_energia": 15,
            "consumo_trabalhadores": 0.8,
            "consumo_chips_processamento": 2.8,   # REDUZIDO: Menos chips que Smartphone
            "consumo_engenheiros_senior": 0.4,    # REDUZIDO: Mais padronizado
            "preco_venda": 175,                    # AUMENTADO: Melhor margem
            "cor": "#3498DB",
            "emoji": "💻"
        },
        "Desktop": {
            "consumo_materia": 45,
            "consumo_energia": 22,
            "consumo_trabalhadores": 1.2,
            "consumo_chips_processamento": 1.8,   # REDUZIDO: Componentes mais simples
            "consumo_engenheiros_senior": 0.15,   # REDUZIDO: Produto commoditizado
            "preco_venda": 235,                    # AUMENTADO: Muito melhor margem
            "cor": "#9B59B6",
            "emoji": "🖥️"
        },
        "Smartwatch": {
            "consumo_materia": 8,
            "consumo_energia": 4,
            "consumo_trabalhadores": 0.35,
            "consumo_chips_processamento": 2.8,   # AUMENTADO: Miniaturização = chips caros!
            "consumo_engenheiros_senior": 0.5,    # AUMENTADO: Tecnologia complexa
            "preco_venda": 60,                     # AUMENTADO: Melhor margem
            "cor": "#1ABC9C",
            "emoji": "⌚"
        },
        "Impressora": {
            "consumo_materia": 25,
            "consumo_energia": 18,
            "consumo_trabalhadores": 0.6,
            "consumo_chips_processamento": 0.0,   # Não precisa (tecnologia mecânica)
            "consumo_engenheiros_senior": 0.0,    # Não precisa (produto simples)
            "preco_venda": 140,                    # AUMENTADO: Melhor margem
            "cor": "#34495E",
            "emoji": "🖨️"
        },
        "Camera": {
            "consumo_materia": 18,
            "consumo_energia": 9,
            "consumo_trabalhadores": 0.7,
            "consumo_chips_processamento": 1.2,   # AUMENTADO: Processador de imagem (mas menos que Smartphone)
            "consumo_engenheiros_senior": 0.6,    # REDUZIDO: Ótica especializada mas não tanto
            "preco_venda": 125,                    # AUMENTADO: MUITO melhor margem! (110→125)
            "cor": "#E67E22",
            "emoji": "📷"
        }
    }
    
    MAPEAMENTO_CONSUMO = {
        'materia_prima': 'consumo_materia',
        'energia': 'consumo_energia',
        'trabalhadores': 'consumo_trabalhadores',
        'chips_processamento': 'consumo_chips_processamento',
        'engenheiros_senior': 'consumo_engenheiros_senior'
    }
    
    MAPEAMENTO_CUSTO = {
        'materia_prima': 'consumo_materia',
        'energia': 'consumo_energia',
        'trabalhadores': 'consumo_trabalhadores',
        'chips_processamento': 'consumo_chips_processamento',
        'engenheiros_senior': 'consumo_engenheiros_senior'
    }
    
    EMOJI_RECURSO = {
        "dinheiro": "💰", 
        "materia_prima": "📦", 
        "energia": "⚡", 
        "trabalhadores": "👥",
        "chips_processamento": "🔌",
        "engenheiros_senior": "👨‍💻"
    }
    
    NOMES_RECURSOS = {
        "dinheiro": "Dinheiro", 
        "materia_prima": "Materia-prima", 
        "energia": "Energia", 
        "trabalhadores": "Equipe",
        "chips_processamento": "Chips Processamento",
        "engenheiros_senior": "Eng. Sênior"
    }
    
    CORES_ACENTO = {
        "dinheiro": "#1ABC9C",
        "materia_prima": "#E67E22",
        "energia": "#F39C12",
        "trabalhadores": "#9B59B6",
        "chips_processamento": "#3498DB",
        "engenheiros_senior": "#E74C3C"
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
