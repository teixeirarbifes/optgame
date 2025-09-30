import sys
import os
import tempfile
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                               QLineEdit, QTextEdit, QTabWidget, QFrame, 
                               QScrollArea, QMessageBox, QDialog, QSpinBox,
                               QSplitter, QGroupBox, QFormLayout, QSlider, QProgressBar,
                               QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
                               QFileDialog)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPalette, QColor, QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import json
from datetime import datetime

# Importar configurações
from config.constants import GameConfig
from controller.controller import GameController

class JogoEconomicoImersivo(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configurações de autosave e estado inicial
        self.caminho_autosave = os.path.join(tempfile.gettempdir(), "planejador_multi_empresas_autosave.json")
        self.carregou_autosave = False
        self.dados_carregados = None

        # Estado do jogo (compatibility for both terminologies)
        self.iteracao_atual = 1
        self.turno_atual = 1  # Alias para compatibilidade
        self.max_iteracoes = GameConfig.MAX_ITERACOES
        self.max_turnos = GameConfig.MAX_TURNOS  # Alias para compatibilidade

        # Estruturas principais do sistema
        self.nomes_empresas = []
        self.equipes_empresas = {}
        self.empresas = {}
        self.empresa_ativa = None

        # Inicializar dicionários para controles de interface
        self.sliders_decisao_empresas = {}
        self.spinboxes_decisao_empresas = {}
        self.labels_valores_empresas = {}
        self.graficos_empresas = {}
        self.widgets_validacao_empresas = {}
        self.paineis_recursos_empresas = {}
        self.paineis_restricoes_empresas = {}
        self.paineis_violacoes_empresas = {}
        self.paineis_objetivo_empresas = {}
        self.paineis_info_empresas = {}
        self.labels_recursos_empresas = {}
        self.labels_recursos_compacto_empresas = {}
        self.displays_ordens_expandida = {}
        self.text_simulacao_empresas = {}
        self.text_simulacao_expandida = {}
        self.sub_tabs_empresas = {}
        self.ultimo_arquivo_salvo = None
        
        # Usar configurações do módulo
        self.recursos_base = GameConfig.RECURSOS_BASE.copy()
        self.custos_unitarios_recursos = GameConfig.CUSTOS_UNITARIOS_RECURSOS.copy()
        self.produtos = GameConfig.get_produtos_inicializados()

        # Camada de controle para regras de negócio
        self.controller = GameController(self)

        # Configurar tema escuro
        self.configurar_tema_escuro()

        # Setup inicial - configurar múltiplas empresas ou carregar autosave
        self.configurar_empresas()

        # Configurar janela principal (mais responsiva)
        self.setWindowTitle(GameConfig.WINDOW_TITLE)
        self.setGeometry(*GameConfig.WINDOW_GEOMETRY)
        self.setMinimumSize(*GameConfig.WINDOW_MIN_SIZE)

        if self.carregou_autosave and self.dados_carregados:
            self.empresas = self.dados_carregados.get('empresas', {})
            self.iteracao_atual = self.dados_carregados.get('iteracao_atual', self.iteracao_atual)
            self.turno_atual = self.dados_carregados.get('turno_atual', self.turno_atual)
            self.max_iteracoes = self.dados_carregados.get('max_iteracoes', self.max_iteracoes)
            self.max_turnos = self.dados_carregados.get('max_turnos', self.max_turnos)
            self.empresa_ativa = self.nomes_empresas[0] if self.nomes_empresas else None
            for nome_empresa in self.nomes_empresas:
                self._garantir_estruturas_empresa(nome_empresa)
                self.widgets_validacao_empresas.setdefault(nome_empresa, {})
        else:
            # Inicializar empresas com dados padrão
            self.inicializar_empresas()

        for nome_empresa in self.nomes_empresas:
            self.widgets_validacao_empresas.setdefault(nome_empresa, {})

        self.criar_interface()
        self.atualizar_graficos()
        self.atualizar_todas_interfaces()
        self.salvar_estado_temporario()
    
    def inicializar_empresas(self):
        """Inicializa os dados de cada empresa"""
        for nome_empresa in self.nomes_empresas:
            # Variáveis de decisão iniciais (quantidades de cada produto)
            variaveis_decisao = {}
            for produto in self.produtos.keys():
                variaveis_decisao[produto] = 0  # Quantidade inicial
                
            self.empresas[nome_empresa] = {
                'recursos_disponiveis': self.recursos_base.copy(),  # Recursos para o mês
                'variaveis_decisao': variaveis_decisao,  # Quantidades planejadas
                'historico_iteracoes': [],  # Histórico de cada iteração
                'historico_recursos': {
                    'turnos': [],
                    'dinheiro': [],
                    'materia_prima': [],
                    'energia': [],
                    'trabalhadores': [],
                },
                'historico_decisoes': [],
                'producao_atual': {},
                'restricoes_violadas': [],  # Restrições violadas na última validação
                'objetivo_atual': 0,  # Valor da função objetivo
                'equipes': self.equipes_empresas[nome_empresa]
            }
            
            # Inicializar dicionários de controles de interface para cada empresa
            self.sliders_decisao_empresas[nome_empresa] = {}
            self.spinboxes_decisao_empresas[nome_empresa] = {}
            self.labels_valores_empresas[nome_empresa] = {}
            self.graficos_empresas[nome_empresa] = {}
            
            # Adicionar referência para widgets de validação
            if not hasattr(self, 'widgets_validacao_empresas'):
                self.widgets_validacao_empresas = {}
            self.widgets_validacao_empresas[nome_empresa] = {}
        
        # Definir primeira empresa como ativa
        self.empresa_ativa = self.nomes_empresas[0] if self.nomes_empresas else None
    
    def _garantir_estruturas_empresa(self, nome_empresa):
        """Garante que dicionários auxiliares da empresa existam (retrocompatibilidade)."""
        self.controller.garantir_estruturas_empresa(nome_empresa)

    def calcular_custo_financeiro_produto(self, produto, quantidade=1):
        """Retorna o custo monetário associado à produção de um produto"""
        return self.controller.calcular_custo_financeiro_produto(produto, quantidade)

    def calcular_custo_total_plano(self, variaveis_decisao):
        """Soma o custo financeiro total do plano de produção"""
        return self.controller.calcular_custo_total_plano(variaveis_decisao)

    def configurar_tema_escuro(self):
        """Configura o tema escuro da aplicação"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
                color: #ECF0F1;
            }
            QWidget {
                background-color: #34495E;
                color: #ECF0F1;
                font-family: Arial;
                font-size: 14px;
            }
            QLabel {
                color: #ECF0F1;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
            QLineEdit, QSpinBox {
                background-color: white;
                color: black;
                border: 3px solid #34495E;
                padding: 10px;
                border-radius: 6px;
                font-size: 18px;
                font-weight: bold;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 4px solid #3498DB;
                background-color: #F8F9FA;
            }
            QTextEdit {
                background-color: #2C3E50;
                color: #ECF0F1;
                border: 2px solid #34495E;
                border-radius: 3px;
                font-family: Courier;
                font-size: 10px;
            }
            QTabWidget::pane {
                border: 2px solid #34495E;
                background-color: #ECF0F1;
            }
            QTabBar::tab {
                background-color: #34495E;
                color: #ECF0F1;
                padding: 12px 20px;
                margin-right: 2px;
                border-radius: 4px 4px 0px 0px;
                font-size: 16px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498DB;
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #34495E;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0px 5px 0px 5px;
            }
            QFrame {
                border: 1px solid #34495E;
                border-radius: 3px;
            }
        """)
    
    def configurar_empresas(self):
        """Janela de configuração inicial para múltiplas empresas"""
        dialog = SetupMultiEmpresasDialog(self)
        if dialog.exec() == QDialog.Accepted:
            if getattr(dialog, 'continue_requested', False) and getattr(dialog, 'dados_autosave', None):
                self.carregou_autosave = True
                self.dados_carregados = dialog.dados_autosave
                self.nomes_empresas = dialog.nomes_empresas
                self.equipes_empresas = dialog.equipes_empresas
                self.ultimo_arquivo_salvo = getattr(dialog, 'caminho_json_selecionado', None)
            else:
                self.carregou_autosave = False
                self.dados_carregados = None
                self.nomes_empresas = dialog.nomes_empresas
                self.equipes_empresas = dialog.equipes_empresas
                self.ultimo_arquivo_salvo = None
        else:
            sys.exit()
    
    def criar_interface(self):
        """Cria a interface principal"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal (margens menores)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Header com informações gerais
        self.criar_header_geral(main_layout)
        
        # Tab widget principal para empresas + ranking
        self.tab_principal = QTabWidget()
        main_layout.addWidget(self.tab_principal)
        
        # Aba de ranking
        self.criar_aba_ranking()
        
        # Criar abas para cada empresa
        for nome_empresa in self.nomes_empresas:
            self.criar_aba_empresa(nome_empresa)
        
        # Footer
        self.criar_footer(main_layout)
    
    def criar_header_geral(self, parent_layout):
        """Cria o cabeçalho geral da aplicação (compacto)"""
        header_frame = QFrame()
        header_frame.setMaximumHeight(40)  # Altura máxima muito pequena
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #34495E;
                border: 1px solid #2C3E50;
                border-radius: 3px;
                padding: 2px;
            }
        """)
        
        # Layout horizontal para economizar espaço
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(5, 2, 5, 2)
        header_layout.setSpacing(10)
        
        # Título compacto à esquerda
        title_label = QLabel("🏭 PLANEJADOR OTIMIZADO")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #ECF0F1;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()  # Espaço no meio
        
        # Status compacto à direita
        subtitle_label = QLabel(f"🎯 {self.iteracao_atual}/{self.max_iteracoes} • {len(self.nomes_empresas)} Empresas")
        subtitle_label.setStyleSheet("font-size: 18px; color: #BDC3C7; font-weight: bold;")
        header_layout.addWidget(subtitle_label)
        
        # Armazenar referência para atualizar depois
        self.label_iteracao_geral = subtitle_label
        
        parent_layout.addWidget(header_frame)
    
    def criar_aba_ranking(self):
        """Cria a aba de ranking das empresas"""
        ranking_widget = QWidget()
        ranking_layout = QVBoxLayout(ranking_widget)
        
        # Título
        titulo = QLabel("🏆 RANKING DE EMPRESAS")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #F39C12; padding: 20px;")
        ranking_layout.addWidget(titulo)
        
        # Área principal com gráficos à esquerda e classificação à direita
        conteudo_layout = QHBoxLayout()
        conteudo_layout.setContentsMargins(12, 12, 12, 12)
        conteudo_layout.setSpacing(18)
        ranking_layout.addLayout(conteudo_layout)

        graficos_frame = QFrame()
        graficos_frame.setObjectName("rankingChartsFrame")
        graficos_frame.setStyleSheet("QFrame#rankingChartsFrame { background-color: #223140; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.06); }")
        graficos_layout = QVBoxLayout(graficos_frame)
        graficos_layout.setContentsMargins(10, 10, 10, 10)
        graficos_layout.setSpacing(10)
        graficos_layout.addWidget(self.criar_graficos_ranking())

        classificacao_frame = QFrame()
        classificacao_frame.setObjectName("rankingClassFrame")
        classificacao_frame.setStyleSheet("QFrame#rankingClassFrame { background-color: #1B2935; border-radius: 12px; border: 1px solid rgba(243, 156, 18, 0.25); }")
        classificacao_layout = QVBoxLayout(classificacao_frame)
        classificacao_layout.setContentsMargins(14, 14, 14, 14)
        classificacao_layout.setSpacing(12)
        classificacao_layout.addWidget(self.criar_tabela_ranking())

        conteudo_layout.addWidget(graficos_frame)
        conteudo_layout.addWidget(classificacao_frame)
        conteudo_layout.setStretch(0, 2)
        conteudo_layout.setStretch(1, 1)
        
        self.tab_principal.addTab(ranking_widget, "🏆 RANKING")
    
    def criar_aba_empresa(self, nome_empresa):
        """Cria uma aba para uma empresa específica com sub-abas"""
        empresa_widget = QWidget()
        empresa_layout = QVBoxLayout(empresa_widget)
        
        # Header da empresa
        self.criar_header_empresa(empresa_layout, nome_empresa)
        
        # Criar sub-abas para organizar melhor a interface
        sub_tabs = QTabWidget()
        sub_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #34495E;
                background-color: #2C3E50;
            }
            QTabBar::tab {
                background-color: #34495E;
                color: #ECF0F1;
                padding: 8px 15px;
                margin-right: 1px;
                border-radius: 4px 4px 0px 0px;
                font-weight: bold;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background-color: #3498DB;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #2980B9;
            }
        """)
        
        # Inicializar dicionário para armazenar as sub-abas
        if not hasattr(self, 'sub_tabs_empresas'):
            self.sub_tabs_empresas = {}
        self.sub_tabs_empresas[nome_empresa] = sub_tabs
        
        # Aba 1: Planejamento e Variáveis de Decisão
        self.criar_aba_producao(sub_tabs, nome_empresa)
        
        # Aba 2: Análise e Validação de Restrições
        self.criar_aba_validacao(sub_tabs, nome_empresa)
        
        # Aba 3: Violações de Restrições (aparece após iteração)
        self.criar_aba_violacoes(sub_tabs, nome_empresa)
        
        # Aba 4: Função Objetivo
        self.criar_aba_funcao_objetivo(sub_tabs, nome_empresa)
        
        # Aba 5: Gráficos e Análise
        self.criar_aba_graficos(sub_tabs, nome_empresa)
        
        empresa_layout.addWidget(sub_tabs)
        
        # Adicionar aba principal
        emoji_empresa = ["🔥", "⚡", "🚀", "💎", "🌟"][self.tab_principal.count() % 5]
        nome_curto = nome_empresa[:12] + "..." if len(nome_empresa) > 12 else nome_empresa
        self.tab_principal.addTab(empresa_widget, f"{emoji_empresa} {nome_curto}")
    
    def criar_aba_producao(self, sub_tabs, nome_empresa):
        """Cria a aba de planejamento de produção"""
        producao_widget = QWidget()
        producao_layout = QVBoxLayout(producao_widget)
        producao_layout.setContentsMargins(6, 6, 6, 6)
        producao_layout.setSpacing(6)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)

        painel_esquerdo = QWidget()
        layout_esquerdo = QVBoxLayout(painel_esquerdo)
        layout_esquerdo.setContentsMargins(8, 8, 8, 8)
        layout_esquerdo.setSpacing(12)

        titulo_principal = QLabel(f"📘 PLANEJAMENTO DE PRODUÇÃO - {nome_empresa}")
        titulo_principal.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        titulo_principal.setStyleSheet("font-size: 24px; font-weight: 800; color: #F5F6FA; padding: 4px 6px;")
        layout_esquerdo.addWidget(titulo_principal)

        self.criar_painel_variaveis_decisao(layout_esquerdo, nome_empresa)
        layout_esquerdo.addStretch()

        splitter.addWidget(painel_esquerdo)

        painel_direito = QWidget()
        painel_direito_layout = QVBoxLayout(painel_direito)
        painel_direito_layout.setContentsMargins(8, 8, 8, 8)
        painel_direito_layout.setSpacing(12)

        self.criar_painel_recursos_compacto(painel_direito_layout, nome_empresa)
        painel_direito_layout.addStretch()

        splitter.addWidget(painel_direito)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        producao_layout.addWidget(splitter)
        sub_tabs.addTab(producao_widget, "📊 Planejamento")
        
    def _obter_texto_custo_unitario_constante(self, recurso):
        """Retorna texto com o custo unitário fixo por produto para cada recurso."""
        unidades_recurso = {
            "dinheiro": "por unidade produzida",
            "materia_prima": "un. por unidade",
            "energia": "un. por unidade",
            "trabalhadores": "colab. por unidade"
        }
        custo_unitario = self.custos_unitarios_recursos.get(recurso)
        if custo_unitario is None:
            return "💸 Custo unitário do recurso: —"

        sufixo = unidades_recurso.get(recurso, '')
        if recurso == "dinheiro":
            descricao = "por dólar planejado"
        elif sufixo:
            descricao = f"por {sufixo}"
        else:
            descricao = "por unidade"

        return (
            "💸 Custo unitário do recurso: $"
            f"{custo_unitario:,.2f} {descricao}"
        )

    def criar_painel_recursos_compacto(self, parent_layout, nome_empresa):
        """Cria painel compacto de recursos com alto contraste e indicadores claros"""
        recursos_group = QGroupBox("⚡ RECURSOS DISPONÍVEIS")
        recursos_group.setStyleSheet("""
            QGroupBox {
                font-size: 20px;
                font-weight: 800;
                margin-top: 12px;
                padding: 18px;
                border: 2px solid #1ABC9C;
                border-radius: 12px;
                background-color: #14202B;
                color: #F5F6FA;
            }
            QGroupBox::title {
                color: #1ABC9C;
                padding: 4px 10px;
            }
        """)

        recursos_layout = QVBoxLayout(recursos_group)
        recursos_layout.setContentsMargins(14, 14, 14, 14)
        recursos_layout.setSpacing(16)

        recursos_disponiveis = self.empresas[nome_empresa]['recursos_disponiveis']
        variaveis_decisao = self.empresas[nome_empresa]['variaveis_decisao']

        cores_acento = {
            "dinheiro": "#1ABC9C",
            "materia_prima": "#E67E22",
            "energia": "#F39C12",
            "trabalhadores": "#9B59B6"
        }
        emoji_recurso = {"dinheiro": "💰", "materia_prima": "📦", "energia": "⚡", "trabalhadores": "👥"}
        nomes_recursos = {"dinheiro": "Dinheiro", "materia_prima": "Matéria-prima", "energia": "Energia", "trabalhadores": "Equipe"}
        mapeamento_custo = {
            'materia_prima': 'custo_materia',
            'energia': 'custo_energia',
            'trabalhadores': 'custo_trabalhadores'
        }

        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        if not hasattr(self, 'labels_recursos_compacto_empresas'):
            self.labels_recursos_compacto_empresas = {}
        self.labels_recursos_compacto_empresas[nome_empresa] = {}

        for indice, (recurso, disponivel) in enumerate(recursos_disponiveis.items()):
            usado = 0
            if recurso == "dinheiro":
                for produto, quantidade in variaveis_decisao.items():
                    if quantidade > 0:
                        usado += self.calcular_custo_financeiro_produto(produto, quantidade)
            else:
                chave_custo = mapeamento_custo.get(recurso)
                if chave_custo:
                    for produto, quantidade in variaveis_decisao.items():
                        if quantidade > 0 and chave_custo in self.produtos[produto]:
                            usado += quantidade * self.produtos[produto][chave_custo]

            restante = disponivel - usado

            card = QFrame()
            card.setObjectName("cardRecurso")
            card.setStyleSheet(f"""
                QFrame#cardRecurso {{
                    background-color: #0F1822;
                    border-radius: 14px;
                    border: 2px solid {cores_acento[recurso]};
                }}
            """)
            card.setMinimumWidth(360)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 18, 18, 18)
            card_layout.setSpacing(16)

            header_layout = QHBoxLayout()
            header_layout.setSpacing(10)

            emoji_label = QLabel(emoji_recurso[recurso])
            emoji_label.setStyleSheet("font-size: 30px;")

            nome_label = QLabel(nomes_recursos[recurso])
            nome_label.setStyleSheet("font-size: 18px; font-weight: 800; color: #F5F6FA;")

            status_label = QLabel("✅ OK")
            status_label.setAlignment(Qt.AlignCenter)
            status_label.setStyleSheet("font-size: 13px; font-weight: bold; padding: 6px 12px; border-radius: 12px; background-color: rgba(39,174,96,0.18); color: #2ECC71;")

            header_layout.addWidget(emoji_label)
            header_layout.addWidget(nome_label)
            header_layout.addStretch()
            header_layout.addWidget(status_label)
            card_layout.addLayout(header_layout)

            consumo_label = QLabel("CONSUMO ATUAL")
            consumo_label.setStyleSheet("font-size: 11px; letter-spacing: 2px; font-weight: bold; color: rgba(245,246,250,0.6);")
            consumo_label.setAlignment(Qt.AlignLeft)
            card_layout.addWidget(consumo_label)

            progress_bar = QProgressBar()
            progress_bar.setMinimum(0)
            progress_bar.setMaximum(100)
            progress_bar.setFixedHeight(26)
            progress_bar.setAlignment(Qt.AlignCenter)
            progress_bar.setTextVisible(True)

            if disponivel > 0:
                percentual_usado = min(100, (usado / disponivel) * 100)
            else:
                percentual_usado = 0

            progress_bar.setValue(int(percentual_usado))
            if recurso == "dinheiro":
                progress_format = f"${usado:,} / ${disponivel:,}  •  %p%"
            else:
                progress_format = f"{usado:,} / {disponivel:,}  •  %p%"
            progress_bar.setFormat(progress_format)
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #070C12;
                    border-radius: 9px;
                    border: 2px solid {cores_acento[recurso]};
                    color: #F5F6FA;
                    font-weight: bold;
                    font-size: 12px;
                }}
                QProgressBar::chunk {{
                    background-color: {cores_acento[recurso]};
                    border-radius: 9px;
                }}
            """)
            card_layout.addWidget(progress_bar)

            unitario_texto = self._obter_texto_custo_unitario_constante(recurso)

            unitario_label = QLabel(unitario_texto)
            unitario_label.setStyleSheet("font-size: 12px; color: #B4C3CE;")
            card_layout.addWidget(unitario_label)

            row = indice // 2
            col = indice % 2
            grid_layout.addWidget(card, row, col)

            self.labels_recursos_compacto_empresas[nome_empresa][recurso] = {
                'progress': progress_bar,
                'status': status_label,
                'card': card,
                'accent': cores_acento[recurso],
                'unitario': unitario_label,
                'unitario_texto': unitario_texto
            }

        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        recursos_layout.addLayout(grid_layout)

        instrucoes_label = QLabel("💡 Ajuste as quantidades de produção para ver o impacto direto nos recursos e no status de cada indicador. O cartão de dinheiro considera o custo financeiro estimado do plano.")
        instrucoes_label.setWordWrap(True)
        instrucoes_label.setStyleSheet("font-size: 14px; color: #A8B0BA; background-color: rgba(255,255,255,0.06); border-radius: 8px; padding: 12px; border: 1px solid rgba(255,255,255,0.08);")
        recursos_layout.addWidget(instrucoes_label)

        parent_layout.addWidget(recursos_group)
    
    def criar_aba_validacao(self, sub_tabs, nome_empresa):
        """Cria a aba de validação de restrições"""
        validacao_widget = QWidget()
        validacao_layout = QVBoxLayout(validacao_widget)
        
        # Título
        titulo = QLabel(f"⚖️ VALIDAÇÃO DE RESTRIÇÕES - {nome_empresa}")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #F39C12; padding: 20px;")
        validacao_layout.addWidget(titulo)
        
        # Botões de navegação no topo
        nav_layout = QHBoxLayout()
        btn_voltar = QPushButton("⬅️ Voltar para Planejamento")
        btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        btn_voltar.clicked.connect(lambda: self.navegar_para_aba(nome_empresa, 0))  # Aba 0 = Planejamento
        
        nav_layout.addWidget(btn_voltar)
        nav_layout.addStretch()
        validacao_layout.addLayout(nav_layout)
        
        # Área principal para validação expandida
        self.criar_area_validacao_expandida(validacao_layout, nome_empresa)
        
        sub_tabs.addTab(validacao_widget, "⚖️ Validação")
    
    def criar_area_validacao_expandida(self, parent_layout, nome_empresa):
        """Cria área expandida para validação de restrições"""
        # Scroll area para a validação
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #34495E;
                border-radius: 8px;
                background-color: #2C3E50;
            }
        """)
        
        # Widget interno do scroll
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        
        # Armazenar referência do layout de validação para atualizações
        self.widgets_validacao_empresas[nome_empresa]['layout'] = scroll_layout
        
        # Análise detalhada de restrições
        self.criar_analise_detalhada_restricoes(scroll_layout, nome_empresa)
        
        scroll_area.setWidget(scroll_widget)
        parent_layout.addWidget(scroll_area)
    
    def criar_aba_violacoes(self, sub_tabs, nome_empresa):
        """Cria aba específica para violações de restrições"""
        violacoes_widget = QWidget()
        violacoes_layout = QVBoxLayout(violacoes_widget)
        
        # Título
        titulo = QLabel(f"🚨 VIOLAÇÕES DE RESTRIÇÕES - {nome_empresa}")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #E74C3C; padding: 15px;")
        violacoes_layout.addWidget(titulo)
        
        # Área de texto grande para violações
        violacoes_text = QTextEdit()
        violacoes_text.setStyleSheet("""
            QTextEdit {
                font-size: 13px;
                font-family: 'Courier New';
                background-color: #2C3E50;
                color: #ECF0F1;
                border: 2px solid #E74C3C;
                border-radius: 8px;
                padding: 15px;
                line-height: 1.5;
            }
        """)
        violacoes_text.setPlainText("⏳ Análise de violações será exibida após executar a iteração.\n\n💡 Configure as quantidades de produção na aba 'Planejamento' e execute a iteração para ver se há violações de restrições.\n\n🎯 Objetivo: Encontrar um plano de produção que respeite todas as restrições de recursos!")
        violacoes_text.setReadOnly(True)
        
        # Armazenar referência para atualização
        if not hasattr(self, 'paineis_violacoes_empresas'):
            self.paineis_violacoes_empresas = {}
        self.paineis_violacoes_empresas[nome_empresa] = violacoes_text
        
        violacoes_layout.addWidget(violacoes_text)
        
        sub_tabs.addTab(violacoes_widget, "🚨 Violações")
        
    def criar_aba_funcao_objetivo(self, sub_tabs, nome_empresa):
        """Cria aba específica para função objetivo"""
        objetivo_widget = QWidget()
        objetivo_layout = QVBoxLayout(objetivo_widget)
        
        # Título
        titulo = QLabel(f"🎯 FUNÇÃO OBJETIVO - {nome_empresa}")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #27AE60; padding: 15px;")
        objetivo_layout.addWidget(titulo)
        
        # Criar análise da função objetivo
        self.criar_analise_funcao_objetivo(objetivo_layout, nome_empresa)
        
        sub_tabs.addTab(objetivo_widget, "🎯 Função Objetivo")
    
    def criar_analise_detalhada_restricoes(self, parent_layout, nome_empresa):
        """Cria análise detalhada das restrições com resumo do plano"""

        def formatar_valor(valor, eh_dinheiro=False):
            return f"${valor:,}" if eh_dinheiro else f"{valor:,}"

        titulo_analise = QLabel("📊 ANÁLISE DETALHADA DAS RESTRIÇÕES")
        titulo_analise.setAlignment(Qt.AlignCenter)
        titulo_analise.setStyleSheet("font-size: 24px; font-weight: bold; color: #3498DB; padding: 20px;")
        parent_layout.addWidget(titulo_analise)

        recursos_disponiveis = self.empresas[nome_empresa]['recursos_disponiveis']
        variaveis_decisao = self.empresas[nome_empresa]['variaveis_decisao']

        mapeamento_custo = {
            'materia_prima': 'custo_materia',
            'energia': 'custo_energia',
            'trabalhadores': 'custo_trabalhadores'
        }

        emoji_recurso = {"dinheiro": "💰", "materia_prima": "📦", "energia": "⚡", "trabalhadores": "👥"}
        nomes_legiveis = {"dinheiro": "Dinheiro", "materia_prima": "Matéria-prima", "energia": "Energia", "trabalhadores": "Equipe"}

        analises_recursos = []
        plano_viavel = True

        for recurso, disponivel in recursos_disponiveis.items():
            chave_custo = mapeamento_custo.get(recurso)
            if recurso != "dinheiro" and not chave_custo:
                continue

            detalhes = []
            consumo_total = 0

            for produto, quantidade in variaveis_decisao.items():
                if quantidade <= 0:
                    continue

                dados_produto = self.produtos.get(produto, {})
                if recurso == "dinheiro":
                    custo_unitario = dados_produto.get('custo_dinheiro', 0)
                    if custo_unitario == 0:
                        continue
                    consumo = custo_unitario * quantidade
                    detalhes.append({
                        'produto': produto,
                        'quantidade': quantidade,
                        'custo_unitario': custo_unitario,
                        'total': consumo,
                        'eh_dinheiro': True
                    })
                else:
                    if chave_custo not in dados_produto:
                        continue
                    custo_unitario = dados_produto[chave_custo]
                    consumo = custo_unitario * quantidade
                    detalhes.append({
                        'produto': produto,
                        'quantidade': quantidade,
                        'custo_unitario': custo_unitario,
                        'total': consumo,
                        'eh_dinheiro': False
                    })

                consumo_total += consumo

            restante = disponivel - consumo_total
            if restante < 0:
                plano_viavel = False

            analises_recursos.append({
                'id': recurso,
                'nome': nomes_legiveis.get(recurso, recurso.title()),
                'emoji': emoji_recurso.get(recurso, '📦'),
                'disponivel': disponivel,
                'consumo': consumo_total,
                'restante': restante,
                'detalhes': detalhes,
                'eh_dinheiro': recurso == "dinheiro"
            })

        receita_total = sum(self.produtos[produto]['preco_venda'] * quantidade
                            for produto, quantidade in variaveis_decisao.items() if quantidade > 0)
        custo_total = self.calcular_custo_total_plano(variaveis_decisao)
        lucro_total = receita_total - custo_total

        resumo_frame = QFrame()
        resumo_frame.setStyleSheet("""
            QFrame {
                background-color: #1F2A36;
                border-radius: 12px;
                border: 2px solid #3498DB;
                padding: 18px;
                margin: 10px 0;
            }
        """)
        resumo_layout = QVBoxLayout(resumo_frame)

        status_label = QLabel("✅ PLANO VIÁVEL" if plano_viavel else "🚨 RESTRIÇÕES VIOLADAS")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet(
            "font-size: 18px; font-weight: 800; "
            + ("color: #2ECC71;" if plano_viavel else "color: #E74C3C;")
        )
        resumo_layout.addWidget(status_label)

        indicadores_label = QLabel(
            f"💰 Receita Estimada: ${receita_total:,}\n"
            f"💸 Custo Estimado: ${custo_total:,}\n"
            f"📈 Lucro Projetado: ${lucro_total:,}"
        )
        indicadores_label.setAlignment(Qt.AlignCenter)
        indicadores_label.setStyleSheet("font-size: 14px; color: #ECF0F1; margin-top: 6px;")
        resumo_layout.addWidget(indicadores_label)

        chips_layout = QGridLayout()
        chips_layout.setContentsMargins(0, 12, 0, 0)
        chips_layout.setHorizontalSpacing(12)
        chips_layout.setVerticalSpacing(8)

        for idx, analise in enumerate(analises_recursos):
            chip = QLabel(
                f"{analise['emoji']} {analise['nome']}: "
                f"{formatar_valor(analise['restante'], analise['eh_dinheiro'])} restante"
            )
            cor_chip = "#27AE60" if analise['restante'] >= 0 else "#E74C3C"
            chip.setStyleSheet(
                "font-size: 12px; font-weight: bold; color: white; padding: 6px 10px; "
                f"border-radius: 10px; background-color: {cor_chip};"
            )
            chips_layout.addWidget(chip, idx // 2, idx % 2)

        resumo_layout.addLayout(chips_layout)
        parent_layout.addWidget(resumo_frame)

        for analise in analises_recursos:
            recurso_group = QGroupBox(f"{analise['emoji']} {analise['nome']} — Detalhes")
            recurso_group.setStyleSheet("""
                QGroupBox {
                    font-size: 18px;
                    font-weight: bold;
                    margin-top: 20px;
                    padding-top: 25px;
                    border: 3px solid #34495E;
                    border-radius: 10px;
                    background-color: #2C3E50;
                }
                QGroupBox::title {
                    color: #F39C12;
                    font-size: 20px;
                }
            """)
            recurso_layout = QVBoxLayout(recurso_group)

            info_frame = QFrame()
            info_frame.setStyleSheet("""
                QFrame {
                    background-color: #34495E;
                    border-radius: 6px;
                    padding: 15px;
                    margin: 5px;
                }
            """)
            info_layout = QGridLayout(info_frame)
            info_layout.setHorizontalSpacing(15)
            info_layout.setVerticalSpacing(8)

            disponivel_label = QLabel(
                f"Disponível: {formatar_valor(analise['disponivel'], analise['eh_dinheiro'])}"
            )
            disponivel_label.setStyleSheet("font-size: 16px; color: #3498DB; font-weight: bold;")
            info_layout.addWidget(disponivel_label, 0, 0)

            consumo_label = QLabel(
                f"Usado: {formatar_valor(analise['consumo'], analise['eh_dinheiro'])}"
            )
            consumo_label.setStyleSheet("font-size: 16px; color: #F39C12; font-weight: bold;")
            info_layout.addWidget(consumo_label, 0, 1)

            restante_label = QLabel(
                f"Restante: {formatar_valor(analise['restante'], analise['eh_dinheiro'])}"
            )
            cor_restante = "#27AE60" if analise['restante'] >= 0 else "#E74C3C"
            restante_label.setStyleSheet(
                f"font-size: 16px; color: {cor_restante}; font-weight: bold;"
            )
            info_layout.addWidget(restante_label, 1, 0, 1, 2)

            if analise['restante'] < 0:
                sugestao = (
                    f"Necessário reduzir {formatar_valor(abs(analise['restante']), analise['eh_dinheiro'])}"
                    f" para respeitar a restrição."
                )
                alerta_label = QLabel(f"⚠️ {sugestao}")
                alerta_label.setStyleSheet(
                    "font-size: 14px; color: #FFFFFF; font-weight: bold; "
                    "background-color: rgba(231, 76, 60, 0.35); padding: 6px; border-radius: 6px;"
                )
                info_layout.addWidget(alerta_label, 2, 0, 1, 2)

            recurso_layout.addWidget(info_frame)

            if analise['detalhes']:
                produtos_frame = QFrame()
                produtos_frame.setStyleSheet("""
                    QFrame {
                        background-color: #2C3E50;
                        border-radius: 6px;
                        padding: 10px;
                        margin: 5px;
                        border: 1px solid #34495E;
                    }
                """)
                produtos_layout = QVBoxLayout(produtos_frame)

                produtos_titulo = QLabel("📊 Consumo por Produto:")
                produtos_titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #ECF0F1; margin-bottom: 8px;")
                produtos_layout.addWidget(produtos_titulo)

                for detalhe in analise['detalhes']:
                    if detalhe['eh_dinheiro']:
                        texto = (
                            f"  • {detalhe['produto']}: {detalhe['quantidade']} unidades × "
                            f"${detalhe['custo_unitario']:,} = ${detalhe['total']:,}"
                        )
                    else:
                        texto = (
                            f"  • {detalhe['produto']}: {detalhe['quantidade']} unidades × "
                            f"{detalhe['custo_unitario']:,} = {detalhe['total']:,}"
                        )

                    produto_info = QLabel(texto)
                    produto_info.setStyleSheet("font-size: 14px; color: #BDC3C7; margin: 3px;")
                    produtos_layout.addWidget(produto_info)

                recurso_layout.addWidget(produtos_frame)
            else:
                nenhum_label = QLabel("Nenhum produto consome este recurso no plano atual.")
                nenhum_label.setStyleSheet("font-size: 13px; color: #95A5A6; font-style: italic; padding-left: 6px;")
                recurso_layout.addWidget(nenhum_label)

            parent_layout.addWidget(recurso_group)

    def criar_analise_funcao_objetivo(self, parent_layout, nome_empresa):
        """Cria uma visão compacta da função objetivo com resumo, tabela e histórico."""
        objetivo_group = QGroupBox("🎯 Função Objetivo")
        objetivo_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                margin-top: 18px;
                padding-top: 18px;
                border: 1px solid #27AE60;
                border-radius: 10px;
                background-color: #22303C;
            }
            QGroupBox::title {
                color: #27AE60;
                font-size: 18px;
            }
        """)

        objetivo_layout = QVBoxLayout(objetivo_group)
        objetivo_layout.setContentsMargins(16, 16, 16, 16)
        objetivo_layout.setSpacing(14)

        if not hasattr(self, 'paineis_objetivo_empresas'):
            self.paineis_objetivo_empresas = {}

        # Resumo compacto das métricas principais
        resumo_frame = QFrame()
        resumo_frame.setStyleSheet("""
            QFrame {
                background-color: #1B262F;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
            QLabel#metricTitulo {
                font-size: 12px;
                font-weight: 500;
                color: #AEB6BF;
            }
            QLabel#metricValor {
                font-size: 18px;
                font-weight: 700;
                color: #ECF0F1;
            }
        """)
        resumo_layout = QGridLayout(resumo_frame)
        resumo_layout.setContentsMargins(12, 10, 12, 10)
        resumo_layout.setHorizontalSpacing(24)
        resumo_layout.setVerticalSpacing(8)

        metric_labels = {}
        metricas_config = [
            ("Receita projetada", "receita"),
            ("Custos estimados", "custo"),
            ("Lucro projetado", "lucro"),
            ("Margem", "margem"),
        ]

        for idx, (titulo, chave) in enumerate(metricas_config):
            titulo_label = QLabel(titulo)
            titulo_label.setObjectName("metricTitulo")
            valor_label = QLabel("--")
            valor_label.setObjectName("metricValor")

            linha = idx // 2
            coluna = idx % 2
            resumo_layout.addWidget(titulo_label, linha * 2, coluna)
            resumo_layout.addWidget(valor_label, linha * 2 + 1, coluna)

            metric_labels[chave] = valor_label

        objetivo_layout.addWidget(resumo_frame)

        # Tabela de produtos
        tabela = QTableWidget()
        tabela.setColumnCount(5)
        tabela.setHorizontalHeaderLabels(["Produto", "Qtd", "Receita", "Custo", "Lucro"])
        tabela.verticalHeader().setVisible(False)
        tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabela.setSelectionMode(QAbstractItemView.NoSelection)
        tabela.setFocusPolicy(Qt.NoFocus)
        tabela.setAlternatingRowColors(True)
        tabela.setStyleSheet("""
            QTableWidget {
                background-color: #1F2A36;
                alternate-background-color: #243240;
                color: #ECF0F1;
                gridline-color: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #2C3E50;
                color: #ECF0F1;
                padding: 6px;
                border: none;
                font-size: 12px;
                font-weight: 600;
            }
        """)
        tabela.horizontalHeader().setStretchLastSection(True)
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabela.setMaximumHeight(160)
        objetivo_layout.addWidget(tabela)

        # Gráfico histórico
        grafico_frame = QFrame()
        grafico_frame.setStyleSheet("""
            QFrame {
                background-color: #1B262F;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)
        grafico_layout = QVBoxLayout(grafico_frame)
        grafico_layout.setContentsMargins(12, 12, 12, 12)
        grafico_layout.setSpacing(8)

        grafico_titulo = QLabel("Histórico por iteração")
        grafico_titulo.setStyleSheet("font-size: 13px; font-weight: 600; color: #AEB6BF;")
        grafico_layout.addWidget(grafico_titulo)

        fig = Figure(figsize=(5.5, 2.4), facecolor='#1B262F')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1B262F')
        ax.tick_params(colors='#D0D3D4')
        for spine in ax.spines.values():
            spine.set_color('#2ECC71')
        fig.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.2)

        canvas = FigureCanvas(fig)
        grafico_layout.addWidget(canvas)
        objetivo_layout.addWidget(grafico_frame)

        self.paineis_objetivo_empresas[nome_empresa] = {
            'resumo_labels': metric_labels,
            'tabela_produtos': tabela,
            'fig': fig,
            'ax': ax,
            'canvas': canvas,
        }

        self.atualizar_funcao_objetivo(nome_empresa)

        parent_layout.addWidget(objetivo_group)
    
    def criar_aba_ordens_ativas(self, sub_tabs, nome_empresa):
        """Cria a aba dedicada para visualizar ordens ativas"""
        ordens_widget = QWidget()
        ordens_layout = QVBoxLayout(ordens_widget)
        
        # Título
        titulo = QLabel(f"📋 ORDENS DE PRODUÇÃO ATIVAS - {nome_empresa}")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #F39C12; padding: 15px;")
        ordens_layout.addWidget(titulo)
        
        # Botões de navegação no topo
        nav_layout = QHBoxLayout()
        btn_voltar = QPushButton("⬅️ Voltar para Produção")
        btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        btn_voltar.clicked.connect(lambda: self.navegar_para_aba(nome_empresa, 0))  # Aba 0 = Produção
        
        btn_executar = QPushButton("⚡ EXECUTAR TURNO")
        btn_executar.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        btn_executar.clicked.connect(self.executar_turno)
        
        nav_layout.addWidget(btn_voltar)
        nav_layout.addStretch()
        nav_layout.addWidget(btn_executar)
        ordens_layout.addLayout(nav_layout)
        
        # Área principal para mostrar ordens (muito maior)
        self.criar_area_ordens_expandida(ordens_layout, nome_empresa)
        
        sub_tabs.addTab(ordens_widget, "📋 Ordens Ativas")
    
    def criar_aba_simulacao(self, sub_tabs, nome_empresa):
        """Cria a aba dedicada para simulações"""
        sim_widget = QWidget()
        sim_layout = QVBoxLayout(sim_widget)
        
        # Título
        titulo = QLabel(f"🔬 SIMULAÇÃO - {nome_empresa}")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #9B59B6; padding: 15px;")
        sim_layout.addWidget(titulo)
        
        # Botão de navegação
        nav_layout = QHBoxLayout()
        btn_voltar = QPushButton("⬅️ Voltar para Produção")
        btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        btn_voltar.clicked.connect(lambda: self.navegar_para_aba(nome_empresa, 0))  # Aba 0 = Produção
        
        nav_layout.addWidget(btn_voltar)
        nav_layout.addStretch()
        sim_layout.addLayout(nav_layout)
        
        # Área de simulação expandida
        self.criar_area_simulacao_expandida(sim_layout, nome_empresa)
        
        sub_tabs.addTab(sim_widget, "🔬 Simulação")
    
    def criar_aba_graficos(self, sub_tabs, nome_empresa):
        """Cria a aba de gráficos e análise"""
        graficos_widget = QWidget()
        graficos_layout = QVBoxLayout(graficos_widget)
        
        # Título
        titulo = QLabel(f"📊 ANÁLISE E GRÁFICOS - {nome_empresa}")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #27AE60; padding: 15px;")
        graficos_layout.addWidget(titulo)
        
        # Criar gráficos (reutilizar método existente)
        self.criar_painel_graficos_empresa_full(graficos_layout, nome_empresa)
        
        sub_tabs.addTab(graficos_widget, "📊 Análise")
    
    def criar_painel_variaveis_decisao(self, parent_container, nome_empresa):
        """Cria o painel de variáveis de decisão com sliders (otimizado)"""
        # Container principal mais compacto (sem scroll)
        variaveis_widget = QWidget()
        variaveis_layout = QVBoxLayout(variaveis_widget)
        variaveis_layout.setContentsMargins(8, 5, 8, 5)
        variaveis_layout.setSpacing(8)
        
        # Título do painel compacto
        titulo = QLabel(f"🎛️ VARIÁVEIS DE DECISÃO")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #F39C12; padding: 8px;")
        variaveis_layout.addWidget(titulo)
        
        # Criar sliders para cada produto (direto, sem grupos extras)
        sliders_group = QGroupBox("📊 QUANTIDADES A PRODUZIR")
        sliders_group.setStyleSheet("""
            QGroupBox { 
                font-size: 16px; 
                font-weight: bold;
                margin-top: 12px; 
                padding-top: 18px;
                border: 3px solid #3498DB;
                border-radius: 8px;
                background-color: #2C3E50;
            }
            QGroupBox::title {
                color: #3498DB;
                font-size: 18px;
            }
        """)
        sliders_layout = QVBoxLayout(sliders_group)
        
        # Inicializar dicionários
        if not hasattr(self, 'sliders_decisao_empresas'):
            self.sliders_decisao_empresas = {}
        if not hasattr(self, 'spinboxes_decisao_empresas'):
            self.spinboxes_decisao_empresas = {}
        if not hasattr(self, 'labels_valores_empresas'):
            self.labels_valores_empresas = {}
        
        self.sliders_decisao_empresas[nome_empresa] = {}
        self.spinboxes_decisao_empresas[nome_empresa] = {}
        self.labels_valores_empresas[nome_empresa] = {}
        
        # Criar slider compacto para cada produto
        for produto, dados in self.produtos.items():
            self.criar_slider_produto_compacto(sliders_layout, produto, dados, nome_empresa)
        
        variaveis_layout.addWidget(sliders_group)
        variaveis_layout.addStretch()  # Para empurrar tudo para cima
        
        # Adicionar ao container (pode ser splitter ou layout)
        if hasattr(parent_container, 'addWidget'):
            parent_container.addWidget(variaveis_widget)
        else:
            # Se for splitter
            parent_container.addWidget(variaveis_widget)
            
    def criar_slider_produto_compacto(self, parent_layout, produto, dados, nome_empresa):
        """Cria um slider compacto para ajustar a quantidade de um produto"""
        produto_frame = QFrame()
        produto_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {dados['cor']};
                border-radius: 6px;
                padding: 6px;
                margin: 2px;
                border: 1px solid #2C3E50;
            }}
        """)
        produto_layout = QVBoxLayout(produto_frame)
        produto_layout.setSpacing(3)
        produto_layout.setContentsMargins(5, 3, 5, 3)
        
        # Cabeçalho compacto do produto
        header_layout = QHBoxLayout()
        produto_label = QLabel(f"{dados['emoji']} {produto}")
        produto_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        header_layout.addWidget(produto_label)
        header_layout.addStretch()
        
        # Preço mais compacto
        preco_label = QLabel(f"${dados['preco_venda']}")
        preco_label.setStyleSheet("font-size: 14px; color: white; font-weight: bold;")
        header_layout.addWidget(preco_label)
        produto_layout.addLayout(header_layout)
        
        # Layout horizontal para controles
        controles_layout = QHBoxLayout()
        controles_layout.setSpacing(5)
        
        # SpinBox compacto
        quantidade_atual = self.empresas[nome_empresa]['variaveis_decisao'][produto]
        spinbox = QSpinBox()
        spinbox.setRange(0, 10000)
        spinbox.setValue(quantidade_atual)
        spinbox.setMaximumWidth(80)  # Aumentado de 60 para 80
        spinbox.setMinimumHeight(35)  # Altura mínima para melhor visibilidade
        spinbox.setStyleSheet("""
            QSpinBox {
                background-color: white;
                color: black;
                border: 3px solid #2C3E50;
                border-radius: 5px;
                padding: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QSpinBox::up-button {
                background-color: #3498DB;
                border: 2px solid #2980B9;
                border-radius: 3px;
                width: 20px;
                height: 15px;
            }
            QSpinBox::up-button:hover {
                background-color: #2980B9;
            }
            QSpinBox::down-button {
                background-color: #3498DB;
                border: 2px solid #2980B9;
                border-radius: 3px;
                width: 20px;
                height: 15px;
            }
            QSpinBox::down-button:hover {
                background-color: #2980B9;
            }
            QSpinBox::up-arrow {
                image: none;
                border: 3px solid black;
                border-left-color: transparent;
                border-right-color: transparent;
                border-bottom-color: transparent;
                width: 0px;
                height: 0px;
            }
            QSpinBox::down-arrow {
                image: none;
                border: 3px solid black;
                border-left-color: transparent;
                border-right-color: transparent;
                border-top-color: transparent;
                width: 0px;
                height: 0px;
            }
        """)
        
        # Slider compacto
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 5000)
        slider.setValue(quantidade_atual)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                border: 1px solid #5c5c5c;
                width: 12px;
                margin: -2px 0;
                border-radius: 6px;
            }
        """)
        
        # Label do valor atual
        valor_label = QLabel(f"{quantidade_atual}")
        valor_label.setStyleSheet("font-size: 18px; color: white; font-weight: bold; min-width: 50px; background-color: rgba(0,0,0,0.3); border-radius: 4px; padding: 4px;")
        valor_label.setAlignment(Qt.AlignCenter)
        
        # Conectar controles
        def sync_from_spinbox(value):
            if value <= slider.maximum():
                slider.setValue(value)
            self.atualizar_variavel_decisao(produto, nome_empresa, value, valor_label)
            
        def sync_from_slider(value):
            spinbox.setValue(value)
            self.atualizar_variavel_decisao(produto, nome_empresa, value, valor_label)
        
        spinbox.valueChanged.connect(sync_from_spinbox)
        slider.valueChanged.connect(sync_from_slider)
        
        controles_layout.addWidget(spinbox)
        controles_layout.addWidget(slider)
        controles_layout.addWidget(valor_label)
        produto_layout.addLayout(controles_layout)
        
        # Armazenar referências
        self.sliders_decisao_empresas[nome_empresa][produto] = slider
        self.spinboxes_decisao_empresas[nome_empresa][produto] = spinbox
        self.labels_valores_empresas[nome_empresa][produto] = valor_label
        
        parent_layout.addWidget(produto_frame)
    
    def criar_slider_produto(self, parent_layout, produto, dados, nome_empresa):
        """Cria um slider para ajustar a quantidade de um produto"""
        produto_frame = QFrame()
        produto_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {dados['cor']};
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
                border: 2px solid #2C3E50;
            }}
            QLabel {{
                color: white;
                font-weight: bold;
            }}
        """)
        produto_layout = QVBoxLayout(produto_frame)
        produto_layout.setSpacing(10)
        
        # Cabeçalho do produto
        header_layout = QHBoxLayout()
        produto_label = QLabel(f"{dados['emoji']} {produto}")
        produto_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(produto_label)
        header_layout.addStretch()
        produto_layout.addLayout(header_layout)
        
        # Informações de custo
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"📦 {dados['custo_materia']}"))
        info_layout.addWidget(QLabel(f"⚡ {dados['custo_energia']}"))
        info_layout.addWidget(QLabel(f"👥 {dados['custo_trabalhadores']}"))
        info_layout.addWidget(QLabel(f"💰 ${dados['preco_venda']}"))
        
        for i in range(info_layout.count()):
            widget = info_layout.itemAt(i).widget()
            if widget:
                widget.setStyleSheet("font-size: 10px; color: #E8E8E8;")
        
        produto_layout.addLayout(info_layout)
        
        # Slider e entrada manual para quantidade
        slider_layout = QHBoxLayout()
        
        quantidade_label = QLabel("Quantidade:")
        quantidade_label.setStyleSheet("font-size: 12px;")
        
        # SpinBox para entrada manual (sem limitação rígida)
        spinbox = QSpinBox()
        spinbox.setMinimum(0)
        spinbox.setMaximum(999999)  # Muito alto para permitir extrapolação
        spinbox.setValue(self.empresas[nome_empresa]['variaveis_decisao'][produto])
        spinbox.setMinimumHeight(40)  # Altura mínima aumentada
        spinbox.setStyleSheet("""
            QSpinBox {
                background-color: white;
                color: black;
                border: 3px solid #5D6D7E;
                border-radius: 6px;
                padding: 8px;
                font-size: 18px;
                font-weight: bold;
                min-width: 80px;
            }
            QSpinBox:focus {
                border: 4px solid #3498DB;
                background-color: #F8F9FA;
            }
            QSpinBox::up-button {
                background-color: #27AE60;
                border: 2px solid #229954;
                border-radius: 4px;
                width: 25px;
                height: 18px;
            }
            QSpinBox::up-button:hover {
                background-color: #229954;
            }
            QSpinBox::down-button {
                background-color: #E74C3C;
                border: 2px solid #C0392B;
                border-radius: 4px;
                width: 25px;
                height: 18px;
            }
            QSpinBox::down-button:hover {
                background-color: #C0392B;
            }
            QSpinBox::up-arrow {
                image: none;
                border: 4px solid white;
                border-left-color: transparent;
                border-right-color: transparent;
                border-bottom-color: transparent;
                width: 0px;
                height: 0px;
            }
            QSpinBox::down-arrow {
                image: none;
                border: 4px solid white;
                border-left-color: transparent;
                border-right-color: transparent;
                border-top-color: transparent;
                width: 0px;
                height: 0px;
            }
        """)
        
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(2000)  # Aumentado para permitir mais extrapolação
        slider.setValue(self.empresas[nome_empresa]['variaveis_decisao'][produto])
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #2C3E50;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #ECF0F1;
            }
        """)
        
        valor_label = QLabel(f"{slider.value()}")
        valor_label.setStyleSheet("font-size: 20px; font-weight: bold; min-width: 60px; color: white; background-color: rgba(0,0,0,0.4); border-radius: 5px; padding: 6px;")
        valor_label.setAlignment(Qt.AlignCenter)
        
        # Conectar ambos para sincronização
        def sync_from_spinbox(value):
            if value <= slider.maximum():
                slider.setValue(value)
            self.atualizar_variavel_decisao(produto, nome_empresa, value, valor_label)
            
        def sync_from_slider(value):
            spinbox.setValue(value)
            self.atualizar_variavel_decisao(produto, nome_empresa, value, valor_label)
        
        spinbox.valueChanged.connect(sync_from_spinbox)
        slider.valueChanged.connect(sync_from_slider)
        
        slider_layout.addWidget(quantidade_label)
        slider_layout.addWidget(spinbox)  # SpinBox primeiro
        slider_layout.addWidget(slider)
        slider_layout.addWidget(valor_label)
        produto_layout.addLayout(slider_layout)
        
        # Armazenar referências (incluir spinbox)
        self.sliders_decisao_empresas[nome_empresa][produto] = slider
        self.spinboxes_decisao_empresas[nome_empresa][produto] = spinbox
        self.labels_valores_empresas[nome_empresa][produto] = valor_label
        self.labels_valores_empresas[nome_empresa][produto] = valor_label
        
        parent_layout.addWidget(produto_frame)
    
    def atualizar_variavel_decisao(self, produto, nome_empresa, valor, label):
        """Atualiza uma variável de decisão"""
        # Atualizar valor na estrutura de dados
        self.empresas[nome_empresa]['variaveis_decisao'][produto] = valor
        
        # Atualizar label
        label.setText(f"{valor}")
        
        # Atualizar apenas a função objetivo em tempo real (para mostrar receita projetada)
        self.atualizar_funcao_objetivo(nome_empresa)
        
        # NÃO atualizar restrições em tempo real - só após iteração
    
    def criar_painel_analise_restricoes(self, parent_layout, nome_empresa):
        """Cria painel para análise de restrições e recursos"""
        # Status das restrições
        restricoes_group = QGroupBox("⚖️ ANÁLISE DE RESTRIÇÕES")
        restricoes_group.setStyleSheet("""
            QGroupBox { 
                font-size: 14px; 
                font-weight: bold;
                margin-top: 10px; 
                padding-top: 20px;
                border: 2px solid #34495E;
                border-radius: 8px;
                background-color: #2C3E50;
            }
            QGroupBox::title {
                color: #F39C12;
            }
        """)
        restricoes_layout = QVBoxLayout(restricoes_group)
        
        # Container para análise de recursos
        # Criar análise de recursos que será mostrada apenas após iteração
        recursos_info = QLabel("📊 A análise de recursos será exibida após executar a iteração")
        recursos_info.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #F39C12;
                background-color: #34495E;
                border: 1px solid #F39C12;
                border-radius: 5px;
                padding: 15px;
                margin: 10px;
                text-align: center;
            }
        """)
        recursos_info.setAlignment(Qt.AlignCenter)
        restricoes_layout.addWidget(recursos_info)
        
        # Placeholder para análise de recursos (será preenchido após iteração)
        recursos_scroll = QScrollArea()
        recursos_scroll.setWidgetResizable(True)
        recursos_scroll.setMaximumHeight(300)
        recursos_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        recursos_widget = QWidget()
        recursos_layout = QVBoxLayout(recursos_widget)
        recursos_scroll.setWidget(recursos_widget)
        
        # Armazenar referência para atualização após iteração
        if not hasattr(self, 'paineis_recursos_empresas'):
            self.paineis_recursos_empresas = {}
        self.paineis_recursos_empresas[nome_empresa] = recursos_layout
        
        restricoes_layout.addWidget(recursos_scroll)
        
        # Container para violações de restrições
        violacoes_group = QGroupBox("🚨 VIOLAÇÕES DE RESTRIÇÕES")
        violacoes_group.setStyleSheet("""
            QGroupBox { 
                font-size: 12px; 
                font-weight: bold;
                margin-top: 10px; 
                padding-top: 15px;
                border: 2px solid #E74C3C;
                border-radius: 8px;
                background-color: #2C3E50;
            }
            QGroupBox::title {
                color: #E74C3C;
            }
        """)
        violacoes_layout = QVBoxLayout(violacoes_group)
        
        # Área de texto para mostrar violações (específica para cada empresa)
        violacoes_text = QTextEdit()
        violacoes_text.setMaximumHeight(150)
        violacoes_text.setStyleSheet("""
            QTextEdit {
                font-size: 11px;
                font-family: 'Courier New';
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #E74C3C;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        violacoes_text.setPlainText("⏳ Análise de violações será exibida após executar a iteração.\n\n💡 Configure as quantidades de produção e execute a iteração para ver se há violações de restrições.")
        violacoes_layout.addWidget(violacoes_text)
        
        restricoes_layout.addWidget(violacoes_group)
        
        # Armazenar referência para atualizações
        if not hasattr(self, 'paineis_restricoes_empresas'):
            self.paineis_restricoes_empresas = {}
        self.paineis_restricoes_empresas[nome_empresa] = {
            'violacoes_text': violacoes_text,
            'restricoes_group': restricoes_group
        }
        
        parent_layout.addWidget(restricoes_group)
        
        # Função objetivo
        objetivo_group = QGroupBox("🎯 FUNÇÃO OBJETIVO")
        objetivo_group.setStyleSheet("""
            QGroupBox { 
                font-size: 12px; 
                font-weight: bold;
                margin-top: 10px; 
                padding-top: 15px;
                border: 2px solid #27AE60;
                border-radius: 8px;
                background-color: #2C3E50;
            }
            QGroupBox::title {
                color: #27AE60;
            }
        """)
        objetivo_layout = QVBoxLayout(objetivo_group)
        
        self.objetivo_label = QLabel("Receita Total: $0")
        self.objetivo_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #27AE60; padding: 10px;")
        self.objetivo_label.setAlignment(Qt.AlignCenter)
        objetivo_layout.addWidget(self.objetivo_label)
        
        self.margem_label = QLabel("Margem de Lucro: 0%")
        self.margem_label.setStyleSheet("font-size: 12px; color: #F39C12; padding: 5px;")
        self.margem_label.setAlignment(Qt.AlignCenter)
        objetivo_layout.addWidget(self.margem_label)
        
        parent_layout.addWidget(objetivo_group)
        parent_layout.addStretch()
    
    def criar_analise_recursos(self, parent_layout, nome_empresa):
        """Cria análise detalhada do uso de recursos"""
        recursos_container = QWidget()
        recursos_layout = QVBoxLayout(recursos_container)
        
        emoji_recurso = {"dinheiro": "💰", "materia_prima": "📦", 
                        "energia": "⚡", "trabalhadores": "👥"}
        
        # Calcular uso de recursos baseado nas variáveis de decisão
        recursos_disponiveis = self.empresas[nome_empresa]['recursos_disponiveis']
        variaveis_decisao = self.empresas[nome_empresa]['variaveis_decisao']
        
        for recurso, disponivel in recursos_disponiveis.items():
            # Calcular consumo total do recurso
            consumo_total = 0
            for produto, quantidade in variaveis_decisao.items():
                if quantidade > 0:
                    if recurso == "dinheiro":
                        consumo_total += self.calcular_custo_financeiro_produto(produto, quantidade)
                    else:
                        consumo_total += self.produtos[produto][f'custo_{recurso}'] * quantidade
            
            # Frame para cada recurso
            recurso_frame = QFrame()
            recurso_frame.setStyleSheet("""
                QFrame {
                    background-color: #34495E;
                    border-radius: 6px;
                    padding: 10px;
                    margin: 3px;
                    border: 1px solid #2C3E50;
                }
            """)
            recurso_layout = QVBoxLayout(recurso_frame)
            
            # Nome do recurso
            nome_recurso = QLabel(f"{emoji_recurso[recurso]} {recurso.replace('_', ' ').title()}")
            nome_recurso.setStyleSheet("font-size: 13px; font-weight: bold; color: #ECF0F1;")
            recurso_layout.addWidget(nome_recurso)
            
            # Análise de uso
            restante = disponivel - consumo_total
            percentual_uso = (consumo_total / disponivel * 100) if disponivel > 0 else 0
            
            uso_layout = QHBoxLayout()
            
            if recurso == "dinheiro":
                disponivel_label = QLabel(f"Disponível: ${disponivel:,}")
                usado_label = QLabel(f"Usado: ${consumo_total:,}")
                restante_label = QLabel(f"Restante: ${restante:,}")
            else:
                disponivel_label = QLabel(f"Disponível: {disponivel:,}")
                usado_label = QLabel(f"Usado: {consumo_total:,}")
                restante_label = QLabel(f"Restante: {restante:,}")
            disponivel_label.setStyleSheet("font-size: 11px; color: #3498DB;")
            usado_label.setStyleSheet("font-size: 11px; color: #F39C12;")
            cor_restante = "#27AE60" if restante >= 0 else "#E74C3C"
            restante_label.setStyleSheet(f"font-size: 11px; color: {cor_restante}; font-weight: bold;")
            
            uso_layout.addWidget(disponivel_label)
            uso_layout.addWidget(usado_label)
            uso_layout.addWidget(restante_label)
            recurso_layout.addLayout(uso_layout)
            
            # Barra de progresso visual
            progress_layout = QHBoxLayout()
            progress_label = QLabel(f"Uso: {percentual_uso:.1f}%")
            progress_label.setStyleSheet("font-size: 10px; color: #BDC3C7;")
            progress_layout.addWidget(progress_label)
            recurso_layout.addLayout(progress_layout)
            
            # Aviso se exceder limite
            if restante < 0:
                aviso_label = QLabel(f"⚠️ EXCESSO: {abs(restante):,}")
                aviso_label.setStyleSheet("font-size: 10px; color: #E74C3C; font-weight: bold; background-color: rgba(231, 76, 60, 0.2); padding: 3px; border-radius: 3px;")
                recurso_layout.addWidget(aviso_label)
            
            recursos_layout.addWidget(recurso_frame)
        
        # Cálculo da receita total
        receita_total = 0
        for produto, quantidade in variaveis_decisao.items():
            if quantidade > 0:
                receita_total += self.produtos[produto]['preco_venda'] * quantidade
        
        receita_frame = QFrame()
        receita_frame.setStyleSheet("""
            QFrame {
                background-color: #27AE60;
                border-radius: 6px;
                padding: 10px;
                margin: 3px;
                border: 1px solid #2C3E50;
            }
        """)
        receita_layout = QVBoxLayout(receita_frame)
        
        receita_titulo = QLabel("💰 RESUMO FINANCEIRO DO PLANO")
        receita_titulo.setStyleSheet("font-size: 12px; font-weight: bold; color: white;")
        receita_layout.addWidget(receita_titulo)
        
        custo_total = self.calcular_custo_total_plano(variaveis_decisao)
        lucro_total = receita_total - custo_total

        receita_valor = QLabel(f"Receita: ${receita_total:,}")
        receita_valor.setStyleSheet("font-size: 12px; font-weight: bold; color: white;")
        receita_layout.addWidget(receita_valor)

        custo_label = QLabel(f"Custo: ${custo_total:,}")
        custo_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #FAD7A0;")
        receita_layout.addWidget(custo_label)

        lucro_label = QLabel(f"Lucro Estimado: ${lucro_total:,}")
        lucro_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2ECC71;")
        receita_layout.addWidget(lucro_label)
        
        recursos_layout.addWidget(receita_frame)
        parent_layout.addWidget(recursos_container)
    
    def atualizar_analise_restricoes(self, nome_empresa):
        """Atualiza a análise de restrições após a iteração"""
        # Atualizar o painel de violações na aba dedicada "Violações"
        if hasattr(self, 'paineis_violacoes_empresas') and nome_empresa in self.paineis_violacoes_empresas:
            violacoes_text_dedicado = self.paineis_violacoes_empresas[nome_empresa]
            self._atualizar_texto_violacoes_detalhado(violacoes_text_dedicado, nome_empresa)
        
        # Atualizar a aba de validação detalhada após iteração
        if hasattr(self, 'widgets_validacao_empresas') and nome_empresa in self.widgets_validacao_empresas:
            if 'layout' in self.widgets_validacao_empresas[nome_empresa]:
                layout_validacao = self.widgets_validacao_empresas[nome_empresa]['layout']
                self.recriar_analise_detalhada_restricoes(layout_validacao, nome_empresa)
            
    def recriar_analise_detalhada_restricoes(self, parent_layout, nome_empresa):
        """Recria a análise detalhada de restrições com valores atualizados"""
        # Limpar widgets existentes do layout
        while parent_layout.count():
            child = parent_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Recriar a análise com valores atuais
        self.criar_analise_detalhada_restricoes(parent_layout, nome_empresa)
            
    def atualizar_analise_recursos_dinamica(self, nome_empresa):
        """Atualiza dinamicamente a análise de recursos"""
        if not hasattr(self, 'paineis_recursos_empresas') or nome_empresa not in self.paineis_recursos_empresas:
            return
            
        recursos_layout = self.paineis_recursos_empresas[nome_empresa]
        
        # Limpar layout anterior
        while recursos_layout.count():
            child = recursos_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Recriar análise atualizada
        emoji_recurso = {"dinheiro": "💰", "materia_prima": "📦", 
                        "energia": "⚡", "trabalhadores": "👥"}
        
        # Calcular uso de recursos baseado nas variáveis de decisão
        recursos_disponiveis = self.empresas[nome_empresa]['recursos_disponiveis']
        variaveis_decisao = self.empresas[nome_empresa]['variaveis_decisao']
        
        mapeamento_custo = {
            'materia_prima': 'custo_materia',
            'energia': 'custo_energia', 
            'trabalhadores': 'custo_trabalhadores'
        }
        
        for recurso, disponivel in recursos_disponiveis.items():
            # Calcular consumo total do recurso
            consumo_total = 0
            for produto, quantidade in variaveis_decisao.items():
                if quantidade > 0:
                    if recurso == "dinheiro":
                        consumo_total += self.calcular_custo_financeiro_produto(produto, quantidade)
                    else:
                        chave_custo = mapeamento_custo.get(recurso)
                        if not chave_custo:
                            continue
                        consumo_total += self.produtos[produto][chave_custo] * quantidade
            
            # Frame para cada recurso
            recurso_frame = QFrame()
            recurso_frame.setStyleSheet("""
                QFrame {
                    background-color: #34495E;
                    border-radius: 6px;
                    padding: 10px;
                    margin: 3px;
                    border: 1px solid #2C3E50;
                }
            """)
            recurso_frame_layout = QVBoxLayout(recurso_frame)
            
            # Nome do recurso
            nome_recurso = QLabel(f"{emoji_recurso[recurso]} {recurso.replace('_', ' ').title()}")
            nome_recurso.setStyleSheet("font-size: 13px; font-weight: bold; color: #ECF0F1;")
            recurso_frame_layout.addWidget(nome_recurso)
            
            # Análise de uso
            restante = disponivel - consumo_total
            percentual_uso = (consumo_total / disponivel * 100) if disponivel > 0 else 0
            
            uso_layout = QHBoxLayout()
            
            if recurso == "dinheiro":
                disponivel_label = QLabel(f"Disponível: ${disponivel:,}")
                usado_label = QLabel(f"Usado: ${consumo_total:,}")
                restante_label = QLabel(f"Restante: ${restante:,}")
            else:
                disponivel_label = QLabel(f"Disponível: {disponivel:,}")
                usado_label = QLabel(f"Usado: {consumo_total:,}")
                restante_label = QLabel(f"Restante: {restante:,}")
            disponivel_label.setStyleSheet("font-size: 11px; color: #3498DB;")
            usado_label.setStyleSheet("font-size: 11px; color: #F39C12;")
            cor_restante = "#27AE60" if restante >= 0 else "#E74C3C"
            restante_label.setStyleSheet(f"font-size: 11px; color: {cor_restante}; font-weight: bold;")
            
            uso_layout.addWidget(disponivel_label)
            uso_layout.addWidget(usado_label)
            uso_layout.addWidget(restante_label)
            recurso_frame_layout.addLayout(uso_layout)
            
            # Barra de progresso visual
            progress_layout = QHBoxLayout()
            progress_label = QLabel(f"Uso: {percentual_uso:.1f}%")
            progress_label.setStyleSheet("font-size: 10px; color: #BDC3C7;")
            progress_layout.addWidget(progress_label)
            recurso_frame_layout.addLayout(progress_layout)
            
            # Aviso se exceder limite
            if restante < 0:
                aviso_label = QLabel(f"⚠️ EXCESSO: {abs(restante):,}")
                aviso_label.setStyleSheet("font-size: 10px; color: #E74C3C; font-weight: bold; background-color: rgba(231, 76, 60, 0.2); padding: 3px; border-radius: 3px;")
                recurso_frame_layout.addWidget(aviso_label)
            
            recursos_layout.addWidget(recurso_frame)
        
        # Cálculo da receita total
        receita_total = 0
        for produto, quantidade in variaveis_decisao.items():
            if quantidade > 0:
                receita_total += self.produtos[produto]['preco_venda'] * quantidade
        
        receita_frame = QFrame()
        receita_frame.setStyleSheet("""
            QFrame {
                background-color: #27AE60;
                border-radius: 6px;
                padding: 10px;
                margin: 3px;
                border: 1px solid #2C3E50;
            }
        """)
        receita_frame_layout = QVBoxLayout(receita_frame)
        
        receita_titulo = QLabel("💰 RESUMO FINANCEIRO DO PLANO")
        receita_titulo.setStyleSheet("font-size: 12px; font-weight: bold; color: white;")
        receita_frame_layout.addWidget(receita_titulo)
        
        custo_total = self.calcular_custo_total_plano(variaveis_decisao)
        lucro_total = receita_total - custo_total

        receita_valor = QLabel(f"Receita: ${receita_total:,}")
        receita_valor.setStyleSheet("font-size: 12px; font-weight: bold; color: white;")
        receita_frame_layout.addWidget(receita_valor)

        custo_label = QLabel(f"Custo: ${custo_total:,}")
        custo_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #FAD7A0;")
        receita_frame_layout.addWidget(custo_label)

        lucro_label = QLabel(f"Lucro Estimado: ${lucro_total:,}")
        lucro_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2ECC71;")
        receita_frame_layout.addWidget(lucro_label)
        
        recursos_layout.addWidget(receita_frame)
    
    def verificar_violacoes_restricoes(self, nome_empresa):
        """Verifica violações de restrições para uma empresa"""
        # Atualizar apenas o painel de violações na aba dedicada "Violações"
        if hasattr(self, 'paineis_violacoes_empresas') and nome_empresa in self.paineis_violacoes_empresas:
            violacoes_text_dedicado = self.paineis_violacoes_empresas[nome_empresa]
            self._atualizar_texto_violacoes_detalhado(violacoes_text_dedicado, nome_empresa)
            
    def _atualizar_texto_violacoes_detalhado(self, violacoes_text, nome_empresa):
        """Atualiza texto detalhado de violações para a aba dedicada"""
        historico = self.empresas[nome_empresa]['historico_iteracoes']

        if not historico:
            violacoes_text.setPlainText(
                "⏳ Ainda não houve iterações para gerar o relatório de violações.\n"
                "Execute uma iteração para ver o detalhamento acumulado."
            )
            return

        texto_detalhado = "📊 RELATÓRIO ACUMULADO DE RESTRIÇÕES POR ITERAÇÃO\n"
        texto_detalhado += "=" * 70 + "\n\n"

        historico_ordenado = sorted(historico, key=lambda item: item.get('iteracao', 0))

        for registro in historico_ordenado:
            iteracao = registro.get('iteracao', 0)
            receita_total = registro.get('receita_total', 0)
            custo_total = registro.get('custo_total', 0)
            violacoes_iteracao = registro.get('violacoes', []) or []
            resumo_recursos = registro.get('resumo_recursos', {}) or {}

            texto_detalhado += f"ITERACAO {iteracao}\n"
            texto_detalhado += "-" * 60 + "\n"

            texto_detalhado += (
                f"💰 Receita Estimada: ${receita_total:,}\n"
                f"💸 Custo Estimado: ${custo_total:,}\n"
                f"📈 Lucro Projetado: ${receita_total - custo_total:,}\n"
            )

            if violacoes_iteracao:
                texto_detalhado += "🚨 Violações detectadas:\n"
                for violacao in violacoes_iteracao:
                    texto_detalhado += f"   {violacao}\n"
            else:
                texto_detalhado += "✅ Nenhuma violação registrada nesta iteração.\n"

            texto_detalhado += "\n"

            if resumo_recursos:
                for recurso_id, dados in resumo_recursos.items():
                    nome = dados.get('nome', recurso_id.replace('_', ' ').title())
                    emoji = dados.get('emoji', '📦')
                    disponivel = dados.get('disponivel', 0)
                    consumo = dados.get('consumo', 0)
                    restante = dados.get('restante', disponivel - consumo)
                    eh_dinheiro = dados.get('eh_dinheiro', False)
                    violacao = dados.get('violacao', False)
                    faltante = dados.get('faltante', max(0, consumo - disponivel))
                    detalhes = dados.get('detalhes', []) or []

                    fmt_val = (lambda v: f"${v:,}" if eh_dinheiro else f"{v:,}")

                    texto_detalhado += f"{emoji} {nome.upper()}\n"
                    texto_detalhado += f"   💼 Disponível: {fmt_val(disponivel)}\n"
                    texto_detalhado += f"   📊 Consumido: {fmt_val(consumo)}\n"
                    texto_detalhado += f"   📦 Restante: {fmt_val(restante)}\n"

                    if detalhes:
                        texto_detalhado += "   🔧 Consumo por produto:\n"
                        for item in detalhes:
                            texto_detalhado += (
                                f"      • {item.get('produto')} : {item.get('quantidade')} × "
                                f"{fmt_val(item.get('custo_unitario', 0))} = {fmt_val(item.get('total', 0))}\n"
                            )

                    if violacao:
                        if eh_dinheiro:
                            texto_detalhado += f"   ❌ VIOLAÇÃO: Necessário +{fmt_val(faltante)}\n"
                            texto_detalhado += f"      🔧 Ajuste: Reduza custos em {fmt_val(faltante)}\n"
                        else:
                            texto_detalhado += f"   ❌ VIOLAÇÃO: Excesso de {fmt_val(faltante)} unidades\n"
                            texto_detalhado += f"      🔧 Ajuste: Reduza produção em {fmt_val(faltante)} unidades\n"
                    else:
                        texto_detalhado += "   ✅ Restrição respeitada.\n"

                    texto_detalhado += "\n"
            else:
                texto_detalhado += "   (Sem dados de recursos para esta iteração.)\n\n"

        violacoes_text.setPlainText(texto_detalhado.rstrip())
        
    def atualizar_funcao_objetivo(self, nome_empresa):
        """Atualiza a análise da função objetivo em tempo real"""
        if not hasattr(self, 'paineis_objetivo_empresas'):
            self.paineis_objetivo_empresas = {}
            
        if nome_empresa not in self.paineis_objetivo_empresas:
            return
        painel = self.paineis_objetivo_empresas[nome_empresa]

        variaveis_decisao = self.empresas[nome_empresa]['variaveis_decisao']

        receita_total = 0
        custo_total = 0
        dados_produtos = []

        for produto, quantidade in variaveis_decisao.items():
            if quantidade <= 0:
                continue

            preco_venda = self.produtos[produto]['preco_venda']
            receita = preco_venda * quantidade
            custo = (
                self.produtos[produto]['custo_materia'] * quantidade +
                self.produtos[produto]['custo_energia'] * quantidade +
                self.produtos[produto]['custo_trabalhadores'] * quantidade
            )
            lucro = receita - custo

            dados_produtos.append({
                'produto': produto,
                'quantidade': quantidade,
                'receita': receita,
                'custo': custo,
                'lucro': lucro,
            })

            receita_total += receita
            custo_total += custo

        lucro_total = receita_total - custo_total
        margem_lucro = (lucro_total / receita_total * 100) if receita_total > 0 else 0

        # Atualizar métricas resumidas
        resumo_labels = painel['resumo_labels']
        resumo_labels['receita'].setText(f"${receita_total:,.0f}")
        resumo_labels['custo'].setText(f"${custo_total:,.0f}")
        resumo_labels['lucro'].setText(f"${lucro_total:,.0f}")
        resumo_labels['margem'].setText(f"{margem_lucro:.1f}%" if receita_total > 0 else "--")

        # Atualizar tabela
        tabela = painel['tabela_produtos']
        if dados_produtos:
            dados_produtos.sort(key=lambda item: item['lucro'], reverse=True)
            tabela.setRowCount(len(dados_produtos))

            for linha, dados in enumerate(dados_produtos):
                tabela.setItem(linha, 0, QTableWidgetItem(dados['produto']))

                item_qtd = QTableWidgetItem(f"{dados['quantidade']:,}")
                item_qtd.setTextAlignment(Qt.AlignCenter)
                tabela.setItem(linha, 1, item_qtd)

                item_receita = QTableWidgetItem(f"${dados['receita']:,.0f}")
                item_receita.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                tabela.setItem(linha, 2, item_receita)

                item_custo = QTableWidgetItem(f"${dados['custo']:,.0f}")
                item_custo.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                tabela.setItem(linha, 3, item_custo)

                item_lucro = QTableWidgetItem(f"${dados['lucro']:,.0f}")
                item_lucro.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if dados['lucro'] < 0:
                    item_lucro.setForeground(QColor('#E74C3C'))
                tabela.setItem(linha, 4, item_lucro)
        else:
            tabela.setRowCount(1)
            tabela.setItem(0, 0, QTableWidgetItem("Nenhum produto em produção"))
            for col in range(1, tabela.columnCount()):
                vazio = QTableWidgetItem("-")
                vazio.setTextAlignment(Qt.AlignCenter)
                tabela.setItem(0, col, vazio)

        # Atualizar gráfico
        ax = painel['ax']
        ax.clear()
        ax.set_facecolor('#1B262F')
        ax.tick_params(colors='#BDC3C7')
        for spine in ax.spines.values():
            spine.set_color('#2ECC71')

        historico = self.empresas[nome_empresa].get('historico_iteracoes', [])

        if historico:
            iteracoes = [registro.get('iteracao', idx + 1) for idx, registro in enumerate(historico)]
            receitas_hist = [registro.get('receita_total', 0) for registro in historico]
            custos_hist = [registro.get('custo_total', 0) for registro in historico]
            lucros_hist = [receita - custo for receita, custo in zip(receitas_hist, custos_hist)]

            ax.plot(iteracoes, receitas_hist, color='#2ECC71', marker='o', linewidth=1.8, label='Receita')
            ax.plot(iteracoes, custos_hist, color='#E67E22', marker='o', linewidth=1.8, label='Custos')
            ax.plot(iteracoes, lucros_hist, color='#F1C40F', marker='o', linewidth=1.8, label='Lucro')

            minimo = min(min(custos_hist), min(receitas_hist), min(lucros_hist), lucro_total)
            maximo = max(max(custos_hist), max(receitas_hist), max(lucros_hist), lucro_total)
            faixa = max(abs(minimo) * 0.1, abs(maximo) * 0.1, 1)
            ax.set_ylim(minimo - faixa, maximo + faixa)

            xticks = sorted(set(iteracoes + [self.iteracao_atual]))
            ax.set_xticks(xticks)
            ax.set_xlabel('Iteração', color='#BDC3C7')
            ax.set_ylabel('Valor ($)', color='#BDC3C7')
            ax.grid(color='#253445', linestyle='--', linewidth=0.6, alpha=0.7)

            ax.plot(self.iteracao_atual, lucro_total, marker='D', markersize=9,
                    color='#E74C3C', linestyle='None', label='Plano atual')

            legenda = ax.legend(facecolor='#1B262F', edgecolor='#2ECC71', fontsize=9)
            for text in legenda.get_texts():
                text.set_color('#ECF0F1')

            ax.set_title('Receita, custos e lucro acumulados', color='#AEB6BF', fontsize=11, pad=10)
        else:
            ax.set_title('Sem histórico ainda', color='#95A5A6', fontsize=11, pad=10)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.text(0.5, 0.5, 'Execute uma iteração para acompanhar a evolução.',
                    color='#BDC3C7', fontsize=10, ha='center', va='center')
            ax.set_xticks([])
            ax.set_yticks([])

        painel['canvas'].draw_idle()
        
    def navegar_para_aba(self, nome_empresa, indice_aba):
        """Navega para uma sub-aba específica de uma empresa"""
        if hasattr(self, 'sub_tabs_empresas') and nome_empresa in self.sub_tabs_empresas:
            self.sub_tabs_empresas[nome_empresa].setCurrentIndex(indice_aba)
    
    def executar_iteracao(self):
        """Executa uma iteração de planejamento - valida restrições e avança"""
        try:
            if self.iteracao_atual > self.max_iteracoes:
                QMessageBox.information(self, "Fim", "Planejamento finalizado!")
                return
            
            # Mapeamento de recursos para chaves de custo
            mapeamento_custo = {
                'materia_prima': 'custo_materia',
                'energia': 'custo_energia', 
                'trabalhadores': 'custo_trabalhadores'
            }
            
            # Validar restrições para todas as empresas
            relatorio_geral = f"📊 RELATÓRIO DA ITERAÇÃO {self.iteracao_atual}\n" + "="*50 + "\n"
            
            todas_empresas_viáveis = True
            
            for nome_empresa in self.nomes_empresas:
                self._garantir_estruturas_empresa(nome_empresa)
                relatorio_geral += f"\n🏢 {nome_empresa}:\n"
                
                recursos_disponiveis = self.empresas[nome_empresa]['recursos_disponiveis']
                variaveis_decisao = self.empresas[nome_empresa]['variaveis_decisao']
                
                violacoes = []
                receita_total = 0
                custo_financeiro_total = self.calcular_custo_total_plano(variaveis_decisao)
                resumo_recursos = {}
                mapa_emojis = {"dinheiro": "💰", "materia_prima": "📦", "energia": "⚡", "trabalhadores": "👥"}
                
                # Verificar restrições
                for recurso, disponivel in recursos_disponiveis.items():
                    if recurso == "dinheiro":
                        continue
                        
                    consumo_total = 0
                    detalhes_consumo = []
                    # Usar o mapeamento correto
                    chave_custo = mapeamento_custo.get(recurso)
                    if not chave_custo:
                        continue
                        
                    for produto, quantidade in variaveis_decisao.items():
                        if quantidade > 0:
                            custo_unitario = self.produtos[produto][chave_custo]
                            consumo_produto = custo_unitario * quantidade
                            consumo_total += consumo_produto
                            detalhes_consumo.append({
                                'produto': produto,
                                'quantidade': quantidade,
                                'custo_unitario': custo_unitario,
                                'total': consumo_produto,
                                'eh_dinheiro': False
                            })
                    
                    if consumo_total > disponivel:
                        excesso = consumo_total - disponivel
                        violacoes.append(f"  ❌ {recurso.replace('_', ' ').title()}: Excesso de {excesso:,}")
                        todas_empresas_viáveis = False
                    else:
                        restante = disponivel - consumo_total
                        relatorio_geral += f"  ✅ {recurso.replace('_', ' ').title()}: {restante:,} restante\n"

                    resumo_recursos[recurso] = {
                        'nome': recurso.replace('_', ' ').title(),
                        'emoji': mapa_emojis.get(recurso, '📦'),
                        'disponivel': disponivel,
                        'consumo': consumo_total,
                        'restante': disponivel - consumo_total,
                        'violacao': consumo_total > disponivel,
                        'faltante': max(0, consumo_total - disponivel),
                        'detalhes': detalhes_consumo,
                        'eh_dinheiro': False
                    }

                dinheiro_disponivel = recursos_disponiveis.get('dinheiro', 0)
                detalhes_financeiros = []
                for produto, quantidade in variaveis_decisao.items():
                    if quantidade > 0:
                        custo_unitario = self.produtos[produto].get('custo_dinheiro', 0)
                        total_custo = custo_unitario * quantidade
                        detalhes_financeiros.append({
                            'produto': produto,
                            'quantidade': quantidade,
                            'custo_unitario': custo_unitario,
                            'total': total_custo,
                            'eh_dinheiro': True
                        })
                if custo_financeiro_total > dinheiro_disponivel:
                    excesso_dinheiro = custo_financeiro_total - dinheiro_disponivel
                    violacoes.append(f"  ❌ Dinheiro: Plano excede em ${excesso_dinheiro:,}")
                    todas_empresas_viáveis = False
                else:
                    restante_dinheiro = dinheiro_disponivel - custo_financeiro_total
                    relatorio_geral += f"  ✅ Dinheiro: ${restante_dinheiro:,} após custos\n"

                resumo_recursos['dinheiro'] = {
                    'nome': 'Dinheiro',
                    'emoji': mapa_emojis.get('dinheiro', '💰'),
                    'disponivel': dinheiro_disponivel,
                    'consumo': custo_financeiro_total,
                    'restante': dinheiro_disponivel - custo_financeiro_total,
                    'violacao': custo_financeiro_total > dinheiro_disponivel,
                    'faltante': max(0, custo_financeiro_total - dinheiro_disponivel),
                    'detalhes': detalhes_financeiros,
                    'eh_dinheiro': True
                }
                
                # Calcular receita
                for produto, quantidade in variaveis_decisao.items():
                    if quantidade > 0:
                        receita_produto = self.produtos[produto]['preco_venda'] * quantidade
                        receita_total += receita_produto
                        relatorio_geral += f"  📱 {produto}: {quantidade} unidades → ${receita_produto:,}\n"
                
                if violacoes:
                    relatorio_geral += f"  🚨 VIOLAÇÕES:\n" + "\n".join(violacoes) + "\n"
                
                relatorio_geral += f"  💰 Receita Total: ${receita_total:,}\n"
                relatorio_geral += f"  💸 Custo Total: ${custo_financeiro_total:,}\n"
                relatorio_geral += f"  📈 Lucro Previsto: ${receita_total - custo_financeiro_total:,}\n"
                
                # Armazenar no histórico
                self.empresas[nome_empresa]['historico_iteracoes'].append({
                    'iteracao': self.iteracao_atual,
                    'variaveis_decisao': variaveis_decisao.copy(),
                    'receita_total': receita_total,
                    'violacoes': violacoes.copy(),
                    'custo_total': custo_financeiro_total,
                    'resumo_recursos': resumo_recursos
                })
            
            if todas_empresas_viáveis:
                relatorio_geral += f"\n✅ TODAS AS EMPRESAS ESTÃO COM PLANOS VIÁVEIS!\n"
            else:
                relatorio_geral += f"\n⚠️ ALGUMAS EMPRESAS PRECISAM AJUSTAR SEUS PLANOS!\n"
            
            # Avançar iteração
            self.iteracao_atual += 1
            
            # Atualizar interface
            self.atualizar_todas_interfaces()

            # Autosave após atualizar a interface
            self.salvar_estado_temporario()
            
            relatorio_geral += f"\n🎯 Próxima iteração: {self.iteracao_atual}\n"
            
            QMessageBox.information(self, "Iteração Executada", relatorio_geral)
            
            # Verificar fim do planejamento
            if self.iteracao_atual > self.max_iteracoes:
                self.mostrar_resultado_final_planejamento()
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao executar iteração: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def criar_painel_producao_empresa(self, nome_empresa):
        """Cria painel com informações da empresa na aba de produção"""
        # Status atual vs futuro da empresa
        status_group = QGroupBox("📊 RECURSOS: ATUAL vs FUTURO")
        status_group.setStyleSheet("""
            QGroupBox { 
                font-size: 14px; 
                font-weight: bold;
                margin-top: 10px; 
                padding-top: 20px;
                border: 2px solid #34495E;
                border-radius: 8px;
                background-color: #2C3E50;
            }
            QGroupBox::title {
                color: #F39C12;
            }
        """)
        status_layout = QVBoxLayout(status_group)
        
        # Calcular recursos futuros baseado nas ordens atuais
        recursos_atuais = self.empresas[nome_empresa]['recursos']
        recursos_futuros = recursos_atuais.copy()
        
        # Calcular consumo das ordens ativas
        producao_atual = self.empresas[nome_empresa]['producao_atual']
        consumo_total = {"materia_prima": 0, "energia": 0, "trabalhadores": 0}
        receita_esperada = 0
        custo_financeiro_total = 0
        
        for produto, quantidade in producao_atual.items():
            if quantidade > 0:
                dados_produto = self.produtos[produto]
                consumo_total["materia_prima"] += dados_produto['custo_materia'] * quantidade
                consumo_total["energia"] += dados_produto['custo_energia'] * quantidade
                consumo_total["trabalhadores"] += dados_produto['custo_trabalhadores'] * quantidade
                receita_esperada += dados_produto['preco_venda'] * quantidade
                custo_financeiro_total += self.calcular_custo_financeiro_produto(produto, quantidade)
        
        # Calcular recursos após execução das ordens
        recursos_futuros["materia_prima"] -= consumo_total["materia_prima"]
        recursos_futuros["energia"] -= consumo_total["energia"]
        recursos_futuros["trabalhadores"] -= consumo_total["trabalhadores"]
        recursos_futuros["dinheiro"] += receita_esperada - custo_financeiro_total
        
        # Container para recursos com scroll se necessário
        recursos_container = QWidget()
        recursos_layout = QVBoxLayout(recursos_container)
        
        emoji_recurso = {"dinheiro": "💰", "materia_prima": "📦", 
                        "energia": "⚡", "trabalhadores": "👥"}
        
        for recurso, valor_atual in recursos_atuais.items():
            # Frame para cada recurso
            recurso_frame = QFrame()
            recurso_frame.setStyleSheet("""
                QFrame {
                    background-color: #34495E;
                    border-radius: 6px;
                    padding: 12px;
                    margin: 5px;
                    border: 1px solid #2C3E50;
                }
            """)
            recurso_layout = QVBoxLayout(recurso_frame)
            
            # Nome do recurso
            nome_recurso = QLabel(f"{emoji_recurso[recurso]} {recurso.replace('_', ' ').title()}")
            nome_recurso.setStyleSheet("font-size: 15px; font-weight: bold; color: #ECF0F1; margin-bottom: 8px;")
            recurso_layout.addWidget(nome_recurso)
            
            # Valores atuais e futuros
            valor_futuro = recursos_futuros[recurso]
            diferenca = valor_futuro - valor_atual
            
            # Layout horizontal para atual vs futuro
            valores_layout = QHBoxLayout()
            
            # Valor atual
            atual_label = QLabel(f"Atual: {valor_atual:,}")
            atual_label.setStyleSheet("font-size: 14px; color: #3498DB; font-weight: bold;")
            
            # Seta
            seta_label = QLabel("→")
            seta_label.setStyleSheet("font-size: 18px; color: #95A5A6; font-weight: bold;")
            
            # Valor futuro com cor baseada na situação
            cor_futuro = "#27AE60" if valor_futuro >= 0 else "#E74C3C"
            if recurso != "dinheiro" and valor_futuro < 0:
                cor_futuro = "#E74C3C"
            elif recurso != "dinheiro" and valor_futuro < valor_atual * 0.2:  # Menos de 20% restante
                cor_futuro = "#F39C12"
            
            futuro_label = QLabel(f"Futuro: {valor_futuro:,}")
            futuro_label.setStyleSheet(f"font-size: 14px; color: {cor_futuro}; font-weight: bold;")
            
            valores_layout.addWidget(atual_label)
            valores_layout.addWidget(seta_label)
            valores_layout.addWidget(futuro_label)
            valores_layout.addStretch()
            
            # Mostrar diferença se há consumo/ganho
            if diferenca != 0:
                simbolo = "+" if diferenca > 0 else ""
                cor_diff = "#27AE60" if diferenca > 0 else "#E74C3C"
                diff_label = QLabel(f"({simbolo}{diferenca:,})")
                diff_label.setStyleSheet(f"font-size: 13px; color: {cor_diff}; font-style: italic; font-weight: bold;")
                valores_layout.addWidget(diff_label)
            
            recurso_layout.addLayout(valores_layout)
            
            # Aviso se recurso ficará negativo
            if valor_futuro < 0 and recurso != "dinheiro":
                aviso_label = QLabel("⚠️ RECURSO INSUFICIENTE!")
                aviso_label.setStyleSheet("font-size: 12px; color: #E74C3C; font-weight: bold; background-color: rgba(231, 76, 60, 0.2); padding: 5px; border-radius: 3px;")
                recurso_layout.addWidget(aviso_label)
            elif valor_futuro < valor_atual * 0.2 and recurso != "dinheiro" and valor_futuro >= 0:
                aviso_label = QLabel("⚠️ Recurso baixo!")
                aviso_label.setStyleSheet("font-size: 12px; color: #F39C12; font-weight: bold; background-color: rgba(243, 156, 18, 0.2); padding: 5px; border-radius: 3px;")
                recurso_layout.addWidget(aviso_label)
            
            recursos_layout.addWidget(recurso_frame)
        
        status_layout.addWidget(recursos_container)
        
        # Resumo das ordens ativas (se houver)
        total_itens = sum(producao_atual.values())
        if total_itens > 0:
            lucro_previsto = receita_esperada - custo_financeiro_total
            resumo_label = QLabel(
                f"📋 {total_itens} itens programados | 💰 Receita +${receita_esperada:,} | "
                f"💸 Custo ${custo_financeiro_total:,} | Lucro +${lucro_previsto:,}"
            )
            resumo_label.setStyleSheet("font-size: 13px; color: #F39C12; font-weight: bold; padding: 10px; background-color: rgba(52, 73, 94, 0.5); border-radius: 5px; margin: 8px;")
            resumo_label.setAlignment(Qt.AlignCenter)
            status_layout.addWidget(resumo_label)
        else:
            sem_ordens_label = QLabel("📋 Nenhuma ordem de produção programada")
            sem_ordens_label.setStyleSheet("font-size: 13px; color: #95A5A6; font-style: italic; padding: 10px; text-align: center;")
            sem_ordens_label.setAlignment(Qt.AlignCenter)
            status_layout.addWidget(sem_ordens_label)
        
        parent_layout.addWidget(status_group)
        
        # Armazenar referência para atualizações
        if not hasattr(self, 'paineis_info_empresas'):
            self.paineis_info_empresas = {}
        self.paineis_info_empresas[nome_empresa] = status_group
        
        # Informações dos produtos (com fontes maiores)
        produtos_group = QGroupBox("🏭 PRODUTOS DISPONÍVEIS")
        produtos_group.setStyleSheet("""
            QGroupBox { 
                font-size: 14px; 
                font-weight: bold;
                margin-top: 10px; 
                padding-top: 20px;
                border: 2px solid #34495E;
                border-radius: 8px;
                background-color: #2C3E50;
            }
            QGroupBox::title {
                color: #3498DB;
            }
        """)
        produtos_layout = QVBoxLayout(produtos_group)
        
        for produto, dados in self.produtos.items():
            produto_frame = QFrame()
            produto_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {dados['cor']};
                    border-radius: 8px;
                    padding: 12px;
                    margin: 5px;
                    border: 2px solid #2C3E50;
                }}
                QLabel {{
                    color: white;
                    font-weight: bold;
                }}
            """)
            produto_layout = QVBoxLayout(produto_frame)
            produto_layout.setSpacing(5)
            
            # Nome do produto (fonte maior)
            nome_label = QLabel(f"{dados['emoji']} {produto}")
            nome_label.setAlignment(Qt.AlignCenter)
            nome_label.setStyleSheet("font-size: 14px; margin-bottom: 5px;")
            produto_layout.addWidget(nome_label)
            
            # Informações principais (fonte maior e melhor contraste)
            info_label = QLabel(f"💰 ${dados['preco_venda']} | ⏱️ {dados['tempo_producao']} turnos")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("font-size: 12px; color: #FFFFFF; background-color: rgba(0,0,0,0.3); padding: 3px; border-radius: 3px;")
            produto_layout.addWidget(info_label)
            
            # Custos detalhados (fonte maior)
            custos_layout = QHBoxLayout()
            custos_items = [
                ("📦", dados['custo_materia']),
                ("⚡", dados['custo_energia']),
                ("👥", dados['custo_trabalhadores'])
            ]
            
            for emoji, valor in custos_items:
                custo_label = QLabel(f"{emoji}{valor}")
                custo_label.setAlignment(Qt.AlignCenter)
                custo_label.setStyleSheet("font-size: 11px; color: #FFFFFF; background-color: rgba(0,0,0,0.2); padding: 2px; border-radius: 2px; margin: 1px;")
                custos_layout.addWidget(custo_label)
            
            produto_layout.addLayout(custos_layout)
            produtos_layout.addWidget(produto_frame)
        
        parent_layout.addWidget(produtos_group)
        parent_layout.addStretch()
    
    def atualizar_painel_info_empresa(self, nome_empresa):
        """Atualiza o painel de informações da empresa em tempo real"""
        if not hasattr(self, 'paineis_info_empresas') or nome_empresa not in self.paineis_info_empresas:
            return
            
        # Remove o painel atual
        painel_atual = self.paineis_info_empresas[nome_empresa]
        parent_layout = painel_atual.parent().layout()
        
        # Encontrar a posição do painel atual
        posicao = -1
        for i in range(parent_layout.count()):
            if parent_layout.itemAt(i).widget() == painel_atual:
                posicao = i
                break
        
        if posicao >= 0:
            # Remove o painel antigo
            parent_layout.removeWidget(painel_atual)
            painel_atual.deleteLater()
            
            # Criar novo painel de status
            status_group = QGroupBox("📊 RECURSOS: ATUAL vs FUTURO")
            status_group.setStyleSheet("""
                QGroupBox { 
                    font-size: 14px; 
                    font-weight: bold;
                    margin-top: 10px; 
                    padding-top: 20px;
                    border: 2px solid #34495E;
                    border-radius: 8px;
                    background-color: #2C3E50;
                }
                QGroupBox::title {
                    color: #F39C12;
                }
            """)
            status_layout = QVBoxLayout(status_group)
            
            # Recalcular recursos (mesmo código do método original)
            recursos_atuais = self.empresas[nome_empresa]['recursos']
            recursos_futuros = recursos_atuais.copy()
            
            producao_atual = self.empresas[nome_empresa]['producao_atual']
            consumo_total = {"materia_prima": 0, "energia": 0, "trabalhadores": 0}
            receita_esperada = 0
            
            for produto, quantidade in producao_atual.items():
                if quantidade > 0:
                    dados_produto = self.produtos[produto]
                    consumo_total["materia_prima"] += dados_produto['custo_materia'] * quantidade
                    consumo_total["energia"] += dados_produto['custo_energia'] * quantidade
                    consumo_total["trabalhadores"] += dados_produto['custo_trabalhadores'] * quantidade
                    receita_esperada += dados_produto['preco_venda'] * quantidade
            
            recursos_futuros["materia_prima"] -= consumo_total["materia_prima"]
            recursos_futuros["energia"] -= consumo_total["energia"]
            recursos_futuros["trabalhadores"] -= consumo_total["trabalhadores"]
            recursos_futuros["dinheiro"] += receita_esperada
            
            # Recriar a interface de recursos
            recursos_container = QWidget()
            recursos_layout = QVBoxLayout(recursos_container)
            
            emoji_recurso = {"dinheiro": "💰", "materia_prima": "📦", 
                            "energia": "⚡", "trabalhadores": "👥"}
            
            for recurso, valor_atual in recursos_atuais.items():
                recurso_frame = QFrame()
                recurso_frame.setStyleSheet("""
                    QFrame {
                        background-color: #34495E;
                        border-radius: 6px;
                        padding: 10px;
                        margin: 3px;
                        border: 1px solid #2C3E50;
                    }
                """)
                recurso_layout = QVBoxLayout(recurso_frame)
                
                nome_recurso = QLabel(f"{emoji_recurso[recurso]} {recurso.replace('_', ' ').title()}")
                nome_recurso.setStyleSheet("font-size: 14px; font-weight: bold; color: #ECF0F1; margin-bottom: 5px;")
                recurso_layout.addWidget(nome_recurso)
                
                valor_futuro = recursos_futuros[recurso]
                diferenca = valor_futuro - valor_atual
                
                valores_layout = QHBoxLayout()
                
                atual_label = QLabel(f"Atual: {valor_atual}")
                atual_label.setStyleSheet("font-size: 13px; color: #3498DB; font-weight: bold;")
                
                seta_label = QLabel("→")
                seta_label.setStyleSheet("font-size: 16px; color: #95A5A6; font-weight: bold;")
                
                cor_futuro = "#27AE60" if valor_futuro >= 0 else "#E74C3C"
                if recurso != "dinheiro" and valor_futuro < 0:
                    cor_futuro = "#E74C3C"
                elif recurso != "dinheiro" and valor_futuro < valor_atual * 0.2:
                    cor_futuro = "#F39C12"
                
                futuro_label = QLabel(f"Futuro: {valor_futuro}")
                futuro_label.setStyleSheet(f"font-size: 13px; color: {cor_futuro}; font-weight: bold;")
                
                valores_layout.addWidget(atual_label)
                valores_layout.addWidget(seta_label)
                valores_layout.addWidget(futuro_label)
                valores_layout.addStretch()
                
                if diferenca != 0:
                    simbolo = "+" if diferenca > 0 else ""
                    cor_diff = "#27AE60" if diferenca > 0 else "#E74C3C"
                    diff_label = QLabel(f"({simbolo}{diferenca})")
                    diff_label.setStyleSheet(f"font-size: 12px; color: {cor_diff}; font-style: italic;")
                    valores_layout.addWidget(diff_label)
                
                recurso_layout.addLayout(valores_layout)
                
                if valor_futuro < 0 and recurso != "dinheiro":
                    aviso_label = QLabel("⚠️ RECURSO INSUFICIENTE!")
                    aviso_label.setStyleSheet("font-size: 11px; color: #E74C3C; font-weight: bold; background-color: rgba(231, 76, 60, 0.2); padding: 3px; border-radius: 3px;")
                    recurso_layout.addWidget(aviso_label)
                elif valor_futuro < valor_atual * 0.2 and recurso != "dinheiro" and valor_futuro >= 0:
                    aviso_label = QLabel("⚠️ Recurso baixo!")
                    aviso_label.setStyleSheet("font-size: 11px; color: #F39C12; font-weight: bold; background-color: rgba(243, 156, 18, 0.2); padding: 3px; border-radius: 3px;")
                    recurso_layout.addWidget(aviso_label)
                
                recursos_layout.addWidget(recurso_frame)
            
            status_layout.addWidget(recursos_container)
            
            if any(qtd > 0 for qtd in producao_atual.values()):
                resumo_label = QLabel(f"📋 {sum(producao_atual.values())} itens programados | 💰 +${receita_esperada} esperado")
                resumo_label.setStyleSheet("font-size: 12px; color: #F39C12; font-weight: bold; padding: 8px; background-color: rgba(52, 73, 94, 0.5); border-radius: 4px; margin: 5px;")
                resumo_label.setAlignment(Qt.AlignCenter)
                status_layout.addWidget(resumo_label)
            
            # Inserir o novo painel na posição correta
            parent_layout.insertWidget(posicao, status_group)
            self.paineis_info_empresas[nome_empresa] = status_group
    
    def criar_area_ordens_expandida(self, parent_layout, nome_empresa):
        """Cria área expandida para visualizar ordens de produção"""
        # Scroll area para as ordens
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #34495E;
                border-radius: 8px;
                background-color: #2C3E50;
            }
        """)
        
        # Widget interno do scroll
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(15, 15, 15, 15)
        
        # Status inicial
        status_label = QLabel("🔄 Nenhuma ordem de produção ativa")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("""
            color: #BDC3C7; 
            font-size: 14px; 
            font-style: italic;
            padding: 20px;
        """)
        scroll_layout.addWidget(status_label)
        
        scroll_area.setWidget(scroll_widget)
        parent_layout.addWidget(scroll_area)
        
        # Botões de ação
        acoes_layout = QHBoxLayout()
        
        btn_limpar = QPushButton("🗑️ Limpar Todas as Ordens")
        btn_limpar.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        btn_limpar.clicked.connect(lambda: self.limpar_ordens_producao(nome_empresa))
        
        btn_atualizar = QPushButton("🔄 Atualizar Visualização")
        btn_atualizar.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        btn_atualizar.clicked.connect(lambda: self.atualizar_display_ordens_expandida(nome_empresa))
        
        acoes_layout.addWidget(btn_limpar)
        acoes_layout.addStretch()
        acoes_layout.addWidget(btn_atualizar)
        parent_layout.addLayout(acoes_layout)
        
        # Armazenar referência
        if not hasattr(self, 'displays_ordens_expandida'):
            self.displays_ordens_expandida = {}
        self.displays_ordens_expandida[nome_empresa] = {
            'scroll_layout': scroll_layout,
            'status_label': status_label
        }
    
    def criar_area_simulacao_expandida(self, parent_layout, nome_empresa):
        """Cria área expandida para simulações"""
        # Área de resultados
        resultados_group = QGroupBox("📊 RESULTADOS DAS SIMULAÇÕES")
        resultados_group.setStyleSheet("""
            QGroupBox { 
                font-size: 14px; 
                font-weight: bold;
                margin-top: 10px; 
                padding-top: 15px;
                border: 2px solid #34495E;
                border-radius: 8px;
            }
        """)
        resultados_layout = QVBoxLayout(resultados_group)
        
        # Área de texto para resultados (muito maior)
        text_simulacao = QTextEdit()
        text_simulacao.setMinimumHeight(400)
        text_simulacao.setStyleSheet("""
            QTextEdit {
                font-size: 14px; 
                font-family: 'Courier New';
                background-color: #2C3E50;
                color: #ECF0F1;
                border: 1px solid #34495E;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        text_simulacao.setPlainText("📋 Clique em 'Simular' em qualquer produto para ver os resultados aqui...\n\n"
                                   "💡 Esta área mostrará:\n"
                                   "   • Custos detalhados de produção\n"
                                   "   • Receita esperada\n"
                                   "   • Viabilidade da produção\n"
                                   "   • Impacto nos recursos\n"
                                   "   • Análise de rentabilidade")
        
        resultados_layout.addWidget(text_simulacao)
        parent_layout.addWidget(resultados_group)
        
        # Botão para limpar simulações
        btn_limpar_sim = QPushButton("🗑️ Limpar Simulações")
        btn_limpar_sim.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        btn_limpar_sim.clicked.connect(lambda: text_simulacao.clear())
        parent_layout.addWidget(btn_limpar_sim)
        
        # Armazenar referência expandida
        if not hasattr(self, 'text_simulacao_expandida'):
            self.text_simulacao_expandida = {}
        self.text_simulacao_expandida[nome_empresa] = text_simulacao
    
    def criar_painel_graficos_empresa_full(self, parent_layout, nome_empresa):
        """Cria painel completo de gráficos para a aba dedicada"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        conteudo_widget = QWidget()
        conteudo_layout = QVBoxLayout(conteudo_widget)
        conteudo_layout.setContentsMargins(8, 8, 8, 8)
        conteudo_layout.setSpacing(18)

        self.criar_painel_graficos_empresa(conteudo_layout, nome_empresa)
        conteudo_layout.addStretch()

        scroll_area.setWidget(conteudo_widget)
        parent_layout.addWidget(scroll_area)
    
    def criar_header_empresa(self, parent_layout, nome_empresa):
        """Cria o cabeçalho específico de uma empresa (ultra compacto)"""
        header_frame = QFrame()
        header_frame.setMaximumHeight(25)  # Altura máxima muito pequena
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border: 1px solid #34495E;
                border-radius: 3px;
                padding: 1px;
                margin: 0px;
            }
        """)
        
        # Layout horizontal compacto
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(3, 1, 3, 1)
        header_layout.setSpacing(5)
        
        # Nome da empresa compacto à esquerda
        nome_curto = nome_empresa[:15] + "..." if len(nome_empresa) > 15 else nome_empresa
        title_label = QLabel(f"🏢 {nome_curto}")
        title_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #3498DB;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()  # Espaço no meio
        
        # Recursos em linha horizontal muito compactos
        recursos = self.empresas[nome_empresa]['recursos_disponiveis']
        cores_recursos = {"dinheiro": "#27AE60", "materia_prima": "#E67E22", 
                         "energia": "#F39C12", "trabalhadores": "#9B59B6"}
        
        # Armazenar labels para atualização posterior
        if not hasattr(self, 'labels_recursos_empresas'):
            self.labels_recursos_empresas = {}
        self.labels_recursos_empresas[nome_empresa] = {}
        
        for recurso, valor in recursos.items():
            # Emojis apenas para economizar espaço
            emojis = {"dinheiro": "💰", "materia_prima": "📦", 
                     "energia": "⚡", "trabalhadores": "👥"}
            
            # Formatar valores mais compactos
            if valor >= 1000:
                valor_str = f"{valor/1000:.0f}k"
            else:
                valor_str = str(valor)
                
            label = QLabel(f"{emojis[recurso]}{valor_str}")
            label.setStyleSheet(f"""
                background-color: {cores_recursos[recurso]};
                color: white;
                font-weight: bold;
                padding: 1px 3px;
                border-radius: 2px;
                margin: 0px;
                font-size: 9px;
                min-width: 30px;
                max-width: 40px;
            """)
            header_layout.addWidget(label)
            self.labels_recursos_empresas[nome_empresa][recurso] = label
        
        parent_layout.addWidget(header_frame)
    
    def criar_painel_controles_empresa(self, parent_splitter, nome_empresa):
        """Cria o painel de controles para uma empresa específica"""
        # Container principal com scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #34495E;
            }
            QScrollBar:vertical {
                background-color: #2C3E50;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3498DB;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #2980B9;
            }
        """)
        
        controles_widget = QWidget()
        controles_layout = QVBoxLayout(controles_widget)
        controles_layout.setContentsMargins(5, 5, 5, 5)
        controles_layout.setSpacing(8)
        
        # Título do painel (mais compacto)
        titulo = QLabel(f"🎮 {nome_empresa[:15]}")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 12px; font-weight: bold; color: #ECF0F1; padding: 5px;")
        controles_layout.addWidget(titulo)
        
        # Equipes da empresa (mais compactas)
        equipes = self.empresas[nome_empresa]['equipes']
        equipes_group = QGroupBox("👥 EQUIPES")
        equipes_group.setStyleSheet("QGroupBox { font-size: 10px; margin-top: 8px; padding-top: 8px; }")
        equipes_layout = QVBoxLayout(equipes_group)
        equipes_layout.setSpacing(3)
        
        cores_equipes = ["#E67E22", "#27AE60", "#F39C12"]
        for i, (tipo, nome_equipe) in enumerate(equipes.items()):
            equipe_label = QLabel(f"{tipo[:3].upper()}: {nome_equipe[:12]}")
            equipe_label.setAlignment(Qt.AlignCenter)
            equipe_label.setStyleSheet(f"""
                background-color: {cores_equipes[i % 3]};
                color: white;
                font-weight: bold;
                padding: 3px;
                border-radius: 3px;
                margin: 1px;
                font-size: 10px;
            """)
            equipes_layout.addWidget(equipe_label)
        
        controles_layout.addWidget(equipes_group)
        
        # Produção (versão compacta)
        self.criar_secao_producao_compacta(controles_layout, nome_empresa)
        
        # Simulação (mais compacta)
        sim_group = QGroupBox("🔬 SIMULAÇÃO")
        sim_group.setStyleSheet("QGroupBox { font-size: 10px; margin-top: 8px; padding-top: 8px; }")
        sim_layout = QVBoxLayout(sim_group)
        
        text_simulacao = QTextEdit()
        text_simulacao.setMaximumHeight(80)
        text_simulacao.setStyleSheet("font-size: 12px; font-family: Courier;")
        sim_layout.addWidget(text_simulacao)
        
        # Armazenar referência
        if not hasattr(self, 'text_simulacao_empresas'):
            self.text_simulacao_empresas = {}
        self.text_simulacao_empresas[nome_empresa] = text_simulacao
        
        controles_layout.addWidget(sim_group)
        controles_layout.addStretch()
        
        # Configurar scroll area
        scroll_area.setWidget(controles_widget)
        parent_splitter.addWidget(scroll_area)
    
    def criar_painel_graficos_empresa(self, parent_splitter, nome_empresa):
        """Cria o painel de análises visuais para uma empresa específica"""
        graficos_widget = QWidget()
        graficos_layout = QVBoxLayout(graficos_widget)
        graficos_layout.setContentsMargins(12, 12, 12, 12)
        graficos_layout.setSpacing(20)

        titulo = QLabel(f"📊 Análises estratégicas — {nome_empresa}")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: 700; color: #ECF0F1; padding: 6px;")
        graficos_layout.addWidget(titulo)

        # Resumo compacto de métricas
        resumo_frame = QFrame()
        resumo_frame.setStyleSheet("""
            QFrame {
                background-color: #1F2A36;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
            QLabel#metricTitulo {
                font-size: 12px;
                color: #9BA7B1;
                font-weight: 500;
            }
            QLabel#metricValor {
                font-size: 18px;
                color: #ECF0F1;
                font-weight: 700;
            }
        """)
        resumo_layout = QGridLayout(resumo_frame)
        resumo_layout.setContentsMargins(14, 10, 14, 10)
        resumo_layout.setHorizontalSpacing(32)
        resumo_layout.setVerticalSpacing(6)

        metric_labels = {}
        metric_config = [
            ("Iterações concluídas", "iteracoes"),
            ("Lucro acumulado", "lucro_total"),
            ("Viol. registradas", "violacoes"),
            ("Eficiência média", "eficiencia"),
        ]

        for idx, (titulo_metric, chave) in enumerate(metric_config):
            titulo_label = QLabel(titulo_metric)
            titulo_label.setObjectName("metricTitulo")
            valor_label = QLabel("--")
            valor_label.setObjectName("metricValor")
            linha = idx // 2
            coluna = idx % 2
            resumo_layout.addWidget(titulo_label, linha * 2, coluna)
            resumo_layout.addWidget(valor_label, linha * 2 + 1, coluna)
            metric_labels[chave] = valor_label

        graficos_layout.addWidget(resumo_frame)

        # Área principal com gráficos e classificação detalhada lado a lado
        conteudo_layout = QHBoxLayout()
        conteudo_layout.setSpacing(18)
        conteudo_layout.setContentsMargins(0, 0, 0, 0)
        graficos_layout.addLayout(conteudo_layout)

        charts_container = QFrame()
        charts_container.setObjectName("chartsContainer")
        charts_container.setStyleSheet("QFrame#chartsContainer { background-color: transparent; }")
        charts_layout = QVBoxLayout(charts_container)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(16)

        # Grade com gráficos
        charts_grid = QGridLayout()
        charts_grid.setSpacing(16)
        charts_grid.setContentsMargins(0, 0, 0, 0)
        charts_grid.setColumnStretch(0, 1)
        charts_grid.setColumnStretch(1, 1)
        charts_grid.setRowStretch(0, 1)
        charts_grid.setRowStretch(1, 1)

        def criar_quadro_grafico(titulo_texto):
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background-color: #1B242F;
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.04);
                }
            """)
            layout = QVBoxLayout(frame)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(6)
            titulo_label = QLabel(titulo_texto)
            titulo_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #AEB6BF;")
            layout.addWidget(titulo_label)
            return frame, layout

        # Gráfico financeiro
        fin_frame, fin_layout = criar_quadro_grafico("Tendência financeira por iteração")
        fig_fin = Figure(figsize=(6.2, 3.1), facecolor='#1B242F')
        ax_fin = fig_fin.add_subplot(111)
        ax_fin.set_facecolor('#1B242F')
        ax_fin.tick_params(colors='#BDC3C7')
        for spine in ax_fin.spines.values():
            spine.set_color('#2ECC71')
        fig_fin.subplots_adjust(left=0.08, right=0.97, top=0.9, bottom=0.2)
        canvas_fin = FigureCanvas(fig_fin)
        canvas_fin.setMinimumHeight(280)
        fin_layout.addWidget(canvas_fin)

        # Gráfico de recursos
        rec_frame, rec_layout = criar_quadro_grafico("Uso de recursos na última iteração")
        fig_rec = Figure(figsize=(6.2, 3.1), facecolor='#1B242F')
        ax_rec = fig_rec.add_subplot(111)
        ax_rec.set_facecolor('#1B242F')
        ax_rec.tick_params(colors='#BDC3C7')
        for spine in ax_rec.spines.values():
            spine.set_color('#3498DB')
        fig_rec.subplots_adjust(left=0.12, right=0.95, top=0.9, bottom=0.25)
        canvas_rec = FigureCanvas(fig_rec)
        canvas_rec.setMinimumHeight(280)
        rec_layout.addWidget(canvas_rec)

        # Gráfico de mix de produção
        mix_frame, mix_layout = criar_quadro_grafico("Mix de produção executado")
        fig_mix = Figure(figsize=(6.2, 3.1), facecolor='#1B242F')
        ax_mix = fig_mix.add_subplot(111)
        ax_mix.set_facecolor('#1B242F')
        fig_mix.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        canvas_mix = FigureCanvas(fig_mix)
        canvas_mix.setMinimumHeight(280)
        mix_layout.addWidget(canvas_mix)

        # Gráfico de violações
        viol_frame, viol_layout = criar_quadro_grafico("Violação de restrições por iteração")
        fig_viol = Figure(figsize=(6.2, 3.1), facecolor='#1B242F')
        ax_viol = fig_viol.add_subplot(111)
        ax_viol.set_facecolor('#1B242F')
        ax_viol.tick_params(colors='#BDC3C7')
        for spine in ax_viol.spines.values():
            spine.set_color('#E74C3C')
        fig_viol.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.2)
        canvas_viol = FigureCanvas(fig_viol)
        canvas_viol.setMinimumHeight(280)
        viol_layout.addWidget(canvas_viol)

        charts_grid.addWidget(fin_frame, 0, 0)
        charts_grid.addWidget(rec_frame, 0, 1)
        charts_grid.addWidget(mix_frame, 1, 0)
        charts_grid.addWidget(viol_frame, 1, 1)

        charts_layout.addLayout(charts_grid)
        conteudo_layout.addWidget(charts_container)

        # Coluna de classificação detalhada
        classificacao_frame = QFrame()
        classificacao_frame.setObjectName("classificacaoFrame")
        classificacao_frame.setStyleSheet("""
            QFrame#classificacaoFrame {
                background-color: #1F2F3D;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
            QLabel#classificacaoTitulo {
                font-size: 14px;
                font-weight: 600;
                color: #AEB6BF;
            }
            QLabel#classificacaoTexto {
                font-size: 12px;
                color: #D5DDE5;
                line-height: 1.4em;
            }
        """)
        classificacao_layout = QVBoxLayout(classificacao_frame)
        classificacao_layout.setContentsMargins(14, 14, 14, 14)
        classificacao_layout.setSpacing(14)

        classificacao_titulo = QLabel("🏅 Classificação detalhada")
        classificacao_titulo.setObjectName("classificacaoTitulo")
        classificacao_layout.addWidget(classificacao_titulo)

        classificacao_label = QLabel("Aguardando dados para classificar.")
        classificacao_label.setObjectName("classificacaoTexto")
        classificacao_label.setWordWrap(True)
        classificacao_label.setAlignment(Qt.AlignTop)
        classificacao_layout.addWidget(classificacao_label)

        insights_frame = QFrame()
        insights_frame.setStyleSheet("""
            QFrame {
                background-color: #192733;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
            QLabel {
                color: #D5DDE5;
                font-size: 12px;
            }
        """)
        insights_layout = QVBoxLayout(insights_frame)
        insights_layout.setContentsMargins(12, 10, 12, 10)
        insights_layout.setSpacing(6)
        insights_titulo = QLabel("📌 Insights automáticos")
        insights_titulo.setStyleSheet("font-size: 13px; font-weight: 600; color: #AEB6BF;")
        insights_label = QLabel("Aguardando dados...")
        insights_label.setWordWrap(True)
        insights_layout.addWidget(insights_titulo)
        insights_layout.addWidget(insights_label)

        classificacao_layout.addWidget(insights_frame)
        classificacao_layout.addStretch()

        conteudo_layout.addWidget(classificacao_frame)
        conteudo_layout.setStretch(0, 2)
        conteudo_layout.setStretch(1, 1)

        self.graficos_empresas[nome_empresa] = {
            'metric_labels': metric_labels,
            'finance_ax': ax_fin,
            'finance_canvas': canvas_fin,
            'recursos_ax': ax_rec,
            'recursos_canvas': canvas_rec,
            'mix_ax': ax_mix,
            'mix_canvas': canvas_mix,
            'violacoes_ax': ax_viol,
            'violacoes_canvas': canvas_viol,
            'classificacao_label': classificacao_label,
            'insights_label': insights_label,
        }

        if hasattr(parent_splitter, 'addWidget'):
            parent_splitter.addWidget(graficos_widget)
    
    def criar_secao_producao_compacta(self, parent_layout, nome_empresa):
        """Cria seção de produção compacta para empresas específicas"""
        producao_group = QGroupBox("🏭 PRODUÇÃO")
        producao_group.setStyleSheet("""
            QGroupBox { 
                font-size: 12px; 
                font-weight: bold;
                margin-top: 15px; 
                padding-top: 15px;
                border: 2px solid #34495E;
                border-radius: 8px;
            }
            QGroupBox::title {
                color: #ECF0F1;
                padding: 0px 8px;
            }
        """)
        producao_layout = QVBoxLayout(producao_group)
        producao_layout.setSpacing(10)
        producao_layout.setContentsMargins(10, 20, 10, 10)
        
        # Criar controles para cada produto
        for produto, dados in self.produtos.items():
            produto_frame = QFrame()
            produto_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {dados['cor']};
                    border-radius: 8px;
                    padding: 8px;
                    margin: 3px;
                    border: 2px solid #2C3E50;
                }}
                QLabel {{
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                }}
            """)
            produto_layout = QVBoxLayout(produto_frame)
            produto_layout.setContentsMargins(8, 8, 8, 8)
            produto_layout.setSpacing(8)
            
            # Nome do produto com mais espaço (fonte maior)
            nome_label = QLabel(f"{dados['emoji']} {produto.split()[1]}")
            nome_label.setAlignment(Qt.AlignCenter)
            nome_label.setStyleSheet("font-size: 14px; padding: 6px; font-weight: bold;")
            produto_layout.addWidget(nome_label)
            
            # Informações do produto (fonte maior e melhor contraste)
            info_label = QLabel(f"💰 ${dados['preco_venda']} | ⏱️ {dados['tempo_producao']}t")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("font-size: 11px; color: #FFFFFF; background-color: rgba(0,0,0,0.3); padding: 3px; border-radius: 3px;")
            produto_layout.addWidget(info_label)
            
            # Controles em layout horizontal mais espaçoso
            controles_layout = QHBoxLayout()
            controles_layout.setSpacing(10)
            controles_layout.setContentsMargins(8, 8, 8, 8)
            
            # Label para quantidade (fonte maior)
            qtd_label = QLabel("Qtd:")
            qtd_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
            controles_layout.addWidget(qtd_label)
            
            # SpinBox melhorado (maior e melhor visibilidade)
            spinbox = QSpinBox()
            spinbox.setMinimum(1)  # Mudei de 0 para 1 para resolver o erro
            spinbox.setMaximum(999)
            spinbox.setValue(1)  # Valor padrão 1 em vez de 0
            spinbox.setMinimumWidth(70)
            spinbox.setMinimumHeight(35)
            spinbox.setStyleSheet("""
                QSpinBox {
                    font-size: 14px; 
                    font-weight: bold;
                    background-color: white; 
                    color: black;
                    border: 2px solid #2C3E50;
                    border-radius: 5px;
                    padding: 6px;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    width: 16px;
                    background-color: #3498DB;
                    border: none;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #2980B9;
                }
            """)
            self.entradas_quantidade_empresas[nome_empresa][produto] = spinbox
            controles_layout.addWidget(spinbox)
            
            # Botões maiores e mais claros (fontes aumentadas)
            btn_simular = QPushButton("📊 Simular")
            btn_simular.setMinimumWidth(85)
            btn_simular.setMinimumHeight(38)
            btn_simular.setStyleSheet("""
                QPushButton {
                    background-color: #3498DB; 
                    color: white;
                    font-size: 12px; 
                    font-weight: bold;
                    padding: 8px 12px;
                    border: none;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #2980B9;
                }
                QPushButton:pressed {
                    background-color: #21618C;
                }
            """)
            btn_simular.clicked.connect(lambda checked, p=produto: self.simular_producao_empresa(p, nome_empresa))
            
            btn_confirmar = QPushButton("✓ Produzir")
            btn_confirmar.setMinimumWidth(85)
            btn_confirmar.setMinimumHeight(38)
            btn_confirmar.setStyleSheet("""
                QPushButton {
                    background-color: #27AE60; 
                    color: white;
                    font-size: 12px; 
                    font-weight: bold;
                    padding: 8px 12px;
                    border: none;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
                QPushButton:pressed {
                    background-color: #1E8449;
                }
            """)
            btn_confirmar.clicked.connect(lambda checked, p=produto: self.confirmar_producao_empresa(p, nome_empresa))
            
            controles_layout.addWidget(btn_simular)
            controles_layout.addWidget(btn_confirmar)
            controles_layout.addStretch()
            
            produto_layout.addLayout(controles_layout)
            producao_layout.addWidget(produto_frame)
        
        parent_layout.addWidget(producao_group)
        
        # Adicionar seção de ordens de produção ativas
        self.criar_secao_ordens_producao(parent_layout, nome_empresa)
    
    def criar_secao_ordens_producao(self, parent_layout, nome_empresa):
        """Cria seção para visualizar ordens de produção ativas"""
        ordens_group = QGroupBox("📋 ORDENS DE PRODUÇÃO ATIVAS")
        ordens_group.setStyleSheet("""
            QGroupBox { 
                font-size: 12px; 
                font-weight: bold;
                margin-top: 10px; 
                padding-top: 15px;
                border: 2px solid #34495E;
                border-radius: 8px;
                background-color: #2C3E50;
            }
            QGroupBox::title {
                color: #F39C12;
                padding: 0px 8px;
            }
        """)
        ordens_layout = QVBoxLayout(ordens_group)
        ordens_layout.setSpacing(8)
        ordens_layout.setContentsMargins(10, 20, 10, 10)
        
        # Área de scroll para as ordens
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(120)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #34495E;
                border-radius: 5px;
                background-color: #34495E;
            }
        """)
        
        # Widget interno do scroll
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(5)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        
        # Label de status inicial
        status_label = QLabel("🔄 Nenhuma ordem de produção ativa")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("""
            color: #BDC3C7; 
            font-size: 11px; 
            font-style: italic;
            padding: 10px;
        """)
        scroll_layout.addWidget(status_label)
        
        scroll_area.setWidget(scroll_widget)
        ordens_layout.addWidget(scroll_area)
        
        # Botão para limpar ordens
        limpar_btn = QPushButton("🗑️ Limpar Todas as Ordens")
        limpar_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                font-size: 10px;
                font-weight: bold;
                padding: 6px;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:pressed {
                background-color: #A93226;
            }
        """)
        limpar_btn.clicked.connect(lambda: self.limpar_ordens_producao(nome_empresa))
        ordens_layout.addWidget(limpar_btn)
        
        # Armazenar referência para atualização
        self.displays_ordens_producao[nome_empresa] = {
            'scroll_layout': scroll_layout,
            'status_label': status_label
        }
        
        parent_layout.addWidget(ordens_group)
    
    def atualizar_display_ordens_producao(self, nome_empresa):
        """Atualiza o display das ordens de produção para uma empresa"""
        if nome_empresa not in self.displays_ordens_producao:
            return
            
        display = self.displays_ordens_producao[nome_empresa]
        scroll_layout = display['scroll_layout']
        status_label = display['status_label']
        
        # Limpar layout atual
        while scroll_layout.count():
            child = scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Verificar se há ordens ativas
        producao_atual = self.empresas[nome_empresa]['producao_atual']
        
        if not producao_atual or all(qtd == 0 for qtd in producao_atual.values()):
            # Nenhuma ordem ativa
            status_label.setText("🔄 Nenhuma ordem de produção ativa")
            status_label.setStyleSheet("""
                color: #BDC3C7; 
                font-size: 11px; 
                font-style: italic;
                padding: 10px;
            """)
            scroll_layout.addWidget(status_label)
        else:
            # Mostrar ordens ativas
            total_ordens = 0
            for produto, quantidade in producao_atual.items():
                if quantidade > 0:
                    total_ordens += quantidade
                    
                    # Frame para cada ordem
                    ordem_frame = QFrame()
                    dados_produto = self.produtos[produto]
                    ordem_frame.setStyleSheet(f"""
                        QFrame {{
                            background-color: {dados_produto['cor']};
                            border-radius: 5px;
                            padding: 5px;
                            margin: 2px;
                            border: 1px solid #2C3E50;
                        }}
                        QLabel {{
                            color: white;
                            font-weight: bold;
                            font-size: 10px;
                        }}
                    """)
                    
                    ordem_layout = QHBoxLayout(ordem_frame)
                    ordem_layout.setContentsMargins(8, 4, 8, 4)
                    
                    # Ícone e nome do produto
                    produto_label = QLabel(f"{dados_produto['emoji']} {produto.split()[1]}")
                    produto_label.setStyleSheet("font-size: 11px;")
                    
                    # Quantidade
                    qtd_label = QLabel(f"Qtd: {quantidade}")
                    qtd_label.setStyleSheet("font-size: 10px; color: #E8E8E8;")
                    
                    # Receita estimada
                    receita = dados_produto['preco_venda'] * quantidade
                    receita_label = QLabel(f"💰 ${receita}")
                    receita_label.setStyleSheet("font-size: 10px; color: #F1C40F;")
                    
                    # Botão excluir individual
                    btn_excluir = QPushButton("🗑️")
                    btn_excluir.setFixedSize(20, 20)
                    btn_excluir.setStyleSheet("""
                        QPushButton {
                            background-color: #E74C3C;
                            color: white;
                            border: none;
                            border-radius: 10px;
                            font-size: 10px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #C0392B;
                        }
                    """)
                    btn_excluir.clicked.connect(lambda checked, p=produto, ne=nome_empresa: self.excluir_ordem_individual(p, ne))
                    
                    ordem_layout.addWidget(produto_label)
                    ordem_layout.addStretch()
                    ordem_layout.addWidget(qtd_label)
                    ordem_layout.addWidget(receita_label)
                    ordem_layout.addWidget(btn_excluir)
                    
                    scroll_layout.addWidget(ordem_frame)
            
            # Adicionar resumo
            resumo_label = QLabel(f"📊 Total: {total_ordens} itens em produção")
            resumo_label.setAlignment(Qt.AlignCenter)
            resumo_label.setStyleSheet("""
                color: #3498DB; 
                font-size: 10px; 
                font-weight: bold;
                padding: 5px;
                background-color: rgba(52, 73, 94, 0.3);
                border-radius: 3px;
                margin: 3px;
            """)
            scroll_layout.addWidget(resumo_label)
    
    def excluir_ordem_individual(self, produto, nome_empresa):
        """Exclui uma ordem específica de produção"""
        if produto not in self.empresas[nome_empresa]['producao_atual'] or self.empresas[nome_empresa]['producao_atual'][produto] == 0:
            QMessageBox.information(self, "Info", f"Nenhuma ordem ativa para {produto}")
            return
        
        quantidade = self.empresas[nome_empresa]['producao_atual'][produto]
        resposta = QMessageBox.question(
            self, 
            "Confirmar Exclusão", 
            f"Deseja excluir a ordem de {quantidade} {produto} de {nome_empresa}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.Yes:
            # Excluir a ordem específica
            self.empresas[nome_empresa]['producao_atual'][produto] = 0
            
            # Limpar completamente se não sobrou nada
            if all(qtd == 0 for qtd in self.empresas[nome_empresa]['producao_atual'].values()):
                self.empresas[nome_empresa]['producao_atual'] = {}
            
            # Note: Display update calls removed as they're no longer needed in the optimization architecture
            self.atualizar_painel_info_empresa(nome_empresa)
            
            QMessageBox.information(self, "Sucesso", f"Ordem de {produto} excluída com sucesso!")

    def limpar_ordens_producao(self, nome_empresa):
        """Limpa todas as ordens de produção de uma empresa"""
        producao_atual = self.empresas[nome_empresa]['producao_atual']
        if not producao_atual or all(qtd == 0 for qtd in producao_atual.values()):
            QMessageBox.information(self, "Info", f"Nenhuma ordem ativa para {nome_empresa}")
            return
            
        resposta = QMessageBox.question(
            self, 
            "Confirmar Limpeza", 
            f"Deseja realmente limpar todas as ordens de produção de {nome_empresa}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.Yes:
            self.empresas[nome_empresa]['producao_atual'] = {}
            # Note: Display update calls removed as they're no longer needed in the optimization architecture
            # Atualizar painel de informações para mostrar recursos sem consumo
            self.atualizar_painel_info_empresa(nome_empresa)
            QMessageBox.information(self, "Sucesso", f"Ordens de {nome_empresa} foram limpas!")
    
    def atualizar_display_ordens_expandida(self, nome_empresa):
        """Atualiza o display expandido das ordens de produção"""
        if not hasattr(self, 'displays_ordens_expandida') or nome_empresa not in self.displays_ordens_expandida:
            return
            
        display = self.displays_ordens_expandida[nome_empresa]
        scroll_layout = display['scroll_layout']
        status_label = display['status_label']
        
        # Limpar layout atual
        while scroll_layout.count():
            child = scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Verificar se há ordens ativas
        producao_atual = self.empresas[nome_empresa]['producao_atual']
        
        if not producao_atual or all(qtd == 0 for qtd in producao_atual.values()):
            # Nenhuma ordem ativa
            status_label.setText("🔄 Nenhuma ordem de produção ativa")
            status_label.setStyleSheet("""
                color: #BDC3C7; 
                font-size: 14px; 
                font-style: italic;
                padding: 20px;
            """)
            scroll_layout.addWidget(status_label)
        else:
            # Título das ordens ativas
            titulo_ordens = QLabel("📋 ORDENS PROGRAMADAS PARA O PRÓXIMO TURNO")
            titulo_ordens.setAlignment(Qt.AlignCenter)
            titulo_ordens.setStyleSheet("""
                color: #F39C12; 
                font-size: 14px; 
                font-weight: bold;
                padding: 10px;
                background-color: rgba(52, 73, 94, 0.5);
                border-radius: 5px;
                margin: 5px;
            """)
            scroll_layout.addWidget(titulo_ordens)
            
            # Mostrar ordens ativas com mais detalhes
            total_ordens = 0
            receita_total = 0
            
            for produto, quantidade in producao_atual.items():
                if quantidade > 0:
                    total_ordens += quantidade
                    dados_produto = self.produtos[produto]
                    receita_produto = dados_produto['preco_venda'] * quantidade
                    receita_total += receita_produto
                    
                    # Frame detalhado para cada ordem
                    ordem_frame = QFrame()
                    ordem_frame.setStyleSheet(f"""
                        QFrame {{
                            background-color: {dados_produto['cor']};
                            border-radius: 8px;
                            padding: 12px;
                            margin: 5px;
                            border: 2px solid #2C3E50;
                        }}
                        QLabel {{
                            color: white;
                            font-weight: bold;
                        }}
                    """)
                    
                    ordem_layout = QVBoxLayout(ordem_frame)
                    ordem_layout.setSpacing(8)
                    
                    # Cabeçalho do produto
                    header_layout = QHBoxLayout()
                    produto_label = QLabel(f"{dados_produto['emoji']} {produto}")
                    produto_label.setStyleSheet("font-size: 16px; font-weight: bold;")
                    
                    qtd_label = QLabel(f"Quantidade: {quantidade}")
                    qtd_label.setStyleSheet("font-size: 14px; color: #E8E8E8;")
                    
                    # Botão excluir individual
                    btn_excluir_expandido = QPushButton("🗑️ Excluir")
                    btn_excluir_expandido.setStyleSheet("""
                        QPushButton {
                            background-color: #E74C3C;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            font-size: 11px;
                            font-weight: bold;
                            padding: 5px 10px;
                        }
                        QPushButton:hover {
                            background-color: #C0392B;
                        }
                    """)
                    btn_excluir_expandido.clicked.connect(lambda checked, p=produto, ne=nome_empresa: self.excluir_ordem_individual(p, ne))
                    
                    header_layout.addWidget(produto_label)
                    header_layout.addStretch()
                    header_layout.addWidget(qtd_label)
                    header_layout.addWidget(btn_excluir_expandido)
                    ordem_layout.addLayout(header_layout)
                    
                    # Detalhes financeiros
                    financeiro_layout = QHBoxLayout()
                    
                    preco_unit = QLabel(f"💰 Preço unitário: ${dados_produto['preco_venda']}")
                    preco_unit.setStyleSheet("font-size: 12px; color: #F1C40F;")
                    
                    receita_label = QLabel(f"💵 Receita total: ${receita_produto}")
                    receita_label.setStyleSheet("font-size: 12px; color: #F1C40F; font-weight: bold;")
                    
                    financeiro_layout.addWidget(preco_unit)
                    financeiro_layout.addStretch()
                    financeiro_layout.addWidget(receita_label)
                    ordem_layout.addLayout(financeiro_layout)
                    
                    # Custos de produção
                    custo_materia = dados_produto['custo_materia'] * quantidade
                    custo_energia = dados_produto['custo_energia'] * quantidade
                    custo_trabalhadores = dados_produto['custo_trabalhadores'] * quantidade
                    
                    custos_layout = QHBoxLayout()
                    custos_layout.addWidget(QLabel(f"📦 Matéria: {custo_materia}"))
                    custos_layout.addWidget(QLabel(f"⚡ Energia: {custo_energia}"))
                    custos_layout.addWidget(QLabel(f"👥 Trabalhadores: {custo_trabalhadores}"))
                    custos_layout.addWidget(QLabel(f"⏱️ Tempo: {dados_produto['tempo_producao']}t"))
                    
                    for i in range(custos_layout.count()):
                        widget = custos_layout.itemAt(i).widget()
                        if widget:
                            widget.setStyleSheet("font-size: 11px; color: #BDC3C7;")
                    
                    ordem_layout.addLayout(custos_layout)
                    scroll_layout.addWidget(ordem_frame)
            
            # Resumo total
            resumo_frame = QFrame()
            resumo_frame.setStyleSheet("""
                QFrame {
                    background-color: #34495E;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 5px;
                    border: 2px solid #3498DB;
                }
                QLabel {
                    color: #ECF0F1;
                    font-weight: bold;
                }
            """)
            resumo_layout = QVBoxLayout(resumo_frame)
            
            resumo_titulo = QLabel("📊 RESUMO TOTAL DAS ORDENS")
            resumo_titulo.setAlignment(Qt.AlignCenter)
            resumo_titulo.setStyleSheet("font-size: 14px; color: #3498DB; margin-bottom: 10px;")
            resumo_layout.addWidget(resumo_titulo)
            
            resumo_info_layout = QHBoxLayout()
            resumo_info_layout.addWidget(QLabel(f"📦 Total de itens: {total_ordens}"))
            resumo_info_layout.addWidget(QLabel(f"💰 Receita total esperada: ${receita_total}"))
            resumo_info_layout.addWidget(QLabel(f"🎯 Turno atual: {self.turno_atual}"))
            
            for i in range(resumo_info_layout.count()):
                widget = resumo_info_layout.itemAt(i).widget()
                if widget:
                    widget.setStyleSheet("font-size: 12px;")
            
            resumo_layout.addLayout(resumo_info_layout)
            scroll_layout.addWidget(resumo_frame)
    
    def criar_secao_producao(self, parent_layout):
        """Cria a seção de produção com tabs"""
        producao_group = QGroupBox("🏭 LINHA DE PRODUÇÃO")
        producao_layout = QVBoxLayout(producao_group)
        
        # Criar tabs para produtos
        self.tab_widget = QTabWidget()
        self.entradas_quantidade = {}
        
        for produto, dados in self.produtos.items():
            self.criar_tab_produto(produto, dados)
        
        producao_layout.addWidget(self.tab_widget)
        parent_layout.addWidget(producao_group)
    
    def criar_tab_produto(self, produto, dados):
        """Cria uma tab para cada produto"""
        tab = QWidget()
        tab.setStyleSheet("QWidget { background-color: #ECF0F1; color: #2C3E50; }")
        layout = QVBoxLayout(tab)
        
        # Título do produto
        titulo = QLabel(produto)
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {dados['cor']}; padding: 5px;")
        layout.addWidget(titulo)
        
        # Custos
        custos_frame = QFrame()
        custos_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {dados['cor']};
                border-radius: 5px;
                padding: 10px;
            }}
            QLabel {{
                color: white;
                font-weight: bold;
            }}
        """)
        custos_layout = QVBoxLayout(custos_frame)
        
        custos_layout.addWidget(QLabel("💰 CUSTOS DE PRODUÇÃO"))
        custos_layout.addWidget(QLabel(f"📦 Matéria-prima: {dados['custo_materia']}"))
        custos_layout.addWidget(QLabel(f"⚡ Energia: {dados['custo_energia']}"))
        custos_layout.addWidget(QLabel(f"👥 Trabalhadores: {dados['custo_trabalhadores']}"))
        custos_layout.addWidget(QLabel(f"💵 Preço de venda: ${dados['preco_venda']}"))
        
        layout.addWidget(custos_frame)
        
        # Entrada de quantidade
        entrada_group = QGroupBox("Quantidade a produzir:")
        entrada_layout = QFormLayout(entrada_group)
        
        spinbox = QSpinBox()
        spinbox.setMinimum(0)
        spinbox.setMaximum(999)
        spinbox.setValue(0)
        spinbox.setStyleSheet("font-size: 14px; padding: 5px;")
        self.entradas_quantidade[produto] = spinbox
        
        entrada_layout.addRow("Quantidade:", spinbox)
        
        # Botões
        botoes_layout = QHBoxLayout()
        
        btn_simular = QPushButton("🧮 Simular")
        btn_simular.setStyleSheet("background-color: #3498DB;")
        btn_simular.clicked.connect(lambda: self.simular_producao(produto))
        
        btn_confirmar = QPushButton("🎯 Confirmar")
        btn_confirmar.setStyleSheet("background-color: #27AE60;")
        btn_confirmar.clicked.connect(lambda: self.confirmar_producao(produto))
        
        botoes_layout.addWidget(btn_simular)
        botoes_layout.addWidget(btn_confirmar)
        
        entrada_layout.addRow(botoes_layout)
        layout.addWidget(entrada_group)
        layout.addStretch()
        
        # Adicionar tab
        self.tab_widget.addTab(tab, f"{dados['emoji']} {produto.split()[1]}")
    
    def criar_painel_graficos(self, parent_splitter):
        """Cria o painel de gráficos com matplotlib"""
        graficos_widget = QWidget()
        graficos_layout = QVBoxLayout(graficos_widget)
        
        # Título
        titulo = QLabel("📊 ANÁLISE EM TEMPO REAL")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #ECF0F1; padding: 10px;")
        graficos_layout.addWidget(titulo)
        
        # Criar figura matplotlib
        self.fig = Figure(figsize=(10, 8), facecolor='#34495E')
        self.canvas = FigureCanvas(self.fig)
        graficos_layout.addWidget(self.canvas)
        
        # Criar subplots
        self.ax1 = self.fig.add_subplot(2, 2, 1)
        self.ax2 = self.fig.add_subplot(2, 2, 2)
        self.ax3 = self.fig.add_subplot(2, 2, 3)
        self.ax4 = self.fig.add_subplot(2, 2, 4)
        
        # Configurar subplots para tema escuro
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.set_facecolor('#2C3E50')
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('white')
        
        self.fig.tight_layout()
        
        parent_splitter.addWidget(graficos_widget)
    
    def criar_footer(self, parent_layout):
        """Cria o rodapé com botões principais"""
        footer_frame = QFrame()
        footer_frame.setStyleSheet("""
            QFrame {
                background-color: #34495E;
                border: 2px solid #2C3E50;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setSpacing(5)
        
        # Botões principais (mais compactos)
        botoes = [
            ("� ITERAÇÃO", "#27AE60", self.executar_iteracao),
            ("📈 RELATÓRIO", "#3498DB", self.mostrar_relatorio),
            ("📋 MODELO", "#9B59B6", self.mostrar_modelo_matematico),
            ("🔄 NOVO", "#E74C3C", self.reiniciar_jogo),
            ("💾 SALVAR", "#95A5A6", self.salvar_jogo),
        ]
        
        for texto, cor, funcao in botoes:
            btn = QPushButton(texto)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {cor};
                    color: white;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 6px 12px;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {self.escurecer_cor(cor)};
                }}
            """)
            btn.clicked.connect(funcao)
            footer_layout.addWidget(btn)
        
        parent_layout.addWidget(footer_frame)
    
    def escurecer_cor(self, cor):
        """Escurece uma cor para o efeito hover"""
        cores_escuras = {
            "#27AE60": "#229954",
            "#3498DB": "#2980B9",
            "#9B59B6": "#8E44AD",
            "#E74C3C": "#C0392B",
            "#95A5A6": "#7F8C8D"
        }
        return cores_escuras.get(cor, cor)
    
    def atualizar_graficos(self):
        """Atualiza todos os gráficos (método de compatibilidade)"""
        self.atualizar_todas_interfaces()
    
    def mostrar_relatorio(self):
        """Mostra relatório completo multi-empresas"""
        dialog = RelatorioMultiDialog(self)
        dialog.exec()
    
    def reiniciar_jogo(self):
        """Reinicia o jogo"""
        resposta = QMessageBox.question(self, "Reiniciar", "Deseja realmente reiniciar a simulação?")
        if resposta == QMessageBox.Yes:
            self.close()
            novo_jogo = JogoEconomicoImersivo()
            novo_jogo.show()
    
    def tem_autosave_disponivel(self):
        """Retorna True se houver um autosave disponível."""
        return os.path.exists(self.caminho_autosave)

    def carregar_estado_temporario(self):
        """Carrega o último estado temporário, se existir."""
        if not self.tem_autosave_disponivel():
            return None
        try:
            with open(self.caminho_autosave, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[AutoSave] Falha ao carregar estado temporário: {e}")
            return None

    def salvar_estado_temporario(self):
        """Salva o estado atual em um arquivo temporário (auto-save)."""
        dados_jogo = {
            'iteracao_atual': self.iteracao_atual,
            'max_iteracoes': self.max_iteracoes,
            'turno_atual': self.turno_atual,
            'max_turnos': self.max_turnos,
            'nomes_empresas': self.nomes_empresas,
            'equipes_empresas': self.equipes_empresas,
            'empresas': self.empresas,
            'timestamp': datetime.now().isoformat()
        }

        try:
            with open(self.caminho_autosave, 'w', encoding='utf-8') as f:
                json.dump(dados_jogo, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[AutoSave] Falha ao salvar estado temporário: {e}")

    def salvar_jogo(self):
        """Salva o estado atual de todas as empresas"""
        dados_jogo = {
            'iteracao_atual': self.iteracao_atual,
            'max_iteracoes': self.max_iteracoes,
            'turno_atual': self.turno_atual,
            'max_turnos': self.max_turnos,
            'nomes_empresas': self.nomes_empresas,
            'equipes_empresas': self.equipes_empresas,
            'empresas': self.empresas,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sugestao_nome = f"simulador_multi_empresas_{timestamp}.json"
            diretorio_inicial = os.path.dirname(self.ultimo_arquivo_salvo) if self.ultimo_arquivo_salvo else os.getcwd()
            caminho_sugerido = os.path.join(diretorio_inicial, sugestao_nome)

            arquivo, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar simulação",
                caminho_sugerido,
                "Arquivos JSON (*.json);;Todos os arquivos (*)"
            )

            if not arquivo:
                return

            if not arquivo.lower().endswith('.json'):
                arquivo += '.json'

            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_jogo, f, indent=2, ensure_ascii=False)
            
            self.ultimo_arquivo_salvo = arquivo
            QMessageBox.information(self, "Sucesso", f"Simulação salva em:\n{arquivo}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar: {str(e)}")
    
    def mostrar_modelo_matematico(self):
        """Mostra o modelo matemático do sistema"""
        dialog = ModeloMatematicoDialog(self)
        dialog.exec()
    
    # Métodos legados (removidos para compatibilidade)
    def simular_producao(self, produto):
        """Método legado - redirecionado"""
        if self.empresa_ativa:
            self.simular_producao_empresa(produto, self.empresa_ativa)
    
    def confirmar_producao(self, produto):
        """Método legado - redirecionado"""
        if self.empresa_ativa:
            self.confirmar_producao_empresa(produto, self.empresa_ativa)
    
    # ===== MÉTODOS PARA MÚLTIPLAS EMPRESAS =====
    
    def simular_producao_empresa(self, produto, nome_empresa):
        """Simula a produção para uma empresa específica"""
        try:
            quantidade = self.entradas_quantidade_empresas[nome_empresa][produto].value()
            if quantidade < 1:  # Mudei de <= 0 para < 1
                # Mostrar erro na área de simulação expandida se existir
                if hasattr(self, 'text_simulacao_expandida') and nome_empresa in self.text_simulacao_expandida:
                    self.text_simulacao_expandida[nome_empresa].append("⚠️ Quantidade deve ser pelo menos 1!")
                # Também mostrar no painel compacto
                if hasattr(self, 'text_simulacao_empresas') and nome_empresa in self.text_simulacao_empresas:
                    self.text_simulacao_empresas[nome_empresa].append("⚠️ Quantidade deve ser pelo menos 1!")
                return
                
            dados = self.produtos[produto]
            recursos = self.empresas[nome_empresa]['recursos_disponiveis']
            
            # Calcular custos
            custo_materia = dados['custo_materia'] * quantidade
            custo_energia = dados['custo_energia'] * quantidade
            custo_trabalhadores = dados['custo_trabalhadores'] * quantidade
            receita = dados['preco_venda'] * quantidade
            lucro = receita
            
            # Verificar viabilidade
            viavel = (custo_materia <= recursos['materia_prima'] and
                     custo_energia <= recursos['energia'] and
                     custo_trabalhadores <= recursos['trabalhadores'])
            
            # Calcular recursos restantes após produção
            materia_restante = recursos['materia_prima'] - custo_materia
            energia_restante = recursos['energia'] - custo_energia
            trabalhadores_restantes = recursos['trabalhadores'] - custo_trabalhadores
            
            # Mostrar resultado detalhado
            resultado = f"""
🧮 SIMULAÇÃO DETALHADA: {produto}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 PARÂMETROS DA SIMULAÇÃO:
   • Produto: {dados['emoji']} {produto}
   • Quantidade solicitada: {quantidade} unidades
   • Tempo de produção: {dados['tempo_producao']} turnos

💰 ANÁLISE FINANCEIRA:
   • Preço de venda por unidade: ${dados['preco_venda']}
   • Receita total esperada: ${receita}
   • Margem bruta: 100% (sem custos de matéria-prima deduzidos)

📦 RECURSOS NECESSÁRIOS:
   • Matéria-prima: {custo_materia} unidades
   • Energia: {custo_energia} unidades  
   • Trabalhadores: {custo_trabalhadores} unidades

📋 RECURSOS ATUAIS:
   • Matéria-prima disponível: {recursos['materia_prima']}
   • Energia disponível: {recursos['energia']}
   • Trabalhadores disponíveis: {recursos['trabalhadores']}

📈 RECURSOS APÓS PRODUÇÃO:
   • Matéria-prima restante: {materia_restante}
   • Energia restante: {energia_restante}
   • Trabalhadores restantes: {trabalhadores_restantes}

{'✅ PRODUÇÃO VIÁVEL - Recursos suficientes!' if viavel else '❌ PRODUÇÃO INVIÁVEL - Recursos insuficientes!'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Simulação realizada em: {datetime.now().strftime('%H:%M:%S')}

"""
            
            # Mostrar na área de simulação expandida
            if hasattr(self, 'text_simulacao_expandida') and nome_empresa in self.text_simulacao_expandida:
                self.text_simulacao_expandida[nome_empresa].append(resultado)
            
            # Mostrar também no painel compacto (versão resumida)
            resultado_compacto = f"""
🧮 SIMULAÇÃO {nome_empresa}: {produto}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Qtd: {quantidade} | 💰 Receita: ${receita}
📦 Matéria: {custo_materia} | ⚡ Energia: {custo_energia}
👥 Trabalhadores: {custo_trabalhadores}
{'✅ VIÁVEL' if viavel else '❌ RECURSOS INSUFICIENTES'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            if hasattr(self, 'text_simulacao_empresas') and nome_empresa in self.text_simulacao_empresas:
                self.text_simulacao_empresas[nome_empresa].append(resultado_compacto)
            
            # Redirecionar automaticamente para a aba de simulação
            self.navegar_para_aba(nome_empresa, 2)  # Aba 2 = Simulação
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na simulação: {str(e)}")
    
    def confirmar_producao_empresa(self, produto, nome_empresa):
        """Confirma a produção para uma empresa específica"""
        try:
            quantidade = self.entradas_quantidade_empresas[nome_empresa][produto].value()
            if quantidade < 1:  # Mudei de <= 0 para < 1
                QMessageBox.warning(self, "Erro", "Quantidade deve ser pelo menos 1!")
                return
                
            dados = self.produtos[produto]
            recursos = self.empresas[nome_empresa]['recursos_disponiveis']
            
            # Calcular custos
            custo_materia = dados['custo_materia'] * quantidade
            custo_energia = dados['custo_energia'] * quantidade
            custo_trabalhadores = dados['custo_trabalhadores'] * quantidade
            
            # Verificar recursos
            if (custo_materia > recursos['materia_prima'] or
                custo_energia > recursos['energia'] or
                custo_trabalhadores > recursos['trabalhadores']):
                QMessageBox.critical(self, "Erro", "Recursos insuficientes!")
                return
            
            # Guardar produção para execução no turno
            if produto not in self.empresas[nome_empresa]['producao_atual']:
                self.empresas[nome_empresa]['producao_atual'][produto] = 0
            self.empresas[nome_empresa]['producao_atual'][produto] += quantidade
            
            # Reset entrada para valor mínimo válido
            self.entradas_quantidade_empresas[nome_empresa][produto].setValue(1)
            
            # Note: Display update calls removed as they're no longer needed in the optimization architecture
            
            # Atualizar painel de informações em tempo real
            self.atualizar_painel_info_empresa(nome_empresa)
            
            QMessageBox.information(self, "Sucesso", 
                                  f"✅ {quantidade} {produto} adicionados à produção de {nome_empresa}!\n"
                                  f"Execute o turno para processar.")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao confirmar produção: {str(e)}")
    
    def executar_turno(self):
        """Executa um turno completo para todas as empresas"""
        resultado = self.controller.executar_turno()

        if resultado.status == "sem_producao":
            QMessageBox.warning(self, "Aviso", "Nenhuma empresa programou produção!")
            return

        if resultado.status == "fim_jogo":
            QMessageBox.information(self, "Fim", "Jogo finalizado!")
            if resultado.jogo_finalizado:
                self.mostrar_resultado_final_multi()
            return

        self.atualizar_todas_interfaces()

        if resultado.relatorio:
            QMessageBox.information(self, "Turno Executado", resultado.relatorio)

        if resultado.jogo_finalizado:
            self.mostrar_resultado_final_multi()
    
    def atualizar_todas_interfaces(self):
        """Atualiza todas as interfaces das empresas"""
        # Atualizar header geral
        if hasattr(self, 'label_iteracao_geral'):
            self.label_iteracao_geral.setText(f"🎯 {self.iteracao_atual}/{self.max_iteracoes} • {len(self.nomes_empresas)} Empresas")
        
        # Atualizar todos os componentes para cada empresa
        for nome_empresa in self.nomes_empresas:
            self._garantir_estruturas_empresa(nome_empresa)
            # Atualizar recursos
            self.atualizar_recursos_empresa(nome_empresa)
            
            # Atualizar análise de restrições SOMENTE após iteração
            self.atualizar_analise_restricoes(nome_empresa)

            # Atualizar painel da função objetivo com histórico mais recente
            self.atualizar_funcao_objetivo(nome_empresa)
            
            # Atualizar gráficos se existem
            if hasattr(self, 'atualizar_graficos_empresa'):
                self.atualizar_graficos_empresa(nome_empresa)
            
            # Sincronizar controles (sliders/spinboxes) com valores atuais
            self.sincronizar_controles_empresa(nome_empresa)
        
        # Atualizar ranking se existir
        if hasattr(self, 'atualizar_ranking'):
            self.atualizar_ranking()
    
    def sincronizar_controles_empresa(self, nome_empresa):
        """Sincroniza sliders e spinboxes com os valores atuais das variáveis de decisão"""
        if (nome_empresa not in self.sliders_decisao_empresas or 
            nome_empresa not in self.spinboxes_decisao_empresas):
            return
        
        variaveis_decisao = self.empresas[nome_empresa]['variaveis_decisao']
        
        for produto in self.produtos.keys():
            if produto in self.sliders_decisao_empresas[nome_empresa]:
                valor_atual = variaveis_decisao[produto]
                
                # Atualizar slider (sem disparar signals para evitar loop)
                slider = self.sliders_decisao_empresas[nome_empresa][produto]
                slider.blockSignals(True)
                if valor_atual <= slider.maximum():
                    slider.setValue(valor_atual)
                slider.blockSignals(False)
                
                # Atualizar spinbox (sem disparar signals para evitar loop)
                if produto in self.spinboxes_decisao_empresas[nome_empresa]:
                    spinbox = self.spinboxes_decisao_empresas[nome_empresa][produto]
                    spinbox.blockSignals(True)
                    spinbox.setValue(valor_atual)
                    spinbox.blockSignals(False)
                
                # Atualizar label de valor
                if (nome_empresa in self.labels_valores_empresas and 
                    produto in self.labels_valores_empresas[nome_empresa]):
                    label = self.labels_valores_empresas[nome_empresa][produto]
                    label.setText(f"{valor_atual}")
    
    def mostrar_resultado_final_planejamento(self):
        """Mostra resultado final do planejamento otimizado"""
        # Calcular ranking final baseado na receita
        dados_finais = []
        for nome_empresa in self.nomes_empresas:
            variaveis_decisao = self.empresas[nome_empresa]['variaveis_decisao']
            receita_total = sum(self.produtos[produto]['preco_venda'] * quantidade 
                              for produto, quantidade in variaveis_decisao.items())
            dados_finais.append((nome_empresa, receita_total))
        
        dados_finais.sort(key=lambda x: x[1], reverse=True)
        
        resultado = "🎯 RESULTADO FINAL - PLANEJAMENTO OTIMIZADO\n"
        resultado += "="*60 + "\n\n"
        
        # Ranking final
        resultado += "🏆 CLASSIFICAÇÃO POR RECEITA PROJETADA:\n\n"
        for i, (nome, receita) in enumerate(dados_finais):
            emoji_posicao = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}°"
            resultado += f"{emoji_posicao} {nome}: ${receita:,}\n"
            
            # Mostrar o plano final
            variaveis = self.empresas[nome]['variaveis_decisao']
            if any(q > 0 for q in variaveis.values()):
                resultado += "   Plano de Produção:\n"
                for produto, quantidade in variaveis.items():
                    if quantidade > 0:
                        resultado += f"     • {produto}: {quantidade} unidades\n"
            resultado += "\n"
        
        resultado += "\n🎉 Planejamento otimizado concluído!\n"
        resultado += "Obrigado por participarem da otimização!"
        
        QMessageBox.information(self, "Fim do Planejamento", resultado)
    
    def atualizar_recursos_empresa(self, nome_empresa):
        """Atualiza os labels de recursos de uma empresa"""
        # Atualizar header compacto
        if nome_empresa in self.labels_recursos_empresas:
            emojis = {"dinheiro": "💰", "materia_prima": "📦", 
                     "energia": "⚡", "trabalhadores": "👥"}
            
            recursos = self.empresas[nome_empresa]['recursos_disponiveis']
            for recurso, label in self.labels_recursos_empresas[nome_empresa].items():
                # Usar formato ultra compacto
                valor = recursos[recurso]
                if valor >= 1000:
                    valor_str = f"{valor/1000:.0f}k"
                else:
                    valor_str = str(valor)
                label.setText(f"{emojis[recurso]}{valor_str}")
        
        # Atualizar painel de recursos compacto na aba planejamento
        if hasattr(self, 'labels_recursos_compacto_empresas') and nome_empresa in self.labels_recursos_compacto_empresas:
            recursos = self.empresas[nome_empresa]['recursos_disponiveis']
            variaveis_decisao = self.empresas[nome_empresa]['variaveis_decisao']
            
            for recurso, widgets in self.labels_recursos_compacto_empresas[nome_empresa].items():
                if isinstance(widgets, dict):  # Nova estrutura com widgets múltiplos
                    disponivel = recursos[recurso]

                    usado = 0
                    if recurso == "dinheiro":
                        for produto, quantidade in variaveis_decisao.items():
                            if quantidade > 0:
                                usado += self.calcular_custo_financeiro_produto(produto, quantidade)
                    else:
                        mapeamento_custo = {
                            'materia_prima': 'custo_materia',
                            'energia': 'custo_energia',
                            'trabalhadores': 'custo_trabalhadores'
                        }
                        chave_custo = mapeamento_custo.get(recurso)
                        if chave_custo:
                            for produto, quantidade in variaveis_decisao.items():
                                if quantidade > 0 and chave_custo in self.produtos[produto]:
                                    usado += quantidade * self.produtos[produto][chave_custo]

                    restante = disponivel - usado
                    percentual_usado = min(100, (usado / disponivel) * 100) if disponivel > 0 else 0
                    razao_uso = usado / disponivel if disponivel > 0 else 0

                    accent = widgets.get('accent', '#1ABC9C')
                    card = widgets.get('card')

                    if restante < 0:
                        border_cor = "#E74C3C"
                        chunk_cor = "#E74C3C"
                        status_texto = "❌ VIOLAÇÃO!"
                        status_bg = "rgba(231, 76, 60, 0.25)"
                        status_fg = "#F9B4B4"
                    elif razao_uso > 0.8:
                        border_cor = "#F39C12"
                        chunk_cor = "#F39C12"
                        status_texto = "⚠️ ATENÇÃO!"
                        status_bg = "rgba(243, 156, 18, 0.22)"
                        status_fg = "#F7CA5B"
                    else:
                        border_cor = accent
                        chunk_cor = accent
                        status_texto = "✅ OK"
                        status_bg = "rgba(39, 174, 96, 0.22)"
                        status_fg = "#2ECC71"

                    if card is not None:
                        card.setStyleSheet(f"""
                            QFrame#cardRecurso {{
                                background-color: #0F1822;
                                border-radius: 14px;
                                border: 2px solid {border_cor};
                            }}
                        """)

                    widgets['progress'].setValue(int(percentual_usado))
                    if recurso == "dinheiro":
                        progress_format = f"${usado:,} / ${disponivel:,}  •  {int(percentual_usado)}%"
                    else:
                        progress_format = f"{usado:,} / {disponivel:,}  •  {int(percentual_usado)}%"
                    widgets['progress'].setFormat(progress_format)
                    widgets['progress'].setStyleSheet(f"""
                        QProgressBar {{
                            background-color: #070C12;
                            border-radius: 9px;
                            border: 2px solid {border_cor};
                            color: #F5F6FA;
                            font-weight: bold;
                            font-size: 12px;
                        }}
                        QProgressBar::chunk {{
                            background-color: {chunk_cor};
                            border-radius: 9px;
                        }}
                    """)

                    unitario_label = widgets.get('unitario')
                    if unitario_label is not None:
                        texto_constante = widgets.get('unitario_texto') or self._obter_texto_custo_unitario_constante(recurso)
                        unitario_label.setText(texto_constante)

                    widgets['status'].setText(status_texto)
                    widgets['status'].setStyleSheet(f"font-size: 13px; font-weight: bold; padding: 6px 12px; border-radius: 12px; background-color: {status_bg}; color: {status_fg};")
                    
                else:  # Estrutura antiga (compatibilidade)
                    valor = recursos[recurso]
                    if valor >= 1000:
                        valor_str = f"{valor/1000:.1f}k"
                    else:
                        valor_str = f"{valor:,}"
                    widgets.setText(valor_str)
                    
                    if valor < self.recursos_base[recurso]:
                        widgets.setStyleSheet("color: #E74C3C; font-weight: bold; font-size: 18px; background-color: rgba(231, 76, 60, 0.2); border-radius: 4px; padding: 4px;")
                    else:
                        widgets.setStyleSheet("color: white; font-weight: bold; font-size: 18px;")
    
    def atualizar_graficos_empresa(self, nome_empresa):
        """Atualiza os gráficos da aba de análise"""
        if nome_empresa not in self.graficos_empresas:
            return

        try:
            self._garantir_estruturas_empresa(nome_empresa)
            empresa = self.empresas[nome_empresa]
            painel = self.graficos_empresas[nome_empresa]

            historico_iter = empresa.get('historico_iteracoes', [])
            historico_dec = empresa.get('historico_decisoes', [])

            # --- métricas de resumo ---
            total_iteracoes = len(historico_iter)
            lucro_acumulado = sum((item.get('receita_total', 0) - item.get('custo_total', 0)) for item in historico_iter)
            total_violacoes = sum(len(item.get('violacoes', []) or []) for item in historico_iter)

            eficiencia_media = "--"
            eficiencia_valor = None
            if historico_iter:
                ultima_iteracao = historico_iter[-1]
                recursos_iter = ultima_iteracao.get('resumo_recursos', {}) or {}
                if recursos_iter:
                    ratios = []
                    for dados in recursos_iter.values():
                        disponivel = dados.get('disponivel', 0)
                        consumo = dados.get('consumo', 0)
                        if disponivel > 0:
                            ratios.append(min(consumo / disponivel, 1) * 100)
                    if ratios:
                        eficiencia_valor = sum(ratios) / len(ratios)
                        eficiencia_media = f"{eficiencia_valor:.1f}%"

            painel['metric_labels']['iteracoes'].setText(str(total_iteracoes))
            painel['metric_labels']['lucro_total'].setText(f"${lucro_acumulado:,.0f}")
            painel['metric_labels']['violacoes'].setText(str(total_violacoes))
            painel['metric_labels']['eficiencia'].setText(eficiencia_media)

            # --- gráfico financeiro ---
            ax_fin = painel['finance_ax']
            ax_fin.clear()
            ax_fin.set_facecolor('#1B262F')
            ax_fin.tick_params(colors='#BDC3C7', labelsize=9)
            for spine in ax_fin.spines.values():
                spine.set_color('#2ECC71')

            if historico_iter:
                iteracoes = [item.get('iteracao', idx + 1) for idx, item in enumerate(historico_iter)]
                receitas = [item.get('receita_total', 0) for item in historico_iter]
                custos = [item.get('custo_total', 0) for item in historico_iter]
                lucros = [r - c for r, c in zip(receitas, custos)]

                ax_fin.plot(iteracoes, receitas, color='#2ECC71', marker='o', linewidth=1.8, label='Receita')
                ax_fin.plot(iteracoes, custos, color='#E67E22', marker='o', linewidth=1.8, label='Custos')
                ax_fin.plot(iteracoes, lucros, color='#F1C40F', marker='o', linewidth=1.8, label='Lucro')

                faixa_min = min(min(receitas), min(custos), min(lucros))
                faixa_max = max(max(receitas), max(custos), max(lucros))
                margem = max(abs(faixa_min) * 0.1, abs(faixa_max) * 0.1, 1)
                ax_fin.set_ylim(faixa_min - margem, faixa_max + margem)

                ax_fin.set_xticks(iteracoes)
                ax_fin.set_xlabel('Iteração', color='#BDC3C7')
                ax_fin.set_ylabel('Valor ($)', color='#BDC3C7')
                ax_fin.grid(color='#253445', linestyle='--', linewidth=0.6, alpha=0.6)
                legenda = ax_fin.legend(facecolor='#1B262F', edgecolor='#2ECC71', fontsize=9)
                for text in legenda.get_texts():
                    text.set_color('#ECF0F1')
                ax_fin.set_title('Receita x custos x lucro', color='#AEB6BF', fontsize=11, pad=10)
            else:
                ax_fin.set_title('Sem dados financeiros ainda', color='#95A5A6', fontsize=11)
                ax_fin.set_xlim(0, 1)
                ax_fin.set_ylim(0, 1)
                ax_fin.set_xticks([])
                ax_fin.set_yticks([])
                ax_fin.text(0.5, 0.5, 'Execute uma iteração para gerar histórico.',
                            color='#BDC3C7', fontsize=10, ha='center', va='center')

            painel['finance_canvas'].draw_idle()

            # --- gráfico de recursos ---
            ax_rec = painel['recursos_ax']
            ax_rec.clear()
            ax_rec.set_facecolor('#1B262F')
            ax_rec.tick_params(colors='#BDC3C7', labelsize=9)
            for spine in ax_rec.spines.values():
                spine.set_color('#3498DB')

            if historico_iter:
                recursos_iter = historico_iter[-1].get('resumo_recursos', {}) or {}
                nomes = []
                disponiveis = []
                consumos = []
                cores = []
                paleta = {
                    'dinheiro': '#1ABC9C',
                    'materia_prima': '#E67E22',
                    'energia': '#F39C12',
                    'trabalhadores': '#9B59B6'
                }
                for recurso_id, dados in recursos_iter.items():
                    nomes.append(dados.get('nome', recurso_id.replace('_', ' ').title()))
                    disponiveis.append(dados.get('disponivel', 0))
                    consumos.append(dados.get('consumo', 0))
                    cores.append(paleta.get(recurso_id, '#5DADE2'))

                if nomes:
                    indices = range(len(nomes))
                    largura = 0.35
                    ax_rec.bar([i - largura/2 for i in indices], disponiveis, width=largura,
                               color='#32475B', label='Disponível')
                    ax_rec.bar([i + largura/2 for i in indices], consumos, width=largura,
                               color=cores, label='Consumido')
                    ax_rec.set_xticks(list(indices))
                    ax_rec.set_xticklabels(nomes, rotation=15, ha='right')
                    ax_rec.set_ylabel('Unidades', color='#BDC3C7')
                    ax_rec.grid(color='#253445', linestyle='--', linewidth=0.5, axis='y', alpha=0.6)
                    ax_rec.legend(facecolor='#1B262F', edgecolor='#3498DB', fontsize=9)
                else:
                    ax_rec.text(0.5, 0.5, 'Nenhum recurso monitorado ainda.',
                                color='#BDC3C7', fontsize=10, ha='center', va='center')
                    ax_rec.set_xticks([])
                    ax_rec.set_yticks([])
            else:
                ax_rec.text(0.5, 0.5, 'Sem dados de iteração para visualizar recursos.',
                            color='#BDC3C7', fontsize=10, ha='center', va='center')
                ax_rec.set_xticks([])
                ax_rec.set_yticks([])

            painel['recursos_canvas'].draw_idle()

            # --- gráfico de mix de produção ---
            ax_mix = painel['mix_ax']
            ax_mix.clear()
            ax_mix.set_facecolor('#1B242F')

            mix_total = {}
            for decisao in historico_dec:
                for produto, quantidade in (decisao.get('producao') or {}).items():
                    mix_total[produto] = mix_total.get(produto, 0) + quantidade

            if mix_total and sum(mix_total.values()) > 0:
                labels = list(mix_total.keys())
                valores = list(mix_total.values())
                cores = [self.produtos[label]['cor'] if label in self.produtos else '#95A5A6' for label in labels]
                ax_mix.pie(valores, labels=labels, colors=cores, autopct='%1.0f%%', textprops={'color': '#ECF0F1', 'fontsize': 10})
            else:
                ax_mix.text(0.5, 0.5, 'Nenhuma produção executada ainda.',
                            color='#BDC3C7', fontsize=10, ha='center', va='center')

            painel['mix_canvas'].draw_idle()

            # --- gráfico de violações ---
            ax_viol = painel['violacoes_ax']
            ax_viol.clear()
            ax_viol.set_facecolor('#1B262F')
            ax_viol.tick_params(colors='#BDC3C7', labelsize=9)
            for spine in ax_viol.spines.values():
                spine.set_color('#E74C3C')

            if historico_iter:
                iteracoes = [item.get('iteracao', idx + 1) for idx, item in enumerate(historico_iter)]
                qtd_viol = [len(item.get('violacoes', []) or []) for item in historico_iter]
                ax_viol.bar(iteracoes, qtd_viol, color='#E74C3C', alpha=0.75)
                ax_viol.set_xlabel('Iteração', color='#BDC3C7')
                ax_viol.set_ylabel('Qtd. violações', color='#BDC3C7')
                ax_viol.set_xticks(iteracoes)
                ax_viol.set_ylim(0, max(qtd_viol + [1]))
                ax_viol.grid(color='#253445', linestyle='--', linewidth=0.5, axis='y', alpha=0.6)
            else:
                ax_viol.text(0.5, 0.5, 'Nenhuma validação registrada ainda.',
                             color='#BDC3C7', fontsize=10, ha='center', va='center')
                ax_viol.set_xticks([])
                ax_viol.set_yticks([])

            painel['violacoes_canvas'].draw_idle()

            # --- classificação detalhada ---
            classificacao_texto = []
            recursos_iter_ultima = historico_iter[-1].get('resumo_recursos', {}) or {} if historico_iter else {}

            if total_iteracoes:
                lucro_medio = lucro_acumulado / total_iteracoes
                ultima_iteracao = historico_iter[-1]
                lucro_ultimo = ultima_iteracao.get('receita_total', 0) - ultima_iteracao.get('custo_total', 0)

                if lucro_medio > 15000:
                    status_financeiro = "Alta rentabilidade"
                    recomendacao_fin = "Considere investir em expansão controlada para consolidar ganhos."
                elif lucro_medio > 5000:
                    status_financeiro = "Rentabilidade sólida"
                    recomendacao_fin = "Mantenha o ritmo atual e busque otimizar custos marginais."
                elif lucro_medio > 0:
                    status_financeiro = "Lucro moderado"
                    recomendacao_fin = "Explore ajustes de preço ou escala para aumentar a margem."
                elif lucro_medio == 0:
                    status_financeiro = "Equilíbrio financeiro"
                    recomendacao_fin = "Revise volumes de produção para destravar crescimento."
                else:
                    status_financeiro = "Prejuízo recorrente"
                    recomendacao_fin = "Reavalie imediatamente preços, mix e custos antes da próxima rodada."

                classificacao_texto.append(
                    f"Saúde financeira: {status_financeiro} (lucro médio ${lucro_medio:,.0f}/iteração; último lucro ${lucro_ultimo:,.0f}). {recomendacao_fin}"
                )
            else:
                classificacao_texto.append("Saúde financeira: aguarde a primeira iteração para avaliar o desempenho financeiro.")

            if eficiencia_valor is not None:
                if eficiencia_valor >= 85:
                    status_eficiencia = "Alta utilização com bom equilíbrio"
                elif eficiencia_valor >= 65:
                    status_eficiencia = "Uso moderado dos recursos"
                else:
                    status_eficiencia = "Utilização baixa, recursos ociosos"
                classificacao_texto.append(
                    f"Eficiência operacional: {status_eficiencia} (média de {eficiencia_valor:.1f}% de consumo dos recursos disponíveis)."
                )
            else:
                classificacao_texto.append("Eficiência operacional: ainda não há dados suficientes de consumo para calcular a eficiência.")

            if total_iteracoes:
                if total_violacoes == 0:
                    status_conformidade = "Totalmente em conformidade"
                else:
                    taxa_violacoes = total_violacoes / total_iteracoes
                    if taxa_violacoes >= 1:
                        status_conformidade = "Incidência crítica de violações"
                    elif taxa_violacoes >= 0.4:
                        status_conformidade = "Alerta severo para as restrições"
                    else:
                        status_conformidade = "Algumas violações pontuais"
                classificacao_texto.append(
                    f"Conformidade: {status_conformidade} ({total_violacoes} violações acumuladas em {total_iteracoes} iterações)."
                )

            if recursos_iter_ultima:
                recurso_critico = min(
                    recursos_iter_ultima.values(),
                    key=lambda dados: dados.get('restante', dados.get('disponivel', 0) - dados.get('consumo', 0))
                )
                restante = recurso_critico.get('restante')
                if restante is None:
                    disponivel = recurso_critico.get('disponivel', 0)
                    consumo = recurso_critico.get('consumo', 0)
                    restante = disponivel - consumo
                restante = max(restante, 0)
                disponivel = recurso_critico.get('disponivel', 0)
                percentual_restante = (restante / disponivel * 100) if disponivel else 0
                classificacao_texto.append(
                    f"Recursos críticos: {recurso_critico.get('nome', '—')} com {restante:,.0f} unidades restantes ({percentual_restante:.0f}% de folga)."
                )
            else:
                classificacao_texto.append("Recursos críticos: aguardando a primeira iteração para identificar gargalos.")

            if mix_total:
                total_produzido = sum(mix_total.values())
                produto_top, qtd_top = max(mix_total.items(), key=lambda item: item[1])
                participacao = (qtd_top / total_produzido * 100) if total_produzido else 0
                if participacao >= 60:
                    status_mix = "Portfólio concentrado em um único produto"
                elif participacao >= 35:
                    status_mix = "Portfólio balanceado com líder claro"
                else:
                    status_mix = "Portfólio diversificado"
                classificacao_texto.append(
                    f"Portfólio produtivo: {status_mix}. Destaque atual: {produto_top} ({participacao:.0f}% do volume acumulado)."
                )
            else:
                classificacao_texto.append("Portfólio produtivo: nenhuma produção executada até o momento.")

            prioridades = []
            if total_violacoes > 0:
                prioridades.append("mitigar violações")
            if total_iteracoes and lucro_acumulado <= 0:
                prioridades.append("reverter prejuízo")
            if eficiencia_valor is not None and eficiencia_valor < 60:
                prioridades.append("aproveitar melhor os recursos")

            if prioridades:
                if len(prioridades) == 1:
                    recomendacao_prioridade = prioridades[0]
                else:
                    recomendacao_prioridade = ", ".join(prioridades[:-1]) + f" e {prioridades[-1]}"
                classificacao_texto.append(f"Prioridade imediata: {recomendacao_prioridade} nas próximas decisões.")
            else:
                classificacao_texto.append("Prioridade imediata: consolidar ganhos e explorar oportunidades de expansão controlada.")

            painel['classificacao_label'].setText("\n\n".join(classificacao_texto))

            # --- insights textuais ---
            insights = []

            if historico_iter:
                melhor_iter = max(historico_iter, key=lambda item: item.get('receita_total', 0) - item.get('custo_total', 0))
                lucro_melhor = melhor_iter.get('receita_total', 0) - melhor_iter.get('custo_total', 0)
                insights.append(f"• Iteração {melhor_iter.get('iteracao')} gerou o maior lucro (${lucro_melhor:,.0f}).")

                recursos_iter = historico_iter[-1].get('resumo_recursos', {}) or {}
                if recursos_iter:
                    recurso_critico = min(
                        recursos_iter.values(),
                        key=lambda dados: dados.get('restante', dados.get('disponivel', 0))
                    )
                    restante = recurso_critico.get('restante', 0)
                    insights.append(
                        f"• Recurso mais crítico agora: {recurso_critico.get('nome', '—')} (restante {restante:,})."
                    )

            if mix_total:
                produto_top = max(mix_total.items(), key=lambda item: item[1])
                insights.append(f"• Produto campeão em produção: {produto_top[0]} ({produto_top[1]:,} unidades acumuladas).")

            if total_violacoes:
                insights.append(f"• {total_violacoes} violações acumuladas — revise as restrições destacadas no histórico.")
            elif total_iteracoes:
                insights.append("• Nenhuma violação registrada até agora. Excelente controle de recursos!")

            if not insights:
                insights = ["Ainda não há dados suficientes para gerar insights. Experimente rodar uma iteração ou turno."]

            painel['insights_label'].setText("\n".join(insights))

        except Exception as e:
            print(f"Erro ao atualizar gráficos da empresa {nome_empresa}: {e}")
    
    def atualizar_ranking(self):
        """Atualiza o ranking das empresas"""
        try:
            # Calcular dados do ranking
            dados_ranking = []
            for nome_empresa in self.nomes_empresas:
                empresa = self.empresas[nome_empresa]
                variaveis = empresa['variaveis_decisao']
                recursos = empresa['recursos_disponiveis']

                receita_atual = 0
                custo_total = 0
                total_unidades = 0
                consumo_recursos = {
                    'materia_prima': 0,
                    'energia': 0,
                    'trabalhadores': 0
                }

                for produto, quantidade in variaveis.items():
                    if quantidade <= 0 or produto not in self.produtos:
                        continue
                    dados_produto = self.produtos[produto]
                    receita_atual += dados_produto['preco_venda'] * quantidade
                    custo_total += self.calcular_custo_financeiro_produto(produto, quantidade)
                    total_unidades += quantidade

                    consumo_recursos['materia_prima'] += dados_produto.get('custo_materia', 0) * quantidade
                    consumo_recursos['energia'] += dados_produto.get('custo_energia', 0) * quantidade
                    consumo_recursos['trabalhadores'] += dados_produto.get('custo_trabalhadores', 0) * quantidade

                violacoes = 0
                if custo_total > recursos.get('dinheiro', 0):
                    violacoes += 1
                for recurso_tipo, consumo in consumo_recursos.items():
                    if consumo > recursos.get(recurso_tipo, 0):
                        violacoes += 1

                lucro_historico = 0
                if 'historico_iteracoes' in empresa:
                    lucro_historico = sum(d.get('receita_total', 0) for d in empresa['historico_iteracoes'])

                custo_unitario = (custo_total / total_unidades) if total_unidades > 0 else 0

                dados_ranking.append({
                    'nome': nome_empresa,
                    'receita_atual': receita_atual,
                    'lucro_historico': lucro_historico,
                    'dinheiro': recursos.get('dinheiro', 0),
                    'iteracoes_jogadas': len(empresa.get('historico_iteracoes', [])),
                    'violacoes': violacoes,
                    'custo_total': custo_total,
                    'custo_unitario': custo_unitario,
                    'total_unidades': total_unidades
                })
            
            # Ordenar: conformes primeiro, depois por menor violação e maior receita
            dados_ranking.sort(key=lambda x: (x['violacoes'] > 0, x['violacoes'], -x['receita_atual']))
            
            # Atualizar gráficos de ranking se existem
            if hasattr(self, 'atualizar_graficos_ranking'):
                self.atualizar_graficos_ranking(dados_ranking)
            
            # Atualizar tabela de ranking se existe
            if hasattr(self, 'atualizar_tabela_ranking'):
                self.atualizar_tabela_ranking(dados_ranking)
            
        except Exception as e:
            print(f"Erro ao atualizar ranking: {e}")
            import traceback
            traceback.print_exc()
    
    def atualizar_graficos_ranking(self, dados_ranking):
        """Atualiza os gráficos de ranking"""
        try:
            # Verificar se os gráficos existem
            if not hasattr(self, 'ax_ranking1'):
                return
            
            # Limpar gráficos
            self.ax_ranking1.clear()
            self.ax_ranking2.clear()
            self.ax_ranking3.clear()
            self.ax_ranking4.clear()
            
            # Configurar cores
            for ax in [self.ax_ranking1, self.ax_ranking2, self.ax_ranking3, self.ax_ranking4]:
                ax.set_facecolor('#2C3E50')
                ax.tick_params(colors='white', labelsize=8)
                for spine in ax.spines.values():
                    spine.set_color('white')
            
            if not dados_ranking:
                # Mostrar mensagem se não há dados
                self.ax_ranking1.text(0.5, 0.5, 'Sem dados de ranking', 
                                    ha='center', va='center', color='white', 
                                    transform=self.ax_ranking1.transAxes)
                self.fig_ranking.tight_layout()
                self.canvas_ranking.draw()
                return
            
            nomes = [d['nome'][:10] for d in dados_ranking]  # Limitar nome
            receitas = [d['receita_atual'] for d in dados_ranking]
            dinheiros = [d['dinheiro'] for d in dados_ranking]
            
            # Gráfico 1: Ranking de Receita Atual
            cores = ['#FFD700', '#C0C0C0', '#CD7F32', '#3498DB', '#9B59B6', '#E74C3C'][:len(nomes)]
            self.ax_ranking1.bar(nomes, receitas, color=cores)
            self.ax_ranking1.set_title('🏆 Receita Atual Planejada', color='white', fontweight='bold', fontsize=10)
            self.ax_ranking1.tick_params(axis='x', rotation=45, labelsize=8)
            
            # Gráfico 2: Recursos Disponíveis (Dinheiro)
            self.ax_ranking2.bar(nomes, dinheiros, color=cores)
            self.ax_ranking2.set_title('💰 Recursos Disponíveis', color='white', fontweight='bold', fontsize=10)
            self.ax_ranking2.tick_params(axis='x', rotation=45, labelsize=8)
            
            # Gráfico 3: Histórico de Receitas (se disponível)
            if any(d['iteracoes_jogadas'] > 0 for d in dados_ranking):
                for i, nome_empresa in enumerate(self.nomes_empresas):
                    historico = self.empresas[nome_empresa].get('historico_iteracoes', [])
                    if historico:
                        iteracoes = [h['iteracao'] for h in historico]
                        receitas_hist = [h['receita_total'] for h in historico]
                        self.ax_ranking3.plot(iteracoes, receitas_hist, 
                                            marker='o', label=nome_empresa[:8], linewidth=2)
                
                self.ax_ranking3.set_title('📈 Evolução das Receitas', color='white', fontweight='bold', fontsize=10)
                self.ax_ranking3.legend(fontsize=8)
                self.ax_ranking3.grid(True, alpha=0.3)
            else:
                self.ax_ranking3.text(0.5, 0.5, 'Execute iterações para\nver evolução', 
                                    ha='center', va='center', color='white', 
                                    transform=self.ax_ranking3.transAxes)
            
            # Gráfico 4: Análise de Restrições
            violacoes_count = []
            for nome_empresa in self.nomes_empresas:
                recursos_disponiveis = self.empresas[nome_empresa]['recursos_disponiveis']
                variaveis_decisao = self.empresas[nome_empresa]['variaveis_decisao']
                
                # Mapeamento de recursos para chaves de custo
                mapeamento_custo = {
                    'materia_prima': 'custo_materia',
                    'energia': 'custo_energia', 
                    'trabalhadores': 'custo_trabalhadores'
                }
                
                violacoes = 0
                for recurso, disponivel in recursos_disponiveis.items():
                    if recurso == "dinheiro":
                        continue
                    
                    chave_custo = mapeamento_custo.get(recurso)
                    if not chave_custo:
                        continue
                    
                    consumo_total = 0
                    for produto, quantidade in variaveis_decisao.items():
                        if quantidade > 0:
                            consumo_total += self.produtos[produto][chave_custo] * quantidade
                    
                    if consumo_total > disponivel:
                        violacoes += 1
                
                violacoes_count.append(violacoes)
            
            cores_violacoes = ['#27AE60' if v == 0 else '#E74C3C' for v in violacoes_count]
            self.ax_ranking4.bar(nomes, violacoes_count, color=cores_violacoes)
            self.ax_ranking4.set_title('⚠️ Violações de Restrições', color='white', fontweight='bold', fontsize=10)
            self.ax_ranking4.tick_params(axis='x', rotation=45, labelsize=8)
            self.ax_ranking4.tick_params(axis='x', rotation=45)
            
            self.fig_ranking.tight_layout()
            self.canvas_ranking.draw()
            
        except Exception as e:
            print(f"Erro ao atualizar gráficos de ranking: {e}")
    
    def atualizar_tabela_ranking(self, dados_ranking):
        """Atualiza o painel visual de ranking"""
        try:
            if not hasattr(self, 'ranking_cards_layout'):
                return
            # Limpar conteúdo atual
            while self.ranking_cards_layout.count():
                item = self.ranking_cards_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            self.ranking_cards = []

            total_empresas = len(dados_ranking)
            empresas_com_violacoes = 0

            def criar_card():
                card = QFrame()
                card.setProperty("class", "ranking-card")
                card_layout = QHBoxLayout(card)
                card_layout.setContentsMargins(12, 12, 12, 12)
                card_layout.setSpacing(12)

                pos_label = QLabel("—")
                pos_label.setProperty("class", "ranking-pos")
                pos_label.setStyleSheet("color: #F7DC6F;")
                card_layout.addWidget(pos_label, 0, Qt.AlignTop)

                info_layout = QVBoxLayout()
                info_layout.setSpacing(6)

                nome_label = QLabel("Empresa")
                nome_label.setProperty("class", "ranking-nome")
                nome_label.setWordWrap(True)
                info_layout.addWidget(nome_label)

                metrics_layout = QVBoxLayout()
                metrics_layout.setSpacing(4)

                receita_label = QLabel("💰 Receita planejada: —")
                receita_label.setProperty("class", "ranking-metric")
                metrics_layout.addWidget(receita_label)

                custo_total_label = QLabel("💵 Custo total estimado: —")
                custo_total_label.setProperty("class", "ranking-metric")
                metrics_layout.addWidget(custo_total_label)

                custo_unitario_label = QLabel("💸 Custo unitário do recurso: —")
                custo_unitario_label.setProperty("class", "ranking-metric")
                metrics_layout.addWidget(custo_unitario_label)

                restricoes_label = QLabel("⚖️ Restrições: —")
                restricoes_label.setProperty("class", "ranking-metric")
                metrics_layout.addWidget(restricoes_label)

                eficiencia_label = QLabel("📈 Score de eficiência: —")
                eficiencia_label.setProperty("class", "ranking-metric")
                metrics_layout.addWidget(eficiencia_label)

                info_layout.addLayout(metrics_layout)
                card_layout.addLayout(info_layout)

                self.ranking_cards_layout.addWidget(card)

                return {
                    'frame': card,
                    'pos': pos_label,
                    'nome': nome_label,
                    'receita': receita_label,
                    'custo_total': custo_total_label,
                    'custo_unitario': custo_unitario_label,
                    'restricoes': restricoes_label,
                    'eficiencia': eficiencia_label
                }

            empresas_com_violacoes = sum(1 for d in dados_ranking if d.get('violacoes', 0) > 0)

            for idx, dados in enumerate(dados_ranking):
                card = criar_card()
                self.ranking_cards.append(card)

                violacoes = dados.get('violacoes', 0)
                custo_total = dados.get('custo_total', 0)
                custo_unitario = dados.get('custo_unitario', 0)
                total_unidades = dados.get('total_unidades', 0)

                card['pos'].setText(f"{idx + 1}º")
                card['pos'].setStyleSheet("color: #F7DC6F; font-size: 30px;")

                card['nome'].setText(dados['nome'])
                card['receita'].setText(f"💰 Receita planejada: ${dados['receita_atual']:,.0f}")

                card['custo_total'].setText(f"💵 Custo total estimado: ${custo_total:,.0f}")
                if total_unidades > 0 and custo_unitario > 0:
                    card['custo_unitario'].setText(f"💸 Custo unitário do recurso: ${custo_unitario:,.2f} por unid.")
                else:
                    card['custo_unitario'].setText("💸 Custo unitário do recurso: —")

                if violacoes == 0:
                    card['restricoes'].setText("⚖️ Restrições: ✅ Em conformidade")
                    card['restricoes'].setStyleSheet("color: #58D68D; font-size: 13px;")
                else:
                    card['restricoes'].setText(f"⚖️ Restrições: ⚠️ {violacoes} alerta(s)")
                    card['restricoes'].setStyleSheet("color: #F1948A; font-size: 13px;")

                eficiencia_score = max(dados['receita_atual'] - custo_total - violacoes * 500, 0)
                card['eficiencia'].setText(f"📈 Score de eficiência: {eficiencia_score:,.0f}")
                card['eficiencia'].setStyleSheet("color: #85C1E9; font-size: 13px;")

            # Garantir espaço ao final do scroll
            self.ranking_cards_layout.addStretch()

            if hasattr(self, 'ranking_extra_label'):
                self.ranking_extra_label.hide()

            resumo_partes = []
            if total_empresas:
                resumo_partes.append(f"📊 Total de empresas: {total_empresas}")
                if empresas_com_violacoes:
                    resumo_partes.append(f"⚠️ {empresas_com_violacoes} com restrições a revisar")
                else:
                    resumo_partes.append("✅ Todas em conformidade")
            else:
                resumo_partes.append("Nenhuma empresa cadastrada")
            resumo_partes.append(f"🕒 Atualizado às {datetime.now().strftime('%H:%M:%S')}")
            self.ranking_summary_label.setText(" • ".join(resumo_partes))

        except Exception as e:
            print(f"Erro ao atualizar painel de ranking: {e}")
    
    def mostrar_resultado_final_multi(self):
        """Mostra resultado final para múltiplas empresas"""
        # Calcular ranking final
        dados_finais = []
        for nome_empresa in self.nomes_empresas:
            empresa = self.empresas[nome_empresa]
            lucro_total = sum(d['lucro'] for d in empresa['historico_decisoes'])
            dados_finais.append((nome_empresa, lucro_total))
        
        dados_finais.sort(key=lambda x: x[1], reverse=True)
        
        resultado = "🎯 RESULTADO FINAL - SIMULAÇÃO MULTI-EMPRESAS\n"
        resultado += "="*60 + "\n\n"
        
        # Ranking final
        resultado += "🏆 CLASSIFICAÇÃO FINAL:\n\n"
        for i, (nome, lucro) in enumerate(dados_finais):
            pos = i + 1
            if pos == 1:
                emoji = "🥇 CAMPEÃ"
            elif pos == 2:
                emoji = "🥈 VICE-CAMPEÃ"
            elif pos == 3:
                emoji = "🥉 TERCEIRO LUGAR"
            else:
                emoji = f"{pos}º LUGAR"
            
            resultado += f"{emoji}: {nome}\n"
            resultado += f"   💰 Lucro Total: ${lucro:,}\n"
            resultado += f"   📊 Média/Turno: ${lucro/(max(1, len(self.empresas[nome]['historico_decisoes']))):,.2f}\n\n"
        
        resultado += "\n🎉 Parabéns a todas as equipes!\n"
        resultado += "Obrigado por participarem da simulação!"
        
        QMessageBox.information(self, "Fim da Simulação", resultado)
    
    def criar_graficos_ranking(self):
        """Cria gráficos de ranking comparativo"""
        # Figura para gráficos de ranking
        self.fig_ranking = Figure(figsize=(12, 8), facecolor='#34495E')
        self.canvas_ranking = FigureCanvas(self.fig_ranking)
        
        # Criar subplots para ranking
        self.ax_ranking1 = self.fig_ranking.add_subplot(2, 2, 1)
        self.ax_ranking2 = self.fig_ranking.add_subplot(2, 2, 2)
        self.ax_ranking3 = self.fig_ranking.add_subplot(2, 2, 3)
        self.ax_ranking4 = self.fig_ranking.add_subplot(2, 2, 4)
        
        # Configurar para tema escuro
        for ax in [self.ax_ranking1, self.ax_ranking2, self.ax_ranking3, self.ax_ranking4]:
            ax.set_facecolor('#2C3E50')
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('white')
        
        self.fig_ranking.tight_layout()
        
        # Inicializar com dados vazios
        self.atualizar_ranking()

        return self.canvas_ranking
    
    def criar_tabela_ranking(self):
        """Cria painel visual de classificação detalhada"""
        container = QFrame()
        container.setObjectName("rankingClassContent")
        container.setStyleSheet("""
            QFrame#rankingClassContent {
                background-color: rgba(12, 24, 33, 0.4);
                border-radius: 12px;
                border: 1px solid rgba(243, 156, 18, 0.25);
            }
            QLabel#rankingTitle {
                font-size: 20px;
                font-weight: 800;
                color: #F5C469;
            }
            QLabel#rankingSubtitle {
                font-size: 12px;
                color: #BDC3C7;
            }
            QFrame[class~="ranking-card"] {
                background-color: rgba(21, 35, 46, 0.88);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
            QLabel[class~="ranking-pos"] {
                font-size: 28px;
            }
            QLabel[class~="ranking-nome"] {
                font-size: 18px;
                font-weight: 700;
                color: #ECF0F1;
            }
            QLabel[class~="ranking-metric"] {
                font-size: 13px;
                color: #D5DDE5;
            }
            QLabel#rankingExtra, QLabel#rankingSummary {
                color: #EAECEE;
                font-size: 12px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        titulo = QLabel("🏅 Classificação Geral")
        titulo.setObjectName("rankingTitle")
        layout.addWidget(titulo)

        subtitulo = QLabel("Atualizado automaticamente a cada iteração")
        subtitulo.setObjectName("rankingSubtitle")
        layout.addWidget(subtitulo)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: rgba(26, 40, 53, 0.9);
                width: 10px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #F39C12;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #D68910;
            }
        """)

        scroll_content = QWidget()
        cards_layout = QVBoxLayout(scroll_content)
        cards_layout.setContentsMargins(0, 0, 4, 0)
        cards_layout.setSpacing(10)

        self.ranking_cards_layout = cards_layout
        self.ranking_cards = []

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        self.ranking_extra_label = QLabel("")
        self.ranking_extra_label.setObjectName("rankingExtra")
        self.ranking_extra_label.setWordWrap(True)
        self.ranking_extra_label.hide()
        layout.addWidget(self.ranking_extra_label)

        self.ranking_summary_label = QLabel("—")
        self.ranking_summary_label.setObjectName("rankingSummary")
        self.ranking_summary_label.setWordWrap(True)
        layout.addWidget(self.ranking_summary_label)

        layout.addStretch()

        # Inicializar painel com dados vazios
        self.atualizar_ranking()

        return container


class SetupMultiEmpresasDialog(QDialog):
    """Dialog para configuração de múltiplas empresas"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nomes_empresas = []
        self.equipes_empresas = {}
        self.continue_requested = False
        self.dados_autosave = None
        self.caminho_json_selecionado = None

        self._parent_ref = parent
        self.cached_autosave = None
        self.autosave_disponivel = False
        if parent and hasattr(parent, 'tem_autosave_disponivel') and callable(parent.tem_autosave_disponivel):
            self.autosave_disponivel = parent.tem_autosave_disponivel()
            if self.autosave_disponivel and hasattr(parent, 'carregar_estado_temporario') and callable(parent.carregar_estado_temporario):
                self.cached_autosave = parent.carregar_estado_temporario()
                if not self.cached_autosave:
                    self.autosave_disponivel = False

        self.setWindowTitle("🏭 CONFIGURAÇÃO MULTI-EMPRESAS")
        self.setGeometry(300, 200, 700, 600)
        self.setModal(True)
        
        # Aplicar tema escuro
        self.setStyleSheet("""
            QDialog {
                background-color: #2C3E50;
                color: #ECF0F1;
            }
            QLabel {
                color: #ECF0F1;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #34495E;
                color: #ECF0F1;
                border: 2px solid #2C3E50;
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton#btnRemover {
                background-color: #E74C3C;
            }
            QPushButton#btnRemover:hover {
                background-color: #C0392B;
            }
            QPushButton#btnAdicionar {
                background-color: #3498DB;
            }
            QPushButton#btnAdicionar:hover {
                background-color: #2980B9;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #34495E;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QScrollArea {
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("🚀 CONFIGURAÇÃO MULTI-EMPRESAS")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; padding: 20px;")
        layout.addWidget(titulo)
        
        # Instruções
        instrucoes = QLabel("Configure quantas empresas irão competir (mínimo 2, máximo 6)")
        instrucoes.setAlignment(Qt.AlignCenter)
        instrucoes.setStyleSheet("font-size: 12px; color: #BDC3C7; padding: 10px;")
        layout.addWidget(instrucoes)
        
        # Área scrollável para empresas
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.empresas_layout = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(400)
        layout.addWidget(scroll)
        
        # Lista de empresas
        self.empresas_widgets = []
        
        # Adicionar 2 empresas iniciais
        self.adicionar_empresa("TechCorp Alpha", "Equipe Recursos A", "Equipe Produção A", "Equipe Finanças A")
        self.adicionar_empresa("InnovaCorp Beta", "Equipe Recursos B", "Equipe Produção B", "Equipe Finanças B")
        
        # Botões de controle
        botoes_layout = QHBoxLayout()
        
        btn_adicionar = QPushButton("➕ Adicionar Empresa")
        btn_adicionar.setObjectName("btnAdicionar")
        btn_adicionar.clicked.connect(self.adicionar_empresa_vazia)
        botoes_layout.addWidget(btn_adicionar)
        
        btn_remover = QPushButton("➖ Remover Última")
        btn_remover.setObjectName("btnRemover")
        btn_remover.clicked.connect(self.remover_empresa)
        botoes_layout.addWidget(btn_remover)
        
        layout.addLayout(botoes_layout)
        
        # Botão iniciar
        btn_iniciar = QPushButton("🚀 INICIAR SIMULAÇÃO")
        btn_iniciar.clicked.connect(self.aceitar)
        btn_iniciar.setStyleSheet("font-size: 14px; padding: 15px;")
        layout.addWidget(btn_iniciar)

        layout.addSpacing(6)
        btn_continuar = QPushButton("⏩ CARREGAR DE ARQUIVO JSON")
        btn_continuar.setStyleSheet("font-size: 13px; padding: 12px; background-color: #F39C12;")
        btn_continuar.clicked.connect(self.continuar_jogo)
        layout.addWidget(btn_continuar)

        if self.autosave_disponivel and self.cached_autosave:
            info_iteracao = self.cached_autosave.get('iteracao_atual')
            info_timestamp = self.cached_autosave.get('timestamp')
            if info_iteracao or info_timestamp:
                detalhes = []
                if info_iteracao:
                    detalhes.append(f"Iteração {info_iteracao}")
                if info_timestamp:
                    if 'T' in info_timestamp:
                        try:
                            detalhes.append(datetime.fromisoformat(info_timestamp).strftime("%d/%m/%Y %H:%M"))
                        except ValueError:
                            detalhes.append(info_timestamp)
                    else:
                        detalhes.append(info_timestamp)
                info_label = QLabel("Auto-save sugerido: " + " • ".join(detalhes))
                info_label.setAlignment(Qt.AlignCenter)
                info_label.setStyleSheet("font-size: 11px; color: #BDC3C7; padding: 4px;")
                layout.addWidget(info_label)
    
    def continuar_jogo(self):
        """Permite selecionar um arquivo JSON de jogo para continuar a simulação."""
        default_path = ""
        if self.autosave_disponivel and self._parent_ref and hasattr(self._parent_ref, 'caminho_autosave'):
            default_path = self._parent_ref.caminho_autosave
        elif self._parent_ref and hasattr(self._parent_ref, 'ultimo_arquivo_salvo') and self._parent_ref.ultimo_arquivo_salvo:
            default_path = self._parent_ref.ultimo_arquivo_salvo

        if not default_path:
            default_path = os.path.join(os.getcwd(), "")

        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo de simulação",
            default_path,
            "Arquivos JSON (*.json);;Todos os arquivos (*)"
        )

        if not arquivo:
            return

        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Arquivo inválido", f"Não foi possível carregar o arquivo selecionado.\n\nDetalhes: {e}")
            return

        nomes = dados.get('nomes_empresas') or []
        equipes = dados.get('equipes_empresas') or {}
        empresas_payload = dados.get('empresas')

        if not nomes or not empresas_payload:
            QMessageBox.warning(self, "Arquivo inválido", "O JSON selecionado não contém os dados necessários para a simulação.")
            return

        self.nomes_empresas = nomes
        self.equipes_empresas = equipes
        self.dados_autosave = dados
        self.caminho_json_selecionado = arquivo
        self.continue_requested = True
        self.accept()

    def adicionar_empresa(self, nome="", recursos="", producao="", financas=""):
        """Adiciona uma nova empresa ao formulário"""
        if len(self.empresas_widgets) >= 6:
            QMessageBox.warning(self, "Limite", "Máximo de 6 empresas permitidas!")
            return
        
        empresa_frame = QGroupBox(f"🏢 EMPRESA {len(self.empresas_widgets) + 1}")
        empresa_layout = QFormLayout(empresa_frame)
        
        # Campos da empresa
        entry_nome = QLineEdit(nome if nome else f"Empresa {len(self.empresas_widgets) + 1}")
        entry_recursos = QLineEdit(recursos if recursos else f"Equipe Recursos {chr(65 + len(self.empresas_widgets))}")
        entry_producao = QLineEdit(producao if producao else f"Equipe Produção {chr(65 + len(self.empresas_widgets))}")
        entry_financas = QLineEdit(financas if financas else f"Equipe Finanças {chr(65 + len(self.empresas_widgets))}")
        
        empresa_layout.addRow("🏢 Nome da Empresa:", entry_nome)
        empresa_layout.addRow("📦 Equipe Recursos:", entry_recursos)
        empresa_layout.addRow("🏭 Equipe Produção:", entry_producao)
        empresa_layout.addRow("💰 Equipe Finanças:", entry_financas)
        
        self.empresas_widgets.append({
            'frame': empresa_frame,
            'nome': entry_nome,
            'recursos': entry_recursos,
            'producao': entry_producao,
            'financas': entry_financas
        })
        
        self.empresas_layout.addWidget(empresa_frame)
    
    def adicionar_empresa_vazia(self):
        """Adiciona uma empresa com campos vazios"""
        self.adicionar_empresa()
    
    def remover_empresa(self):
        """Remove a última empresa"""
        if len(self.empresas_widgets) <= 2:
            QMessageBox.warning(self, "Mínimo", "Mínimo de 2 empresas necessárias!")
            return
        
        empresa_widget = self.empresas_widgets.pop()
        empresa_widget['frame'].setParent(None)
    
    def aceitar(self):
        """Valida e aceita a configuração"""
        if len(self.empresas_widgets) < 2:
            QMessageBox.warning(self, "Erro", "Mínimo de 2 empresas necessárias!")
            return
        
        self.nomes_empresas = []
        self.equipes_empresas = {}
        
        # Validar campos
        for i, empresa in enumerate(self.empresas_widgets):
            nome = empresa['nome'].text().strip()
            recursos = empresa['recursos'].text().strip()
            producao = empresa['producao'].text().strip()
            financas = empresa['financas'].text().strip()
            
            if not all([nome, recursos, producao, financas]):
                QMessageBox.warning(self, "Erro", f"Todos os campos da Empresa {i+1} devem ser preenchidos!")
                return
            
            if nome in self.nomes_empresas:
                QMessageBox.warning(self, "Erro", f"Nome da empresa '{nome}' já existe!")
                return
            
            self.nomes_empresas.append(nome)
            self.equipes_empresas[nome] = {
                'recursos': recursos,
                'producao': producao,
                'financas': financas
            }
        
        self.accept()


class SetupDialog(QDialog):
    """Dialog para configuração inicial"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🏭 CONFIGURAÇÃO INICIAL")
        self.setGeometry(400, 300, 500, 400)
        self.setModal(True)
        
        # Aplicar tema escuro
        self.setStyleSheet("""
            QDialog {
                background-color: #2C3E50;
                color: #ECF0F1;
            }
            QLabel {
                color: #ECF0F1;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #34495E;
                color: #ECF0F1;
                border: 2px solid #2C3E50;
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #34495E;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("🚀 CONFIGURAÇÃO DA SIMULAÇÃO")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px;")
        layout.addWidget(titulo)
        
        # Formulário
        form_group = QGroupBox("Configurações")
        form_layout = QFormLayout(form_group)
        
        # Nome da empresa
        self.entry_empresa = QLineEdit("TechCorp Industries")
        form_layout.addRow("🏢 Nome da Empresa:", self.entry_empresa)
        
        # Grupos
        self.entry_grupo_recursos = QLineEdit("Equipe Alpha")
        form_layout.addRow("📦 Grupo Recursos:", self.entry_grupo_recursos)
        
        self.entry_grupo_producao = QLineEdit("Equipe Beta")
        form_layout.addRow("🏭 Grupo Produção:", self.entry_grupo_producao)
        
        self.entry_grupo_financas = QLineEdit("Equipe Gamma")
        form_layout.addRow("💰 Grupo Finanças:", self.entry_grupo_financas)
        
        layout.addWidget(form_group)
        
        # Botão
        btn_iniciar = QPushButton("🚀 INICIAR SIMULAÇÃO")
        btn_iniciar.clicked.connect(self.aceitar)
        layout.addWidget(btn_iniciar)
    
    def aceitar(self):
        self.nome_empresa = self.entry_empresa.text().strip()
        self.grupo_recursos = self.entry_grupo_recursos.text().strip()
        self.grupo_producao = self.entry_grupo_producao.text().strip()
        self.grupo_financas = self.entry_grupo_financas.text().strip()
        
        if not all([self.nome_empresa, self.grupo_recursos, self.grupo_producao, self.grupo_financas]):
            QMessageBox.warning(self, "Erro", "Todos os campos devem ser preenchidos!")
            return
        
        self.accept()

class RelatorioMultiDialog(QDialog):
    """Dialog para mostrar relatório completo multi-empresas"""
    def __init__(self, parent):
        super().__init__(parent)
        self.jogo = parent
        self.setWindowTitle("📈 RELATÓRIO MULTI-EMPRESAS")
        self.setGeometry(100, 50, 900, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Tab widget para diferentes relatórios
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Aba de ranking
        self.criar_aba_ranking_relatorio(tab_widget)
        
        # Aba para cada empresa
        for nome_empresa in self.jogo.nomes_empresas:
            self.criar_aba_empresa_relatorio(tab_widget, nome_empresa)
    
    def criar_aba_ranking_relatorio(self, tab_widget):
        """Cria aba de ranking no relatório"""
        ranking_widget = QWidget()
        layout = QVBoxLayout(ranking_widget)
        
        text_relatorio = QTextEdit()
        text_relatorio.setReadOnly(True)
        text_relatorio.setStyleSheet("font-family: 'Courier New'; font-size: 11px;")
        layout.addWidget(text_relatorio)
        
        # Gerar relatório de ranking
        relatorio = self.gerar_relatorio_ranking()
        text_relatorio.setPlainText(relatorio)
        
        tab_widget.addTab(ranking_widget, "🏆 RANKING GERAL")
    
    def criar_aba_empresa_relatorio(self, tab_widget, nome_empresa):
        """Cria aba de relatório específico da empresa"""
        empresa_widget = QWidget()
        layout = QVBoxLayout(empresa_widget)
        
        text_relatorio = QTextEdit()
        text_relatorio.setReadOnly(True)
        text_relatorio.setStyleSheet("font-family: 'Courier New'; font-size: 10px;")
        layout.addWidget(text_relatorio)
        
        # Gerar relatório da empresa
        relatorio = self.gerar_relatorio_empresa(nome_empresa)
        text_relatorio.setPlainText(relatorio)
        
        tab_widget.addTab(empresa_widget, f"🏢 {nome_empresa[:10]}")
    
    def gerar_relatorio_ranking(self):
        """Gera relatório geral de ranking"""
        relatorio = f"""
🏭 RELATÓRIO MULTI-EMPRESAS
{'='*70}

📊 SITUAÇÃO GERAL:
• Turno Atual: {self.jogo.turno_atual}/{self.jogo.max_turnos}
• Empresas Participantes: {len(self.jogo.nomes_empresas)}

🏆 RANKING ATUAL:
{'='*40}
"""
        
        # Calcular ranking
        dados_ranking = []
        for nome_empresa in self.jogo.nomes_empresas:
            empresa = self.jogo.empresas[nome_empresa]
            lucro_total = sum(d['lucro'] for d in empresa['historico_decisoes'])
            dados_ranking.append({
                'nome': nome_empresa,
                'lucro_total': lucro_total,
                'dinheiro': empresa['recursos']['dinheiro'],
                'turnos': len(empresa['historico_decisoes'])
            })
        
        dados_ranking.sort(key=lambda x: x['lucro_total'], reverse=True)
        
        for i, dados in enumerate(dados_ranking):
            pos = i + 1
            emoji_pos = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{pos}º"
            
            relatorio += f"\n{emoji_pos} {dados['nome']}:\n"
            relatorio += f"   💰 Lucro Total: ${dados['lucro_total']:,}\n"
            relatorio += f"   💵 Dinheiro Atual: ${dados['dinheiro']:,}\n"
            relatorio += f"   📊 Média/Turno: ${dados['lucro_total']/(max(1, dados['turnos'])):,.2f}\n"
        
        relatorio += f"\n📈 ESTATÍSTICAS GERAIS:\n"
        relatorio += f"{'='*40}\n"
        
        total_lucro = sum(d['lucro_total'] for d in dados_ranking)
        media_geral = total_lucro / len(dados_ranking) if dados_ranking else 0
        
        relatorio += f"• Lucro Total de Todas as Empresas: ${total_lucro:,}\n"
        relatorio += f"• Média de Lucro por Empresa: ${media_geral:,.2f}\n"
        relatorio += f"• Empresa Líder: {dados_ranking[0]['nome'] if dados_ranking else 'N/A'}\n"
        if len(dados_ranking) > 1:
            relatorio += f"• Diferença para 2º Lugar: ${(dados_ranking[0]['lucro_total'] - dados_ranking[1]['lucro_total']):,}\n"
        
        return relatorio
    
    def gerar_relatorio_empresa(self, nome_empresa):
        """Gera relatório específico de uma empresa"""
        empresa = self.jogo.empresas[nome_empresa]
        equipes = empresa['equipes']
        
        relatorio = f"""
🏢 RELATÓRIO DETALHADO - {nome_empresa.upper()}
{'='*60}

👥 EQUIPES:
• Recursos: {equipes['recursos']}
• Produção: {equipes['producao']}
• Finanças: {equipes['financas']}

📊 SITUAÇÃO ATUAL:
• Dinheiro: ${empresa['recursos']['dinheiro']:,}
• Matéria-prima: {empresa['recursos']['materia_prima']}
• Energia: {empresa['recursos']['energia']}
• Trabalhadores: {empresa['recursos']['trabalhadores']}

📈 HISTÓRICO DE DECISÕES:
{'='*40}
"""
        
        lucro_total = 0
        for decisao in empresa['historico_decisoes']:
            relatorio += f"\n🎯 TURNO {decisao['turno']}:\n"
            relatorio += f"  💰 Lucro: ${decisao['lucro']:,}\n"
            relatorio += f"  📦 Produção:\n"
            for produto, qtd in decisao['producao'].items():
                if qtd > 0:
                    relatorio += f"    • {produto}: {qtd} unidades\n"
            lucro_total += decisao['lucro']
        
        relatorio += f"\n💰 RESUMO FINANCEIRO:\n"
        relatorio += f"{'='*40}\n"
        relatorio += f"• Lucro Total Acumulado: ${lucro_total:,}\n"
        relatorio += f"• Turnos Jogados: {len(empresa['historico_decisoes'])}\n"
        relatorio += f"• Média por Turno: ${lucro_total/(max(1, len(empresa['historico_decisoes']))):,.2f}\n"
        
        # Análise de produtos
        if len(empresa['historico_decisoes']) > 0:
            relatorio += f"\n📊 ANÁLISE DE PRODUTOS:\n"
            relatorio += f"{'='*40}\n"
            
            produtos_totais = {}
            for decisao in empresa['historico_decisoes']:
                for produto, qtd in decisao['producao'].items():
                    if produto not in produtos_totais:
                        produtos_totais[produto] = 0
                    produtos_totais[produto] += qtd
            
            for produto, total in produtos_totais.items():
                if total > 0:
                    dados = self.jogo.produtos[produto]
                    receita_total = total * dados['preco_venda']
                    relatorio += f"• {produto}:\n"
                    relatorio += f"  Total produzido: {total} unidades\n"
                    relatorio += f"  Receita gerada: ${receita_total:,}\n"
                    relatorio += f"  Eficiência: {receita_total/total:,.2f} $/unidade\n"
        
        return relatorio


class RelatorioDialog(QDialog):
    """Dialog para mostrar relatório completo"""
    def __init__(self, parent):
        super().__init__(parent)
        self.jogo = parent
        self.setWindowTitle("📈 RELATÓRIO COMPLETO")
        self.setGeometry(200, 100, 700, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        text_relatorio = QTextEdit()
        text_relatorio.setReadOnly(True)
        layout.addWidget(text_relatorio)
        
        # Gerar relatório
        relatorio = self.gerar_relatorio()
        text_relatorio.setPlainText(relatorio)
    
    def gerar_relatorio(self):
        """Gera o texto do relatório"""
        relatorio = f"""
🏭 RELATÓRIO EMPRESARIAL - {self.jogo.nome_empresa.upper()}
{'='*60}

📊 SITUAÇÃO ATUAL:
• Turno: {self.jogo.turno_atual}/{self.jogo.max_turnos}
• Dinheiro: ${self.jogo.recursos['dinheiro']:,}
• Matéria-prima: {self.jogo.recursos['materia_prima']}
• Energia: {self.jogo.recursos['energia']}
• Trabalhadores: {self.jogo.recursos['trabalhadores']}

📈 HISTÓRICO DE DECISÕES:
{'='*40}
"""
        
        lucro_total = 0
        for decisao in self.jogo.historico_decisoes:
            relatorio += f"\n🎯 TURNO {decisao['turno']}:\n"
            relatorio += f"  Lucro: ${decisao['lucro']:,}\n"
            relatorio += f"  Produção:\n"
            for produto, qtd in decisao['producao'].items():
                if qtd > 0:
                    relatorio += f"    • {produto}: {qtd} unidades\n"
            lucro_total += decisao['lucro']
        
        relatorio += f"\n💰 RESUMO FINANCEIRO:\n"
        relatorio += f"{'='*40}\n"
        relatorio += f"• Lucro Total Acumulado: ${lucro_total:,}\n"
        relatorio += f"• Média por Turno: ${lucro_total/(max(1, len(self.jogo.historico_decisoes))):,.2f}\n"
        
        # Análise de eficiência
        if len(self.jogo.historico_decisoes) > 0:
            relatorio += f"\n📊 ANÁLISE DE EFICIÊNCIA:\n"
            relatorio += f"{'='*40}\n"
            
            produtos_totais = {}
            for decisao in self.jogo.historico_decisoes:
                for produto, qtd in decisao['producao'].items():
                    if produto not in produtos_totais:
                        produtos_totais[produto] = 0
                    produtos_totais[produto] += qtd
            
            for produto, total in produtos_totais.items():
                if total > 0:
                    dados = self.jogo.produtos[produto]
                    receita_total = total * dados['preco_venda']
                    relatorio += f"• {produto}:\n"
                    relatorio += f"  Total produzido: {total}\n"
                    relatorio += f"  Receita gerada: ${receita_total:,}\n"
        
        relatorio += f"\n👥 EQUIPES PARTICIPANTES:\n"
        relatorio += f"{'='*40}\n"
        for grupo in [self.jogo.grupo_recursos, self.jogo.grupo_producao, self.jogo.grupo_financas]:
            relatorio += f"• {grupo}\n"
        
        return relatorio


class ModeloMatematicoDialog(QDialog):
    """Dialog para mostrar o modelo matemático"""
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("📐 MODELO MATEMÁTICO DO SISTEMA")
        self.setGeometry(100, 50, 800, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        text_modelo = QTextEdit()
        text_modelo.setReadOnly(True)
        text_modelo.setStyleSheet("font-family: Courier; font-size: 11px;")
        layout.addWidget(text_modelo)
        
        modelo_matematico = """
📐 MODELO MATEMÁTICO DO SIMULADOR EMPRESARIAL
═══════════════════════════════════════════════════════════════

🎯 FUNÇÃO OBJETIVO:
    Maximizar Z = Σ(i=1 a n) [pi × qi] - Σ(j=1 a m) [rj × Σ(i=1 a n) cij × qi]
    
    Onde:
    Z = Lucro total da empresa
    pi = Preço de venda do produto i
    qi = Quantidade produzida do produto i
    cij = Consumo do recurso j para produzir 1 unidade do produto i
    rj = Custo unitário do recurso j

⚖️ RESTRIÇÕES DO SISTEMA:

    1) RESTRIÇÃO DE MATÉRIA-PRIMA:
       Σ(i=1 a n) c1i × qi ≤ R1
       
    2) RESTRIÇÃO DE ENERGIA:
       Σ(i=1 a n) c2i × qi ≤ R2
       
    3) RESTRIÇÃO DE TRABALHADORES:
       Σ(i=1 a n) c3i × qi ≤ R3
       
    4) RESTRIÇÃO DE CAPITAL:
       Σ(i=1 a n) Σ(j=1 a m) cij × rj × qi ≤ D
       
    5) RESTRIÇÕES DE NÃO-NEGATIVIDADE:
       qi ≥ 0, para todo i

