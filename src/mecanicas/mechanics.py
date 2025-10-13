# -*- coding: utf-8 -*-
"""Utilidades de lógica do jogo (sem dependências de UI)."""
from __future__ import annotations

from typing import Any, Dict, Tuple


class GameMechanics:
    """Coleção de operações puramente mecânicas do jogo."""

    @staticmethod
    def calcular_custo_financeiro_produto(
        produtos: Dict[str, Dict[str, Any]], produto: str, quantidade: int = 1
    ) -> float:
        """
        Calcula custo financeiro baseado em:
        CUSTO = (consumo_materia × R$1.50) + (consumo_energia × R$0.80) + (consumo_trab × R$25.00)
        """
        from config.constants import GameConfig
        
        dados_produto = produtos.get(produto, {})
        
        # Calcula custo unitário dinamicamente
        consumo_materia = dados_produto.get("consumo_materia", dados_produto.get("custo_materia", 0))
        consumo_energia = dados_produto.get("consumo_energia", dados_produto.get("custo_energia", 0))
        consumo_trab = dados_produto.get("consumo_trabalhadores", dados_produto.get("custo_trabalhadores", 0))
        
        custo_unitario = (
            consumo_materia * GameConfig.CUSTOS_UNITARIOS_RECURSOS.get('materia_prima', 1.5) +
            consumo_energia * GameConfig.CUSTOS_UNITARIOS_RECURSOS.get('energia', 0.8) +
            consumo_trab * GameConfig.CUSTOS_UNITARIOS_RECURSOS.get('trabalhadores', 25.0)
        )
        
        return custo_unitario * max(0, quantidade)

    @staticmethod
    def calcular_custo_total_plano(
        produtos: Dict[str, Dict[str, Any]], variaveis_decisao: Dict[str, int]
    ) -> float:
        custo_total = 0.0
        for produto, quantidade in (variaveis_decisao or {}).items():
            if quantidade and quantidade > 0:
                custo_total += GameMechanics.calcular_custo_financeiro_produto(
                    produtos, produto, quantidade
                )
        return custo_total

    @staticmethod
    def calcular_consumo_recursos(
        produtos: Dict[str, Dict[str, Any]], variaveis_decisao: Dict[str, int]
    ) -> Dict[str, float]:
        """
        Calcula consumo de recursos baseado em:
        consumo_total_recurso = Σ(consumo_recurso_por_unidade × quantidade)
        """
        from config.constants import GameConfig
        
        consumo = {
            "materia_prima": 0.0,
            "energia": 0.0,
            "trabalhadores": 0.0,
            "dinheiro": 0.0,
            "chips_processamento": 0.0,
            "engenheiros_senior": 0.0
        }

        for produto, quantidade in (variaveis_decisao or {}).items():
            if not quantidade or quantidade <= 0:
                continue

            dados = produtos.get(produto, {})
            
            # Consumo físico de recursos
            consumo_materia = dados.get("consumo_materia", dados.get("custo_materia", 0))
            consumo_energia = dados.get("consumo_energia", dados.get("custo_energia", 0))
            consumo_trab = dados.get("consumo_trabalhadores", dados.get("custo_trabalhadores", 0))
            consumo_chips = dados.get("consumo_chips_processamento", 0)
            consumo_eng = dados.get("consumo_engenheiros_senior", 0)
            
            consumo["materia_prima"] += consumo_materia * quantidade
            consumo["energia"] += consumo_energia * quantidade
            consumo["trabalhadores"] += consumo_trab * quantidade
            consumo["chips_processamento"] += consumo_chips * quantidade
            consumo["engenheiros_senior"] += consumo_eng * quantidade
            
            # Custo monetário = consumo × custo_unitário (recursos especializados não têm custo)
            consumo["dinheiro"] += (
                consumo_materia * quantidade * GameConfig.CUSTOS_UNITARIOS_RECURSOS.get('materia_prima', 1.5) +
                consumo_energia * quantidade * GameConfig.CUSTOS_UNITARIOS_RECURSOS.get('energia', 0.8) +
                consumo_trab * quantidade * GameConfig.CUSTOS_UNITARIOS_RECURSOS.get('trabalhadores', 25.0)
            )

        return consumo

    @staticmethod
    def calcular_metricas_plano(
        produtos: Dict[str, Dict[str, Any]], variaveis_decisao: Dict[str, int]
    ) -> Dict[str, float]:
        receita = 0.0
        for produto, quantidade in (variaveis_decisao or {}).items():
            if not quantidade or quantidade <= 0:
                continue
            dados = produtos.get(produto, {})
            receita += dados.get("preco_venda", 0) * quantidade

        custo = GameMechanics.calcular_custo_total_plano(produtos, variaveis_decisao)
        lucro = receita - custo
        margem = (lucro / receita * 100) if receita else 0.0

        return {
            "receita": receita,
            "custo": custo,
            "lucro": lucro,
            "margem": margem,
        }

    @staticmethod
    def garantir_estruturas_empresa(
        empresas: Dict[str, Dict[str, Any]], nome_empresa: str
    ) -> None:
        empresa = empresas.setdefault(nome_empresa, {})
        empresa.setdefault("recursos_disponiveis", {})
        empresa.setdefault("variaveis_decisao", {})
        empresa.setdefault("historico_iteracoes", [])

        historico_recursos = empresa.setdefault("historico_recursos", {})
        historico_recursos.setdefault("turnos", [])
        historico_recursos.setdefault("dinheiro", [])
        historico_recursos.setdefault("materia_prima", [])
        historico_recursos.setdefault("energia", [])
        historico_recursos.setdefault("trabalhadores", [])

        empresa.setdefault("historico_decisoes", [])
        empresa.setdefault("producao_atual", {})
        empresa.setdefault("restricoes_violadas", [])
        empresa.setdefault("objetivo_atual", 0)

    @staticmethod
    def aplicar_producao(
        produtos: Dict[str, Dict[str, Any]],
        empresa: Dict[str, Any],
        produto: str,
        quantidade: int,
    ) -> Tuple[float, float, float]:
        if quantidade <= 0:
            return 0.0, 0.0, 0.0

        dados_produto = produtos.get(produto)
        if not dados_produto:
            return 0.0, 0.0, 0.0

        recursos = empresa.setdefault("recursos_disponiveis", {})

        custo_financeiro = GameMechanics.calcular_custo_financeiro_produto(
            produtos, produto, quantidade
        )

        recursos["dinheiro"] = recursos.get("dinheiro", 0) - custo_financeiro

        for recurso, chave_custo in (
            ("materia_prima", "custo_materia"),
            ("energia", "custo_energia"),
            ("trabalhadores", "custo_trabalhadores"),
        ):
            custo_unitario = dados_produto.get(chave_custo, 0)
            recursos[recurso] = recursos.get(recurso, 0) - custo_unitario * quantidade

        receita = dados_produto.get("preco_venda", 0) * quantidade
        recursos["dinheiro"] = recursos.get("dinheiro", 0) + receita

        lucro = receita - custo_financeiro
        return lucro, receita, custo_financeiro

    @staticmethod
    def registrar_historico_turno(
        empresa: Dict[str, Any], 
        turno: int, 
        lucro_turno: float,
        violacoes: list = None,
        receita: float = 0,
        custo: float = 0,
        consumo: dict = None
    ) -> None:
        historico_recursos = empresa.setdefault("historico_recursos", {})
        recursos_disponiveis = empresa.setdefault("recursos_disponiveis", {})

        historico_recursos.setdefault("turnos", []).append(turno)
        for recurso in ("dinheiro", "materia_prima", "energia", "trabalhadores"):
            historico_recursos.setdefault(recurso, []).append(
                recursos_disponiveis.get(recurso, 0)
            )

        empresa.setdefault("historico_decisoes", []).append(
            {
                "turno": turno,
                "producao": empresa.get("producao_atual", {}).copy(),
                "lucro": lucro_turno,
                "receita": receita,
                "custo": custo,
                "recursos_apos": recursos_disponiveis.copy(),
                "violacoes": violacoes or [],
                "consumo": consumo or {}
            }
        )