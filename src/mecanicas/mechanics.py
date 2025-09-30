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
        dados_produto = produtos.get(produto, {})
        custo_unitario = dados_produto.get("custo_dinheiro", 0)
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
        empresa: Dict[str, Any], turno: int, lucro_turno: float
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
                "recursos_apos": recursos_disponiveis.copy(),
            }
        )