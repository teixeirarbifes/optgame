# -*- coding: utf-8 -*-
"""Aplicação Web Flask"""

from flask import Flask, session, g, request, jsonify
from flask_session import Session
import os
import secrets
import hashlib
import time

def create_app():
    """Factory para criar aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_NAME'] = 'optgame_session'
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutos
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    # Inicializar sessão
    Session(app)
    
    # Registrar blueprints
    from .routes import admin_bp, aluno_bp, api_bp, main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(aluno_bp, url_prefix='/aluno')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Middleware para gerenciar heartbeat de sessão
    @app.after_request
    def session_heartbeat(response):
        """Atualizar timestamp de última atividade"""
        if 'empresa_nome' in session or 'admin_autenticado' in session:
            session['last_activity'] = time.time()
        return response
    
    # Context processor para injetar CSRF token em todos os templates
    @app.context_processor
    def inject_csrf_token():
        """Injetar token CSRF em todos os templates"""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        return dict(csrf_token=session.get('csrf_token'))
    
    # Middleware para validar CSRF em requisições AJAX POST/PUT/DELETE
    @app.before_request
    def csrf_protect():
        """Proteção CSRF para requisições AJAX"""
        # Apenas para métodos que modificam dados
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Ignorar rotas de login
            if request.endpoint in ['aluno.login', 'admin.login', 'main.index']:
                return
            
            # Para requisições AJAX
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                token = request.headers.get('X-CSRF-Token')
                
                if not token or token != session.get('csrf_token'):
                    return jsonify({
                        'sucesso': False,
                        'erro': 'Token CSRF inválido',
                        'mensagem': 'Requisição não autorizada. Faça login novamente.'
                    }), 403
    
    # Rate limiting simples (em produção use Flask-Limiter)
    @app.before_request
    def rate_limit():
        """Rate limiting básico por IP"""
        if not hasattr(g, 'rate_limit_storage'):
            g.rate_limit_storage = {}
        
        # Obter IP do cliente
        client_ip = request.remote_addr
        current_time = time.time()
        
        # Limpar registros antigos (mais de 1 minuto)
        g.rate_limit_storage = {
            ip: timestamps 
            for ip, timestamps in g.rate_limit_storage.items() 
            if any(t > current_time - 60 for t in timestamps)
        }
        
        # Adicionar timestamp atual
        if client_ip not in g.rate_limit_storage:
            g.rate_limit_storage[client_ip] = []
        
        g.rate_limit_storage[client_ip].append(current_time)
        
        # Limitar a 100 requisições por minuto
        recent_requests = [t for t in g.rate_limit_storage[client_ip] if t > current_time - 60]
        if len(recent_requests) > 100:
            return jsonify({
                'sucesso': False,
                'erro': 'Rate limit excedido',
                'mensagem': 'Muitas requisições. Aguarde um momento.'
            }), 429
    
    return app