📊 VARIÁVEIS DO MODELO:

    🔸 VARIÁVEIS DE DECISÃO:
       q1 = Quantidade de Smartphones a produzir
       q2 = Quantidade de Laptops a produzir  
       q3 = Quantidade de Desktops a produzir

    🔸 PARÂMETROS FIXOS:
       p1 = $180 (preço Smartphone)
       p2 = $350 (preço Laptop)
       p3 = $480 (preço Desktop)

    🔸 MATRIZ DE COEFICIENTES TÉCNICOS:
       
       Recurso          | Smartphone | Laptop | Desktop |
       ─────────────────┼────────────┼────────┼─────────┤
       Matéria-prima    |     45     |   85   |   120   |
       Energia          |     25     |   60   |    80   |
       Trabalhadores    |      3     |    5   |     7   |

     🔸 RECURSOS DISPONÍVEIS (por turno):
         R1 = 2500  (matéria-prima inicial)
         R2 = 3500  (energia inicial)
         R3 = 100   (trabalhadores inicial)
         D  = $50000 (capital inicial)

     🔸 CUSTOS UNITÁRIOS DOS RECURSOS (rj):
         Matéria-prima      → $12,00 por unidade
         Energia            → $0,45 por unidade
         Trabalhadores      → $28,00 por colaborador-hora
         Capital (dinheiro) → $1,00 por dólar disponível

