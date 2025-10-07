# -*- coding: utf-8 -*-
"""Servidor FastAPI para o portal educacional do jogo."""
from __future__ import annotations

import asyncio
import copy
import socket
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config.constants import GameConfig
from mecanicas import GameMechanics


class WebPortal:
    """Publica informações do jogo via web enquanto a UI PySide6 roda localmente."""

    def __init__(self, jogo) -> None:
        self.jogo = jogo
        self.host = GameConfig.PORTAL_HOST
        self.port = GameConfig.PORTAL_PORT
        self.templates_dir = Path(__file__).resolve().parent / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        self.templates = Jinja2Templates(directory=str(self.templates_dir))
        self.app = self._create_app()
        self._thread: Optional[threading.Thread] = None
        self._server: Optional[uvicorn.Server] = None
        self._network_ip = self._detectar_ip_rede()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start(self) -> None:
        """Inicia o servidor FastAPI em uma thread dedicada."""
        if self._thread and self._thread.is_alive():
            return

        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="warning",
            loop="asyncio",
        )
        self._server = uvicorn.Server(config)

        def _run() -> None:
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._server.serve())

        self._thread = threading.Thread(target=_run, name="WebPortalThread", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Solicita o encerramento do servidor web."""
        if self._server:
            self._server.should_exit = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._thread = None
        self._server = None

    def base_url(self) -> str:
        host = "localhost"
        if self.host not in {"0.0.0.0", "127.0.0.1", "localhost"}:
            host = self.host
        return f"http://{host}:{self.port}"

    def network_url(self) -> str:
        host = self._network_ip or self.host
        if host in {"0.0.0.0", "127.0.0.1"}:
            host = "localhost"
        return f"http://{host}:{self.port}"

    # ------------------------------------------------------------------
    # FastAPI configuration
    # ------------------------------------------------------------------
    def _create_app(self) -> FastAPI:
        app = FastAPI(title=GameConfig.PORTAL_TITLE)

        @app.get("/health")
        async def healthcheck() -> Dict[str, str]:
            return {"status": "ok"}

        @app.get("/", response_class=HTMLResponse)
        async def index(request: Request) -> HTMLResponse:
            contexto = {
                "request": request,
                "portal_title": GameConfig.PORTAL_TITLE,
                "empresas": self._listar_empresas(),
                "constantes": self._constantes_portal(),
            }
            return self.templates.TemplateResponse("index.html", contexto)

        @app.get("/empresa/{slug}", response_class=HTMLResponse)
        async def portal_empresa(request: Request, slug: str) -> HTMLResponse:
            empresa = self._buscar_empresa_por_slug(slug)
            if not empresa:
                raise HTTPException(status_code=404, detail="Empresa não encontrada")
            contexto = {
                "request": request,
                "portal_title": GameConfig.PORTAL_TITLE,
                "empresa": empresa,
                "erro": None,
            }
            return self.templates.TemplateResponse("empresa_login.html", contexto)

        @app.post("/empresa/{slug}", response_class=HTMLResponse)
        async def autenticar_empresa(
            request: Request,
            slug: str,
            senha: str = Form(..., description="Senha de acesso da empresa"),
        ) -> HTMLResponse:
            empresa = self._buscar_empresa_por_slug(slug)
            if not empresa:
                raise HTTPException(status_code=404, detail="Empresa não encontrada")

            senha_correta = empresa.get("portal", {}).get("senha")
            if not senha_correta or senha != senha_correta:
                contexto = {
                    "request": request,
                    "portal_title": GameConfig.PORTAL_TITLE,
                    "empresa": empresa,
                    "erro": "Senha incorreta. Tente novamente.",
                }
                return self.templates.TemplateResponse("empresa_login.html", contexto)

            contexto = self._montar_contexto_empresa(request, empresa)
            return self.templates.TemplateResponse("empresa_dashboard.html", contexto)

        return app

    # ------------------------------------------------------------------
    # Helpers para montar dados
    # ------------------------------------------------------------------
    def _snapshot(self) -> Dict[str, Any]:
        return {
            "iteracao_atual": self.jogo.iteracao_atual,
            "turno_atual": self.jogo.turno_atual,
            "max_iteracoes": self.jogo.max_iteracoes,
            "max_turnos": self.jogo.max_turnos,
            "produtos": copy.deepcopy(self.jogo.produtos),
            "empresas": copy.deepcopy(self.jogo.empresas),
        }

    def _listar_empresas(self) -> List[Dict[str, Any]]:
        snapshot = self._snapshot()
        empresas = []
        for nome, dados in snapshot["empresas"].items():
            portal = dados.get("portal", {})
            if not portal.get("slug"):
                continue
            empresas.append(
                {
                    "nome": nome,
                    "slug": portal["slug"],
                    "senha": portal.get("senha"),
                    "historico": len(dados.get("historico_decisoes", [])),
                }
            )
        empresas.sort(key=lambda item: item["nome"].lower())
        return empresas

    def _buscar_empresa_por_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        snapshot = self._snapshot()
        for nome, dados in snapshot["empresas"].items():
            portal = dados.get("portal", {})
            if portal.get("slug") == slug:
                resultado = copy.deepcopy(dados)
                resultado["nome"] = nome
                resultado["portal"] = portal
                resultado["produtos"] = snapshot["produtos"]
                resultado["iteracao_atual"] = snapshot["iteracao_atual"]
                resultado["turno_atual"] = snapshot["turno_atual"]
                resultado["max_iteracoes"] = snapshot["max_iteracoes"]
                resultado["max_turnos"] = snapshot["max_turnos"]
                return resultado
        return None

    def _montar_contexto_empresa(self, request: Request, empresa: Dict[str, Any]) -> Dict[str, Any]:
        variaveis = empresa.get("variaveis_decisao", {})
        produtos = empresa.get("produtos", {})

        consumo = GameMechanics.calcular_consumo_recursos(produtos, variaveis)
        metricas = GameMechanics.calcular_metricas_plano(produtos, variaveis)

        recursos_disponiveis = empresa.get("recursos_disponiveis", {})
        folgas = []
        for recurso, disponivel in recursos_disponiveis.items():
            gasto = consumo.get(recurso, 0.0)
            folga = disponivel - gasto
            status = "ok"
            if folga < 0:
                status = "deficit"
            elif disponivel and folga / max(disponivel, 1) < 0.1:
                status = "atenção"
            folgas.append(
                {
                    "recurso": recurso,
                    "nome": GameConfig.NOMES_RECURSOS.get(recurso, recurso.title()),
                    "disponivel": disponivel,
                    "consumo": gasto,
                    "folga": folga,
                    "status": status,
                }
            )

        historico_decisoes = empresa.get("historico_decisoes", [])
        historico_recursos = self._montar_historico_recursos(
            empresa.get("historico_recursos", {})
        )

        dicas = self._gerar_dicas(metricas, folgas)

        return {
            "request": request,
            "portal_title": GameConfig.PORTAL_TITLE,
            "empresa": empresa,
            "variaveis_decisao": variaveis,
            "folgas": folgas,
            "metricas": metricas,
            "historico_decisoes": historico_decisoes,
            "historico_recursos": historico_recursos,
            "constantes": self._constantes_portal(),
            "modelo_matematico": GameConfig.get_modelo_matematico(),
            "dicas": dicas,
            "portal_base": self.base_url(),
            "portal_rede": self.network_url(),
        }

    def _montar_historico_recursos(self, historico: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        turnos = historico.get("turnos", [])
        retorno: List[Dict[str, Any]] = []
        for idx, turno in enumerate(turnos):
            retorno.append(
                {
                    "turno": turno,
                    "dinheiro": self._safe_get(historico.get("dinheiro", []), idx),
                    "materia_prima": self._safe_get(historico.get("materia_prima", []), idx),
                    "energia": self._safe_get(historico.get("energia", []), idx),
                    "trabalhadores": self._safe_get(historico.get("trabalhadores", []), idx),
                }
            )
        return retorno

    @staticmethod
    def _safe_get(lista: List[Any], idx: int) -> Any:
        try:
            return lista[idx]
        except IndexError:
            return None

    def _gerar_dicas(self, metricas: Dict[str, float], folgas: List[Dict[str, Any]]) -> List[str]:
        dicas: List[str] = []

        margem = metricas.get("margem", 0.0)
        if margem < 5:
            dicas.append(
                "A margem de lucro está abaixo de 5%. Avalie ajustar preços ou reduzir custos."
            )
        elif margem < 15:
            dicas.append(
                "Margem moderada: revisar alocação de recursos pode elevar o resultado."
            )

        for info in folgas:
            if info["status"] == "deficit":
                dicas.append(
                    f"{info['nome']} está em déficit de {abs(info['folga']):,.0f} unidades. Reduza a produção ou aumente recursos."
                )
            elif info["status"] == "atenção":
                dicas.append(
                    f"{info['nome']} com folga limitada ({info['folga']:,.0f}). Mantenha monitoramento próximo."
                )

        if not dicas:
            dicas.append("Plano atual equilibrado! Continue monitorando o desempenho por turno.")

        return dicas

    @staticmethod
    def _constantes_portal() -> Dict[str, Any]:
        return {
            "recursos_base": GameConfig.RECURSOS_BASE,
            "custos_unitarios": GameConfig.CUSTOS_UNITARIOS_RECURSOS,
            "produtos": GameConfig.get_produtos_inicializados(),
    }

    def _detectar_ip_rede(self) -> str:
        candidatos: List[str] = []
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect(("8.8.8.8", 80))
                candidatos.append(sock.getsockname()[0])
        except OSError:
            pass

        try:
            candidatos.append(socket.gethostbyname(socket.gethostname()))
        except OSError:
            pass

        for ip in candidatos:
            if ip and not ip.startswith("127."):
                return ip

        if candidatos:
            return candidatos[0]

        return "127.0.0.1"