# -*- coding: utf-8 -*-
"""
Configurações e constantes do jogo
"""

class GameConfig:
    """Configuração do jogo"""
    
    # Configurações gerais
    MAX_ITERACOES = 12
    MAX_TURNOS = 12  # Alias para compatibilidade
    
    # Configurações da janela
    WINDOW_TITLE = "🏭 PLANEJADOR DE PRODUÇÃO OTIMIZADO - MULTI-EMPRESAS"
    WINDOW_GEOMETRY = (50, 50, 1400, 800)
    WINDOW_MIN_SIZE = (1000, 600)
    
    # Recursos base disponíveis para o mês
    RECURSOS_BASE = {
        "dinheiro": 50000,
        "materia_prima": 2500,
        "energia": 3500,
        "trabalhadores": 100
    }
    
    # Custos unitários r_j (valor monetário de uma unidade de recurso)
    CUSTOS_UNITARIOS_RECURSOS = {
        "dinheiro": 1.0,              # cada 1 dólar investido
        "materia_prima": 12.0,        # custo por unidade de matéria-prima
        "energia": 0.45,              # custo por kWh equivalente
        "trabalhadores": 28.0         # custo por colaborador-hora
    }
    
    # Produtos com características mais realistas (compartilhado entre empresas)
    PRODUTOS = {
        "📱 Smartphone": {
            "custo_materia": 45,
            "custo_energia": 25,
            "custo_trabalhadores": 3,
            "preco_venda": 180,
            "tempo_producao": 2,
            "cor": "#E74C3C",
            "emoji": "📱"
        },
        "💻 Laptop": {
            "custo_materia": 85,
            "custo_energia": 60,
            "custo_trabalhadores": 5,
            "preco_venda": 350,
            "tempo_producao": 3,
            "cor": "#3498DB",
            "emoji": "💻"
        },
        "🖥️ Desktop": {
            "custo_materia": 120,
            "custo_energia": 80,
            "custo_trabalhadores": 7,
            "preco_venda": 480,
            "tempo_producao": 4,
            "cor": "#9B59B6",
            "emoji": "🖥️"
        }
    }
    
    # Mapeamento de recursos para campos de custo nos produtos
    MAPEAMENTO_CUSTO = {
        'materia_prima': 'custo_materia',
        'energia': 'custo_energia',
        'trabalhadores': 'custo_trabalhadores'
    }
    
    # Emojis e nomes legíveis para recursos
    EMOJI_RECURSO = {
        "dinheiro": "💰", 
        "materia_prima": "📦", 
        "energia": "⚡", 
        "trabalhadores": "👥"
    }
    
    NOMES_RECURSOS = {
        "dinheiro": "Dinheiro", 
        "materia_prima": "Matéria-prima", 
        "energia": "Energia", 
        "trabalhadores": "Equipe"
    }
    
    # Cores de acento para recursos
    CORES_ACENTO = {
        "dinheiro": "#1ABC9C",
        "materia_prima": "#E67E22",
        "energia": "#F39C12",
        "trabalhadores": "#9B59B6"
    }
    
    # Assegurar que produtos tenham custo financeiro básico
    @classmethod
    def inicializar_produtos(cls):
        """Garante custo financeiro básico caso não esteja definido"""
        for dados_produto in cls.PRODUTOS.values():
            if 'custo_dinheiro' not in dados_produto:
                dados_produto['custo_dinheiro'] = (
                    dados_produto.get('custo_materia', 0)
                    + dados_produto.get('custo_energia', 0)
                    + dados_produto.get('custo_trabalhadores', 0)
                )
    
    @classmethod
    def get_produtos_inicializados(cls):
        """Retorna produtos com custos financeiros inicializados"""
        cls.inicializar_produtos()
        return cls.PRODUTOS.copy()