🔄 DINÂMICA TEMPORAL:

    EVOLUÇÃO DOS RECURSOS NO TURNO t:
    
    R1(t+1) = R1(t) - Σ(i=1 a 3) c1i × qi(t)
    R2(t+1) = R2(t) - Σ(i=1 a 3) c2i × qi(t)  
    R3(t+1) = R3(t) - Σ(i=1 a 3) c3i × qi(t)
    D(t+1) = D(t) + Σ(i=1 a 3) pi × qi(t) - Σ(j=1 a m) rj × Σ(i=1 a 3) cij × qi(t)

📈 FUNÇÃO DE PERFORMANCE:

    LUCRO NO TURNO t:
    L(t) = Σ(i=1 a 3) pi × qi(t) - Σ(j=1 a m) rj × Σ(i=1 a 3) cij × qi(t)
    
    LUCRO ACUMULADO ATÉ TURNO T:
    LA(T) = Σ(t=1 a T) L(t)
    
    EFICIÊNCIA DE RECURSOS:
    E(t) = L(t) / [Σ(j=1 a m) rj × Σ(i=1 a 3) cij × qi(t)]

🎲 MODELO ESTOCÁSTICO (Extensão):

    Para cenários avançados, pode-se incluir:
    
    pi(t) = pi × (1 + εi(t))
    
    Onde εi(t) ~ N(0, σ²) representa flutuações de mercado

