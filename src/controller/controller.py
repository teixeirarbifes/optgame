# -*- coding: utf-8 -*-
"""Controlador da lógica do jogo, desacoplado da camada de UI."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from mecanicas.mechanics import GameMechanics


@dataclass
class TurnoResultado:
    status: str
    relatorio: Optional[str] = None
    jogo_finalizado: bool = False


class GameController:
    """Coordena as operações mecânicas usando o estado exposto pela UI."""

    def __init__(self, ui) -> None:
        self.ui = ui

    def calcular_custo_financeiro_produto(self, produto: str, quantidade: int = 1) -> float:
        return GameMechanics.calcular_custo_financeiro_produto(
            self.ui.produtos, produto, quantidade
        )

    def calcular_custo_total_plano(self, variaveis_decisao) -> float:
        return GameMechanics.calcular_custo_total_plano(
            self.ui.produtos, variaveis_decisao
        )

    def garantir_estruturas_empresa(self, nome_empresa: str) -> None:
        GameMechanics.garantir_estruturas_empresa(self.ui.empresas, nome_empresa)

    def executar_turno(self) -> TurnoResultado:
        ui = self.ui

        tem_producao = any(
            any(qtd > 0 for qtd in (ui.empresas.get(empresa, {}).get("producao_atual", {})).values())
            for empresa in ui.nomes_empresas
        )
        if not tem_producao:
            return TurnoResultado(status="sem_producao")

        if ui.turno_atual > ui.max_turnos:
            return TurnoResultado(status="fim_jogo", jogo_finalizado=True)

        relatorio = f"📊 RELATÓRIO TURNO {ui.turno_atual}\n" + "=" * 50 + "\n"

        for nome_empresa in ui.nomes_empresas:
            self.garantir_estruturas_empresa(nome_empresa)
            empresa = ui.empresas[nome_empresa]
            lucro_turno = 0.0

            relatorio += f"\n🏢 {nome_empresa}:\n"

            producao_atual = empresa.get("producao_atual", {})
            for produto, quantidade in producao_atual.items():
                if quantidade <= 0:
                    continue

                lucro_produto, receita, custo_financeiro = GameMechanics.aplicar_producao(
                    ui.produtos, empresa, produto, quantidade
                )
                if receita or custo_financeiro:
                    relatorio += (
                        f"  • {produto}: {quantidade} unidades → Receita ${receita:,} | "
                        f"Custo ${custo_financeiro:,} | Lucro ${lucro_produto:,}\n"
                    )
                lucro_turno += lucro_produto

            GameMechanics.registrar_historico_turno(
                empresa, ui.turno_atual, lucro_turno
            )

            empresa["producao_atual"] = {}
            relatorio += f"  💰 Lucro: ${lucro_turno:,}\n"

        ui.turno_atual += 1
        ui.iteracao_atual = ui.turno_atual

        relatorio += f"\n🎯 Próximo turno: {ui.turno_atual}\n"

        jogo_finalizado = ui.turno_atual > ui.max_turnos
        return TurnoResultado(
            status="ok", relatorio=relatorio, jogo_finalizado=jogo_finalizado
        )