🧮 ALGORITMO DE SOLUÇÃO:

    1) INPUT: qi para i = 1,2,3
    2) VERIFICAR: Σ cij × qi ≤ Rj para todo j e Σ rj × Σ cij × qi ≤ D
    3) SE viável: CALCULAR custo_total = Σ rj × Σ cij × qi e lucro L(t) = Σ pi × qi - custo_total
    4) ATUALIZAR: Rj(t+1) = Rj(t) - Σ cij × qi
    5) OUTPUT: Novos recursos, custos e lucro

🔍 ANÁLISE DE SENSIBILIDADE:

    ∂Z/∂Rj = λj (multiplicador de Lagrange do recurso j)
    
    Interpretação: valor marginal de uma unidade adicional
    do recurso j para o lucro total.

═══════════════════════════════════════════════════════════════
📚 CONCEITOS APLICADOS:
• Programação Linear
• Otimização com Restrições  
• Análise de Recursos Limitados
• Teoria da Decisão
• Modelagem de Sistemas Produtivos
═══════════════════════════════════════════════════════════════
        """
        
        text_modelo.setPlainText(modelo_matematico)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        jogo = JogoEconomicoImersivo()
        jogo.show()
        sys.exit(app.exec())
    except ImportError as e:
        print("❌ Erro: PySide6 ou matplotlib não instalados!")
        print("Execute: pip install PySide6 matplotlib")
        print(f"Erro específico: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
