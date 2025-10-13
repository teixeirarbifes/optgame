# -*- coding: utf-8 -*-
"""Rotas da aplicação web"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from functools import wraps
import time
import secrets
import hashlib
import uuid
import json
import random
from .game_state import game_state
from config.constants import GameConfig

# Blueprints
main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__)
aluno_bp = Blueprint('aluno', __name__)
api_bp = Blueprint('api', __name__)

# =============================================================================
# SISTEMA DE SEGURANÇA CSRF
# =============================================================================

def gerar_csrf_token():
    """Gera um token CSRF único"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

def validar_csrf_token(token):
    """Valida o token CSRF"""
    return token and session.get('csrf_token') == token

def csrf_required(f):
    """Decorator para validar CSRF em requisições AJAX"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE']:
            token = request.headers.get('X-CSRF-Token') or request.json.get('csrf_token')
            if not validar_csrf_token(token):
                return jsonify({
                    'sucesso': False,
                    'erro': 'Token CSRF inválido',
                    'mensagem': 'Requisição inválida. Recarregue a página.'
                }), 403
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# DECORADORES DE AUTENTICAÇÃO
# =============================================================================

def admin_required(f):
    """Decorator para rotas que requerem autenticação de admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_autenticado'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def empresa_required(f):
    """Decorator para rotas que requerem autenticação de empresa"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        empresa_nome = session.get('empresa_nome')
        login_time = session.get('login_time')
        session_id_server = session.get('session_id')
        session_version_user = session.get('session_version', 0)
        
        # Verificar se está logado
        if not empresa_nome:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'sucesso': False,
                    'erro': 'Não autenticado',
                    'mensagem': 'Faça login para continuar',
                    'redirect': url_for('aluno.login')
                }), 401
            return redirect(url_for('aluno.login'))
        
        # Verificar se a sessão foi invalidada (versão diferente)
        if session_version_user < game_state.session_version:
            session.clear()
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'sucesso': False,
                    'erro': 'Sessão invalidada',
                    'mensagem': 'Sua sessão foi encerrada. Faça login novamente.',
                    'redirect': url_for('aluno.login')
                }), 401
            flash('Sua sessão foi encerrada. Faça login novamente.', 'warning')
            return redirect(url_for('aluno.login'))
        
        # Verificar timeout de sessão (30 minutos)
        if login_time and (time.time() - login_time) > 1800:
            session.clear()
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'sucesso': False,
                    'erro': 'Sessão expirada',
                    'mensagem': 'Sua sessão expirou. Faça login novamente.',
                    'redirect': url_for('aluno.login')
                }), 401
            flash('Sessão expirada. Faça login novamente.', 'warning')
            return redirect(url_for('aluno.login'))
        
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# ROTAS PRINCIPAIS
# =============================================================================

@main_bp.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')

# =============================================================================
# ROTAS ADMINISTRATIVAS
# =============================================================================

@admin_bp.route('/')
def admin_index():
    """Redirect raiz do admin para login ou dashboard"""
    if session.get('admin_autenticado'):
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('admin.login'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login do administrador"""
    if request.method == 'POST':
        senha = request.form.get('senha')
        print(f"DEBUG: Senha recebida: '{senha}'")
        print(f"DEBUG: Senha esperada: '{game_state.admin_password}'")
        print(f"DEBUG: Comparação: {senha == game_state.admin_password}")
        if senha == game_state.admin_password:
            session['admin_autenticado'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Senha incorreta!', 'danger')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Logout do administrador"""
    session.clear()
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Dashboard administrativo"""
    estatisticas = game_state.get_estatisticas_gerais()
    ranking = game_state.get_ranking()
    
    return render_template('admin/dashboard.html',
                         estatisticas=estatisticas,
                         ranking=ranking,
                         empresas=game_state.empresas,
                         produtos=game_state.produtos,
                         recursos_base=GameConfig.RECURSOS_BASE)

@admin_bp.route('/empresas')
@admin_required
def empresas():
    """Gerenciar empresas"""
    return render_template('admin/empresas.html',
                         empresas=game_state.empresas)

@admin_bp.route('/processar-turno', methods=['POST'])
@admin_required
@csrf_required
def processar_turno():
    """Processar turno atual com CSRF"""
    resultado = game_state.processar_turno()
    return jsonify(resultado)

@admin_bp.route('/abrir-iteracao', methods=['POST'])
@admin_required
@csrf_required
def abrir_iteracao():
    """Abrir próxima iteração com CSRF"""
    game_state.abrir_proxima_iteracao()
    return jsonify({'sucesso': True, 'iteracao': game_state.iteracao_atual})

@admin_bp.route('/resetar-jogo', methods=['POST'])
@admin_required
@csrf_required
def resetar_jogo():
    """Resetar o jogo completamente com CSRF (apaga tudo, incluindo empresas)"""
    game_state.reset_game()
    return jsonify({'sucesso': True, 'mensagem': 'Jogo resetado completamente! Todas as empresas foram removidas.'})

@admin_bp.route('/resetar-progresso', methods=['POST'])
@admin_required
@csrf_required
def resetar_progresso():
    """Resetar apenas o progresso (mantém empresas cadastradas)"""
    game_state.resetar_progresso()
    total_empresas = len(game_state.empresas)
    return jsonify({
        'sucesso': True, 
        'mensagem': f'Progresso resetado! {total_empresas} empresa(s) mantida(s).',
        'total_empresas': total_empresas
    })

@admin_bp.route('/invalidar-sessoes', methods=['POST'])
@admin_required
@csrf_required
def invalidar_sessoes():
    """Invalida todas as sessões de empresas (força logout de todos os alunos)"""
    game_state.invalidar_todas_sessoes()
    return jsonify({'sucesso': True, 'mensagem': 'Todas as sessões de empresas foram invalidadas'})

@admin_bp.route('/alterar-senha-empresa', methods=['POST'])
@admin_required
@csrf_required
def alterar_senha_empresa():
    """Alterar senha de uma empresa com CSRF"""
    nome_empresa = request.json.get('nome_empresa')
    nova_senha = request.json.get('nova_senha')
    
    if not nome_empresa or not nova_senha:
        return jsonify({'sucesso': False, 'mensagem': 'Dados incompletos'}), 400
    
    empresa = game_state.empresas.get(nome_empresa)
    if not empresa:
        return jsonify({'sucesso': False, 'mensagem': 'Empresa não encontrada'}), 404
    
    empresa['senha'] = nova_senha
    return jsonify({'sucesso': True, 'mensagem': 'Senha alterada com sucesso!'})

@admin_bp.route('/acessar-como-empresa/<nome_empresa>')
@admin_required
def acessar_como_empresa(nome_empresa):
    """Admin acessa o sistema como se fosse a empresa"""
    empresa = game_state.empresas.get(nome_empresa)
    if not empresa:
        flash('Empresa não encontrada!', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Salvar que é admin acessando como empresa
    session['admin_acessando_como'] = nome_empresa
    session['empresa_nome'] = nome_empresa
    session['session_id'] = str(uuid.uuid4())
    session['session_token'] = secrets.token_hex(32)
    session['login_time'] = time.time()
    session['session_version'] = game_state.session_version
    
    flash(f'Agora você está acessando como: {nome_empresa}', 'info')
    return redirect(url_for('aluno.dashboard'))

# =============================================================================
# GERENCIAMENTO DE SAVES
# =============================================================================

@admin_bp.route('/api/saves/listar')
@admin_required
@csrf_required
def listar_saves():
    """Listar todos os saves disponíveis"""
    saves = game_state.listar_saves()
    return jsonify({'sucesso': True, 'saves': saves})

@admin_bp.route('/api/saves/salvar', methods=['POST'])
@admin_required
@csrf_required
def salvar_save():
    """Salvar estado atual do jogo"""
    nome_arquivo = request.json.get('nome_arquivo')
    sucesso, mensagem, arquivo = game_state.salvar_estado_arquivo(nome_arquivo)
    return jsonify({
        'sucesso': sucesso,
        'mensagem': mensagem,
        'arquivo': arquivo
    })

@admin_bp.route('/api/saves/carregar', methods=['POST'])
@admin_required
@csrf_required
def carregar_save():
    """Carregar um save"""
    nome_arquivo = request.json.get('nome_arquivo')
    
    if not nome_arquivo:
        return jsonify({'sucesso': False, 'mensagem': 'Nome do arquivo não fornecido'}), 400
    
    sucesso, mensagem = game_state.carregar_estado_arquivo(nome_arquivo)
    return jsonify({'sucesso': sucesso, 'mensagem': mensagem})

@admin_bp.route('/api/saves/excluir', methods=['POST'])
@admin_required
@csrf_required
def excluir_save():
    """Excluir um save específico"""
    nome_arquivo = request.json.get('nome_arquivo')
    
    if not nome_arquivo:
        return jsonify({'sucesso': False, 'mensagem': 'Nome do arquivo não fornecido'}), 400
    
    sucesso, mensagem = game_state.excluir_save(nome_arquivo)
    return jsonify({'sucesso': sucesso, 'mensagem': mensagem})

@admin_bp.route('/api/saves/excluir-todos', methods=['POST'])
@admin_required
@csrf_required
def excluir_todos_saves():
    """Excluir todos os saves"""
    if not request.json.get('confirmar'):
        return jsonify({'sucesso': False, 'mensagem': 'Confirmação necessária'}), 400
    
    sucesso, mensagem, quantidade = game_state.excluir_todos_saves()
    return jsonify({
        'sucesso': sucesso,
        'mensagem': mensagem,
        'quantidade': quantidade
    })

@admin_bp.route('/api/saves/download/<nome_arquivo>')
@admin_required
def download_save(nome_arquivo):
    """Download de um save"""
    from flask import send_file
    
    caminho = game_state.obter_caminho_save(nome_arquivo)
    
    if not caminho:
        return jsonify({'sucesso': False, 'mensagem': 'Save não encontrado'}), 404
    
    return send_file(caminho, as_attachment=True, download_name=nome_arquivo)

@admin_bp.route('/api/saves/upload', methods=['POST'])
@admin_required
@csrf_required
def upload_save():
    """Upload e validação de um save"""
    if 'arquivo' not in request.files:
        return jsonify({'sucesso': False, 'mensagem': 'Nenhum arquivo enviado'}), 400
    
    arquivo = request.files['arquivo']
    
    if arquivo.filename == '':
        return jsonify({'sucesso': False, 'mensagem': 'Arquivo sem nome'}), 400
    
    if not arquivo.filename.endswith('.json'):
        return jsonify({'sucesso': False, 'mensagem': 'Apenas arquivos .json são permitidos'}), 400
    
    try:
        # Ler e validar conteúdo
        conteudo = arquivo.read()
        dados_json = json.loads(conteudo)
        
        # Validar estrutura
        valido, mensagem = game_state.validar_save_upload(dados_json)
        
        if not valido:
            return jsonify({'sucesso': False, 'mensagem': f'Save inválido: {mensagem}'}), 400
        
        # Salvar arquivo
        import os
        saves_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saves')
        os.makedirs(saves_dir, exist_ok=True)
        
        # Verificar se arquivo já existe
        nome_original = arquivo.filename
        caminho_arquivo = os.path.join(saves_dir, nome_original)
        
        if os.path.exists(caminho_arquivo):
            return jsonify({
                'sucesso': False,
                'mensagem': f'Já existe um save com o nome "{nome_original}". Renomeie o arquivo antes de fazer upload.',
                'arquivo_existe': True
            }), 409  # 409 Conflict
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_json, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'Save "{arquivo.filename}" enviado e validado com sucesso!',
            'arquivo': arquivo.filename
        })
        
    except json.JSONDecodeError:
        return jsonify({'sucesso': False, 'mensagem': 'Arquivo JSON inválido'}), 400
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': f'Erro ao processar arquivo: {str(e)}'}), 500

@admin_bp.route('/api/saves/auto-save/toggle', methods=['POST'])
@admin_required
@csrf_required
def toggle_auto_save():
    """Ativar/desativar auto-save"""
    data = request.get_json()
    enabled = data.get('enabled', False)
    
    novo_estado = game_state.set_auto_save(enabled)
    status = "ativado" if novo_estado else "desativado"
    
    return jsonify({
        'sucesso': True,
        'mensagem': f'Auto-save {status} com sucesso!',
        'auto_save_enabled': novo_estado
    })

@admin_bp.route('/api/saves/auto-save/status', methods=['GET'])
@admin_required
def get_auto_save_status():
    """Obter status do auto-save"""
    return jsonify({
        'sucesso': True,
        'auto_save_enabled': game_state.get_auto_save_status()
    })

@admin_bp.route('/api/otimizar/<nome_empresa>', methods=['POST'])
@admin_required
@csrf_required
def otimizar_empresa(nome_empresa):
    """Calcular solução ótima para uma empresa"""
    resultado = game_state.calcular_solucao_otima(nome_empresa)
    
    if resultado['sucesso']:
        # Formatar resultado de forma legível
        try:
            from web_app.optimizer import ProductionOptimizer
            optimizer = ProductionOptimizer()
            texto_legivel = optimizer.formatar_resultado_legivel(resultado)
            resultado['texto_legivel'] = texto_legivel
        except:
            pass
    
    return jsonify(resultado)

@admin_bp.route('/api/enviar-otimizacao/<nome_empresa>', methods=['POST'])
@admin_required
@csrf_required
def enviar_otimizacao_empresa(nome_empresa):
    """Enviar solução ótima para a empresa (SEM confirmar) - empresa pode modificar"""
    resultado = game_state.enviar_solucao_para_empresa(nome_empresa)
    
    if resultado['sucesso']:
        # Formatar resultado de forma legível
        try:
            from web_app.optimizer import ProductionOptimizer
            optimizer = ProductionOptimizer()
            
            # Criar dict com resultado completo para formatação
            resultado_completo = {
                'sucesso': True,
                'status': 'Optimal',
                'producao_otima': resultado['producao_otima'],
                'lucro_esperado': resultado['lucro_esperado'],
                'detalhes': resultado['detalhes'],
                'recursos_utilizados': {},
                'recursos_restantes': {}
            }
            
            # Calcular recursos utilizados para exibição
            empresa = game_state.empresas.get(nome_empresa)
            if empresa:
                recursos_utilizados = {'materia_prima': 0, 'energia': 0, 'trabalhadores': 0, 'dinheiro': 0}
                for produto, qtd in resultado['producao_otima'].items():
                    prod_info = game_state.produtos[produto]
                    recursos_utilizados['materia_prima'] += qtd * prod_info['consumo_materia']
                    recursos_utilizados['energia'] += qtd * prod_info['consumo_energia']
                    recursos_utilizados['trabalhadores'] += qtd * prod_info['consumo_trabalhadores']
                
                from config.constants import GameConfig
                recursos_utilizados['dinheiro'] = (
                    recursos_utilizados['materia_prima'] * GameConfig.CUSTOS_UNITARIOS_RECURSOS['materia_prima'] +
                    recursos_utilizados['energia'] * GameConfig.CUSTOS_UNITARIOS_RECURSOS['energia'] +
                    recursos_utilizados['trabalhadores'] * GameConfig.CUSTOS_UNITARIOS_RECURSOS['trabalhadores']
                )
                
                resultado_completo['recursos_utilizados'] = recursos_utilizados
                resultado_completo['recursos_restantes'] = {
                    k: empresa['recursos_disponiveis'][k] - v
                    for k, v in recursos_utilizados.items()
                }
            
            texto_legivel = optimizer.formatar_resultado_legivel(resultado_completo)
            resultado['texto_legivel'] = texto_legivel
        except Exception as e:
            print(f"Erro ao formatar resultado: {e}")
    
    return jsonify(resultado)

@admin_bp.route('/api/aplicar-otimizacao/<nome_empresa>', methods=['POST'])
@admin_required
@csrf_required
def aplicar_otimizacao_empresa(nome_empresa):
    """Aplicar solução ótima E CONFIRMAR automaticamente para uma empresa"""
    resultado = game_state.aplicar_solucao_otima(nome_empresa)
    
    if resultado['sucesso']:
        # Formatar resultado de forma legível
        try:
            from web_app.optimizer import ProductionOptimizer
            optimizer = ProductionOptimizer()
            
            # Criar dict com resultado completo para formatação
            resultado_completo = {
                'sucesso': True,
                'status': 'Optimal',
                'producao_otima': resultado['producao_otima'],
                'lucro_esperado': resultado['lucro_esperado'],
                'detalhes': resultado['detalhes'],
                'recursos_utilizados': {},
                'recursos_restantes': {}
            }
            
            # Calcular recursos utilizados para exibição
            empresa = game_state.empresas.get(nome_empresa)
            if empresa:
                recursos_utilizados = {'materia_prima': 0, 'energia': 0, 'trabalhadores': 0, 'dinheiro': 0}
                for produto, qtd in resultado['producao_otima'].items():
                    prod_info = game_state.produtos[produto]
                    recursos_utilizados['materia_prima'] += qtd * prod_info['consumo_materia']
                    recursos_utilizados['energia'] += qtd * prod_info['consumo_energia']
                    recursos_utilizados['trabalhadores'] += qtd * prod_info['consumo_trabalhadores']
                
                from config.constants import GameConfig
                recursos_utilizados['dinheiro'] = (
                    recursos_utilizados['materia_prima'] * GameConfig.CUSTOS_UNITARIOS_RECURSOS['materia_prima'] +
                    recursos_utilizados['energia'] * GameConfig.CUSTOS_UNITARIOS_RECURSOS['energia'] +
                    recursos_utilizados['trabalhadores'] * GameConfig.CUSTOS_UNITARIOS_RECURSOS['trabalhadores']
                )
                
                resultado_completo['recursos_utilizados'] = recursos_utilizados
                resultado_completo['recursos_restantes'] = {
                    k: empresa['recursos_disponiveis'][k] - v
                    for k, v in recursos_utilizados.items()
                }
            
            texto_legivel = optimizer.formatar_resultado_legivel(resultado_completo)
            resultado['texto_legivel'] = texto_legivel
        except Exception as e:
            print(f"Erro ao formatar resultado: {e}")
    
    return jsonify(resultado)

@admin_bp.route('/api/calcular-otimo-sem-mostrar/<nome_empresa>', methods=['POST'])
@admin_required
@csrf_required
def calcular_otimo_sem_mostrar(nome_empresa):
    """Calcular solução ótima SEM MOSTRAR (apenas GAP%)"""
    resultado = game_state.calcular_otimo_sem_mostrar(nome_empresa)
    return jsonify(resultado)

@admin_bp.route('/api/calcular-otimo-todas', methods=['POST'])
@admin_required
@csrf_required
def calcular_otimo_todas():
    """Calcular solução ótima para TODAS as empresas"""
    resultado = game_state.calcular_otimo_todas_empresas()
    return jsonify(resultado)

@admin_bp.route('/api/enviar-otimo-todas', methods=['POST'])
@admin_required
@csrf_required
def enviar_otimo_todas():
    """Enviar solução ótima para TODAS as empresas (SEM confirmar)"""
    resultado = game_state.enviar_otimo_todas_empresas()
    return jsonify(resultado)

@admin_bp.route('/api/aplicar-otimo-todas', methods=['POST'])
@admin_required
@csrf_required
def aplicar_otimo_todas():
    """Aplicar E CONFIRMAR solução ótima em TODAS as empresas (GAP 0%)"""
    resultado = game_state.aplicar_otimo_todas_empresas()
    return jsonify(resultado)

@admin_bp.route('/api/toggle-calcular-otimo-ao-criar', methods=['POST'])
@admin_required
@csrf_required
def toggle_calcular_otimo_ao_criar():
    """Ativar/desativar cálculo automático de ótimo ao criar empresa"""
    data = request.get_json()
    enabled = data.get('enabled', False)
    
    game_state.calcular_otimo_ao_criar = enabled
    status = "ativado" if enabled else "desativado"
    
    return jsonify({
        'sucesso': True,
        'mensagem': f'Cálculo automático de ótimo ao criar empresa {status}!',
        'calcular_otimo_ao_criar': game_state.calcular_otimo_ao_criar
    })

@admin_bp.route('/api/status-calcular-otimo-ao-criar', methods=['GET'])
@admin_required
def get_status_calcular_otimo_ao_criar():
    """Obter status do cálculo automático ao criar"""
    return jsonify({
        'sucesso': True,
        'calcular_otimo_ao_criar': game_state.calcular_otimo_ao_criar
    })

# =============================================================================
# ROTAS DOS ALUNOS
# =============================================================================

@aluno_bp.route('/')
def aluno_index():
    """Sempre redireciona para login (sem persistência)"""
    return redirect(url_for('aluno.login'))

@aluno_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login dos alunos (empresas) - AJAX apenas"""
    if request.method == 'POST':
        # Aceitar JSON para AJAX
        if request.is_json:
            data = request.json
            nome = data.get('nome')
            senha = data.get('senha')
            
            if game_state.autenticar_empresa(nome, senha):
                # Criar token de sessão temporário único
                session_id = str(uuid.uuid4())
                session_token = secrets.token_hex(32)
                session['empresa_nome'] = nome
                session['session_token'] = session_token
                session['session_id'] = session_id
                session['login_time'] = time.time()
                session['session_version'] = game_state.session_version
                
                return jsonify({
                    'sucesso': True,
                    'mensagem': 'Login realizado com sucesso!',
                    'empresa': nome,
                    'session_id': session_id,
                    'redirect': url_for('aluno.dashboard')
                })
            else:
                return jsonify({
                    'sucesso': False,
                    'mensagem': 'Nome da empresa ou senha incorretos!'
                }), 401
        
        # Fallback para POST tradicional (compatibilidade)
        nome = request.form.get('nome')
        senha = request.form.get('senha')
        
        if game_state.autenticar_empresa(nome, senha):
            session_id = str(uuid.uuid4())
            session['empresa_nome'] = nome
            session['session_token'] = secrets.token_hex(32)
            session['session_id'] = session_id
            session['login_time'] = time.time()
            session['session_version'] = game_state.session_version
            return redirect(url_for('aluno.dashboard'))
        else:
            flash('Nome da empresa ou senha incorretos!', 'danger')
    
    empresas_list = list(game_state.empresas.keys())
    return render_template('aluno/login.html', empresas=empresas_list)

@aluno_bp.route('/logout')
def logout():
    """Logout da empresa - Limpa sessão e sessionStorage"""
    session.clear()
    return render_template('aluno/logout.html')

@aluno_bp.route('/dashboard')
@empresa_required
def dashboard():
    """Dashboard da empresa"""
    nome_empresa = session.get('empresa_nome')
    empresa = game_state.empresas.get(nome_empresa)
    
    if not empresa:
        session.pop('empresa_nome', None)
        return redirect(url_for('aluno.login'))
    
    # Não mais exibimos métricas projetadas - alunos devem calcular manualmente
    return render_template('aluno/dashboard.html',
                         empresa=empresa,
                         produtos=game_state.produtos,
                         iteracao_atual=game_state.iteracao_atual,
                         iteracao_aberta=game_state.iteracao_aberta)

@aluno_bp.route('/api/estado', methods=['GET'])
@empresa_required
def api_estado():
    """API: Retorna estado atual do jogo para AJAX"""
    nome_empresa = session.get('empresa_nome')
    empresa = game_state.empresas.get(nome_empresa)
    
    if not empresa:
        return jsonify({'erro': 'Empresa não encontrada'}), 404
    
    # Pegar decisão anterior (último histórico ou decisão atual)
    decisao_anterior = {}
    if empresa.get('historico') and len(empresa['historico']) > 0:
        decisao_anterior = empresa['historico'][-1].get('decisao', {})
    
    return jsonify({
        'iteracao_atual': game_state.iteracao_atual,
        'iteracao_aberta': game_state.iteracao_aberta,
        'recursos': empresa.get('recursos_disponiveis', {}),
        'recursos_base': empresa.get('recursos_base', GameConfig.RECURSOS_BASE),
        'recursos_maximos': GameConfig.RECURSOS_BASE,
        'lucro_ultimo_turno': empresa.get('lucro_ultimo_turno', 0),
        'decisao_anterior': decisao_anterior,
        'decisao_atual': empresa.get('decisao_atual', {}),  # Decisão atual (confirmada ou não)
        'decisao_confirmada': empresa.get('decisao_confirmada', False),
        'decisoes_nao_confirmadas': empresa.get('decisoes_nao_confirmadas', {}),
        'historico': empresa.get('historico', [])
    })

@aluno_bp.route('/enviar-decisao', methods=['POST'])
@empresa_required
@csrf_required
def enviar_decisao():
    """Enviar decisão de produção - AJAX apenas com CSRF"""
    nome_empresa = session.get('empresa_nome')
    
    if not game_state.iteracao_aberta:
        return jsonify({
            'sucesso': False, 
            'mensagem': 'Iteração fechada para envios'
        }), 400
    
    # Aceitar JSON para AJAX
    if request.is_json:
        decisoes = request.json.get('decisoes', {})
        print(f"\n=== RECEBENDO DECISAO VIA JSON ===")
        print(f"Empresa: {nome_empresa}")
        print(f"Dados recebidos: {request.json}")
        print(f"Decisoes extraidas: {decisoes}")
    else:
        # Fallback para form data (compatibilidade)
        decisoes = {}
        for produto in game_state.produtos.keys():
            quantidade = request.form.get(f'produto_{produto}', 0)
            try:
                quantidade = float(quantidade)  # Aceita valores decimais
                if quantidade >= 0:
                    decisoes[produto] = round(quantidade, 2)  # Arredonda para 2 casas decimais
            except:
                decisoes[produto] = 0
    
    # Validar formato
    if not isinstance(decisoes, dict):
        return jsonify({
            'sucesso': False,
            'mensagem': 'Formato de decisões inválido'
        }), 400
    
    # Validar que decisoes não está vazio
    if not decisoes:
        print(f"ERRO: Decisoes vazia!")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Nenhuma decisão foi enviada'
        }), 400
    
    # Registra a decisão SEM VALIDAR (mesmo que viole recursos)
    empresa = game_state.empresas.get(nome_empresa)
    if not empresa:
        return jsonify({
            'sucesso': False,
            'mensagem': 'Empresa não encontrada'
        }), 404
    
    empresa['decisao_atual'] = decisoes
    empresa['decisao_confirmada'] = True
    
    print(f"Decisao registrada com sucesso: {decisoes}")
    
    return jsonify({
        'sucesso': True, 
        'mensagem': 'Decisão registrada com sucesso! Aguarde o professor processar o turno para ver os resultados.'
    })

# =============================================================================
# API REST
# =============================================================================

@api_bp.route('/status')
def status():
    """Status geral do jogo"""
    return jsonify(game_state.get_estatisticas_gerais())

@api_bp.route('/ranking')
def ranking():
    """Ranking de empresas com status de decisão"""
    empresas_ranking = game_state.get_ranking()
    
    # Adicionar informação de decisão_confirmada e histórico de lucros
    for emp in empresas_ranking:
        empresa_data = game_state.empresas.get(emp['nome'], {})
        emp['decisao_confirmada'] = empresa_data.get('decisao_confirmada', False)
        emp['historico_lucros'] = empresa_data.get('historico_lucros', {'turnos': [], 'valores': []})
    
    return jsonify(empresas_ranking)

@api_bp.route('/empresa/<nome>')
@empresa_required
def dados_empresa(nome):
    """Dados de uma empresa específica"""
    empresa = game_state.empresas.get(nome)
    if not empresa or session.get('empresa_nome') != nome:
        return jsonify({'erro': 'Não autorizado'}), 403
    
    return jsonify(empresa)

@api_bp.route('/produtos')
def produtos():
    """Lista de produtos disponíveis"""
    return jsonify(game_state.produtos)

@api_bp.route('/csrf-token')
def obter_csrf_token():
    """Retorna o token CSRF para uso em requisições AJAX"""
    return jsonify({'csrf_token': gerar_csrf_token()})

@api_bp.route('/admin/criar-empresa', methods=['POST'])
@admin_required
@csrf_required
def criar_empresa():
    """Criar nova empresa com proteção CSRF"""
    data = request.json
    nome = data.get('nome')
    equipe = data.get('equipe')
    senha = data.get('senha')
    
    if not nome or not senha:
        return jsonify({'sucesso': False, 'mensagem': 'Nome e senha são obrigatórios'})
    
    sucesso = game_state.adicionar_empresa(nome, equipe or '', senha)
    
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': f'Empresa {nome} criada com sucesso'})
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Empresa já existe'})

@api_bp.route('/admin/remover-empresa/<nome>', methods=['DELETE'])
@admin_required
@csrf_required
def remover_empresa(nome):
    """Remover empresa com proteção CSRF"""
    if nome in game_state.empresas:
        del game_state.empresas[nome]
        return jsonify({'sucesso': True})
    return jsonify({'sucesso': False, 'mensagem': 'Empresa não encontrada'})

@admin_bp.route('/api/gerar-modelo-default', methods=['POST'])
@admin_required
@csrf_required
def gerar_modelo_default():
    """Gerar modelo default otimizando parâmetros do jogo para produção fixa"""
    dados = request.get_json()
    
    if not dados:
        return jsonify({'sucesso': False, 'mensagem': 'Dados não fornecidos'}), 400
    
    producao_esperada = dados.get('producao_esperada', {})
    parametros_principais = dados.get('parametros_principais', {})
    aplicar_para = dados.get('aplicar_para', 'nova')
    
    if not producao_esperada:
        return jsonify({'sucesso': False, 'mensagem': 'Produção esperada não definida'}), 400
    
    try:
        # Validar produtos
        produtos_validos = set(game_state.produtos.keys())
        for produto in producao_esperada.keys():
            if produto not in produtos_validos:
                return jsonify({'sucesso': False, 'mensagem': f'Produto inválido: {produto}'}), 400
        
        # Usar recursos base realistas (limitar dentro de faixas sensatas)
        recursos_alvo = {
            'dinheiro': max(50000, min(500000, parametros_principais.get('dinheiro', 50000))),
            'materia_prima': max(10000, min(100000, parametros_principais.get('materia_prima', 20000))),
            'energia': max(10000, min(100000, parametros_principais.get('energia', 15000))),
            'trabalhadores': max(300, min(5000, parametros_principais.get('trabalhadores', 600)))
        }
        
        # Definir perfis únicos e bem diferenciados por produto
        perfis_produtos = {
            'Camera': {'prioridade_materia': 0.4, 'prioridade_energia': 0.3, 'prioridade_trabalho': 0.3},
            'Desktop': {'prioridade_materia': 0.5, 'prioridade_energia': 0.4, 'prioridade_trabalho': 0.1},
            'Impressora': {'prioridade_materia': 0.3, 'prioridade_energia': 0.2, 'prioridade_trabalho': 0.5},
            'Laptop': {'prioridade_materia': 0.45, 'prioridade_energia': 0.35, 'prioridade_trabalho': 0.2},
            'Smartphone': {'prioridade_materia': 0.25, 'prioridade_energia': 0.5, 'prioridade_trabalho': 0.25},
            'Smartwatch': {'prioridade_materia': 0.2, 'prioridade_energia': 0.3, 'prioridade_trabalho': 0.5}
        }
        
        # Otimizar custos usando abordagem reversa
        custos_otimizados = {}
        
        # Primeira passada: distribuir recursos base proporcionalmente
        total_producao_ponderada = {
            'materia_prima': 0,
            'energia': 0,
            'trabalhadores': 0
        }
        
        # Calcular total ponderado por prioridades
        for produto, quantidade in producao_esperada.items():
            perfil = perfis_produtos.get(produto, {'prioridade_materia': 0.33, 'prioridade_energia': 0.33, 'prioridade_trabalho': 0.34})
            total_producao_ponderada['materia_prima'] += quantidade * perfil['prioridade_materia']
            total_producao_ponderada['energia'] += quantidade * perfil['prioridade_energia']  
            total_producao_ponderada['trabalhadores'] += quantidade * perfil['prioridade_trabalho']
        
        # Recursos disponíveis para distribuir (85% para dar margem)
        recursos_distribuir = {
            'materia_prima': int(recursos_alvo['materia_prima'] * 0.85),
            'energia': int(recursos_alvo['energia'] * 0.85),
            'trabalhadores': int(recursos_alvo['trabalhadores'] * 0.85)
        }
        
        # Calcular recursos disponíveis para distribuição
        recursos_distribuir = {
            'materia_prima': int(recursos_alvo['materia_prima'] * 0.85),
            'energia': int(recursos_alvo['energia'] * 0.85),
            'trabalhadores': int(recursos_alvo['trabalhadores'] * 0.85)
        }
        
        # Definir multiplicadores para todos os produtos
        multiplicadores = {
            'Camera': {'materia': 1.5, 'energia': 1.2, 'trabalho': 1.8},
            'Desktop': {'materia': 2.0, 'energia': 1.8, 'trabalho': 0.8},
            'Impressora': {'materia': 1.3, 'energia': 0.9, 'trabalho': 2.2},
            'Laptop': {'materia': 1.7, 'energia': 1.4, 'trabalho': 1.1},
            'Smartphone': {'materia': 0.8, 'energia': 2.0, 'trabalho': 1.0},
            'Smartwatch': {'materia': 0.6, 'energia': 1.1, 'trabalho': 2.5}
        }
        
        # Calcular consumo base para produtos da produção esperada (eficientes)
        produtos_esperados = set(producao_esperada.keys())
        produtos_todos = set(game_state.produtos.keys())
        produtos_nao_esperados = produtos_todos - produtos_esperados
        
        # Primeiro: calcular custos para produtos ESPERADOS (eficientes)
        for produto, quantidade in producao_esperada.items():
            perfil = perfis_produtos.get(produto, {'prioridade_materia': 0.33, 'prioridade_energia': 0.33, 'prioridade_trabalho': 0.34})
            
            # Calcular consumo por unidade baseado na proporção e prioridade
            consumo_materia_total = (recursos_distribuir['materia_prima'] * quantidade * perfil['prioridade_materia']) / total_producao_ponderada['materia_prima']
            consumo_energia_total = (recursos_distribuir['energia'] * quantidade * perfil['prioridade_energia']) / total_producao_ponderada['energia']
            consumo_trabalhadores_total = (recursos_distribuir['trabalhadores'] * quantidade * perfil['prioridade_trabalho']) / total_producao_ponderada['trabalhadores']
            
            # Consumo por unidade (permitir decimais)
            consumo_materia_unit = max(5.0, consumo_materia_total / quantidade)
            consumo_energia_unit = max(3.0, consumo_energia_total / quantidade)
            consumo_trabalhadores_unit = max(1.0, consumo_trabalhadores_total / quantidade)
            
            mult = multiplicadores.get(produto, {'materia': 1.0, 'energia': 1.0, 'trabalho': 1.0})
            
            # Aplicar multiplicadores e adicionar variação aleatória pequena
            variacao = random.uniform(0.9, 1.1)  # ±10% de variação
            
            custos_otimizados[produto] = {
                'consumo_materia': max(5.0, min(100.0, round(consumo_materia_unit * mult['materia'] * variacao, 1))),
                'consumo_energia': max(3.0, min(80.0, round(consumo_energia_unit * mult['energia'] * variacao, 1))),
                'consumo_trabalhadores': max(1.0, min(20.0, round(consumo_trabalhadores_unit * mult['trabalho'] * variacao, 1))),
                'preco_venda': game_state.produtos[produto]['preco_venda']  # Manter preço original
            }
        
        # Segundo: calcular custos para produtos NÃO ESPERADOS (menos eficientes)
        for produto in produtos_nao_esperados:
            # Usar perfis similares mas com penalidade de eficiência
            mult_base = multiplicadores.get(produto, {'materia': 1.0, 'energia': 1.0, 'trabalho': 1.0})
            
            # Tornar produtos não esperados menos eficientes (mais caros)
            penalidade_eficiencia = random.uniform(1.3, 1.8)  # 30% a 80% mais caro
            variacao = random.uniform(0.9, 1.2)  # Mais variação
            
            # Custos base mais altos para produtos não esperados
            custos_otimizados[produto] = {
                'consumo_materia': max(8.0, min(120.0, round(25.0 * mult_base['materia'] * penalidade_eficiencia * variacao, 1))),
                'consumo_energia': max(6.0, min(100.0, round(18.0 * mult_base['energia'] * penalidade_eficiencia * variacao, 1))),
                'consumo_trabalhadores': max(2.0, min(25.0, round(8.0 * mult_base['trabalho'] * penalidade_eficiencia * variacao, 1))),
                'preco_venda': game_state.produtos[produto]['preco_venda']  # Manter preço original
            }
        
        # Calcular consumo total real com os custos otimizados (TODOS os produtos)
        recursos_utilizados = {
            'materia_prima': 0,
            'energia': 0,
            'trabalhadores': 0,
            'dinheiro': 0
        }
        
        # Calcular apenas para produtos esperados (que devem ser produzidos)
        for produto, quantidade in producao_esperada.items():
            recursos_utilizados['materia_prima'] += quantidade * custos_otimizados[produto]['consumo_materia']
            recursos_utilizados['energia'] += quantidade * custos_otimizados[produto]['consumo_energia']
            recursos_utilizados['trabalhadores'] += quantidade * custos_otimizados[produto]['consumo_trabalhadores']
        
        # Calcular custo em dinheiro
        recursos_utilizados['dinheiro'] = (
            recursos_utilizados['materia_prima'] * GameConfig.CUSTOS_UNITARIOS_RECURSOS['materia_prima'] +
            recursos_utilizados['energia'] * GameConfig.CUSTOS_UNITARIOS_RECURSOS['energia'] +
            recursos_utilizados['trabalhadores'] * GameConfig.CUSTOS_UNITARIOS_RECURSOS['trabalhadores']
        )
        
        # Ajustar recursos alvo para garantir que a produção seja exatamente atingível
        # Adicionar margem de 15% para garantir viabilidade
        recursos_finais = {
            'materia_prima': int(recursos_utilizados['materia_prima'] * 1.15),
            'energia': int(recursos_utilizados['energia'] * 1.15),
            'trabalhadores': int(recursos_utilizados['trabalhadores'] * 1.15),
            'dinheiro': int(recursos_utilizados['dinheiro'] * 1.15)
        }
        
        # CALIBRAÇÃO ITERATIVA: Ajustar até convergir na produção esperada
        max_iteracoes = 5  # Máximo de iterações para evitar loop infinito
        tolerancia = 0.03  # 3% de tolerância na produção
        
        for iteracao in range(max_iteracoes):
            try:
                from web_app.optimizer import ProductionOptimizer
                
                # Testar otimização com custos atuais
                optimizer = ProductionOptimizer()
                resultado_teste = optimizer.otimizar_producao(recursos_finais, produtos_customizados=custos_otimizados)
                
                if not resultado_teste.get('sucesso'):
                    print(f"Iteração {iteracao + 1}: Otimização falhou")
                    break
                
                producao_otima_teste = resultado_teste['producao_otima']
                
                # Verificar convergência
                todos_convergidos = True
                ajustes_realizados = {}
                
                for produto, quantidade_esperada in producao_esperada.items():
                    quantidade_otima = producao_otima_teste.get(produto, 0)
                    diferenca_percentual = abs(quantidade_otima - quantidade_esperada) / max(quantidade_esperada, 1)
                    
                    print(f"Iteração {iteracao + 1} - {produto}: esperado={quantidade_esperada}, otimo={quantidade_otima}, diff={diferenca_percentual:.3f}")
                    
                    if diferenca_percentual > tolerancia:
                        todos_convergidos = False
                        
                        # Calcular fator de ajuste mais suave
                        fator_erro = quantidade_esperada / max(quantidade_otima, 0.1)
                        
                        # Ajuste adaptativo baseado na magnitude do erro
                        if diferenca_percentual > 0.2:  # Erro grande (>20%)
                            intensidade_ajuste = 0.15  # Ajuste mais agressivo
                        elif diferenca_percentual > 0.1:  # Erro médio (>10%)
                            intensidade_ajuste = 0.08  # Ajuste moderado
                        else:  # Erro pequeno (>3%)
                            intensidade_ajuste = 0.03  # Ajuste suave
                        
                        if fator_erro > 1:  # Precisa produzir mais - reduzir custos
                            fator_ajuste = 1 - intensidade_ajuste
                        else:  # Produzindo demais - aumentar custos
                            fator_ajuste = 1 + intensidade_ajuste
                        
                        # Aplicar ajuste
                        custos_otimizados[produto]['consumo_materia'] = round(custos_otimizados[produto]['consumo_materia'] * fator_ajuste, 1)
                        custos_otimizados[produto]['consumo_energia'] = round(custos_otimizados[produto]['consumo_energia'] * fator_ajuste, 1) 
                        custos_otimizados[produto]['consumo_trabalhadores'] = round(custos_otimizados[produto]['consumo_trabalhadores'] * fator_ajuste, 1)
                        
                        ajustes_realizados[produto] = fator_ajuste
                
                print(f"Iteração {iteracao + 1}: Ajustes realizados: {ajustes_realizados}")
                
                # Se todos convergidos, parar
                if todos_convergidos:
                    print(f"Convergência atingida na iteração {iteracao + 1}!")
                    break
                
                # Recalcular recursos utilizados após ajustes
                recursos_utilizados = {
                    'materia_prima': 0,
                    'energia': 0,
                    'trabalhadores': 0,
                    'dinheiro': 0
                }
                
                for produto, quantidade in producao_esperada.items():
                    recursos_utilizados['materia_prima'] += quantidade * custos_otimizados[produto]['consumo_materia']
                    recursos_utilizados['energia'] += quantidade * custos_otimizados[produto]['consumo_energia']
                    recursos_utilizados['trabalhadores'] += quantidade * custos_otimizados[produto]['consumo_trabalhadores']
                
                recursos_utilizados['dinheiro'] = (
                    recursos_utilizados['materia_prima'] * GameConfig.CUSTOS_UNITARIOS_RECURSOS['materia_prima'] +
                    recursos_utilizados['energia'] * GameConfig.CUSTOS_UNITARIOS_RECURSOS['energia'] +
                    recursos_utilizados['trabalhadores'] * GameConfig.CUSTOS_UNITARIOS_RECURSOS['trabalhadores']
                )
                
                # Atualizar recursos finais
                recursos_finais = {
                    'materia_prima': int(recursos_utilizados['materia_prima'] * 1.15),
                    'energia': int(recursos_utilizados['energia'] * 1.15),
                    'trabalhadores': int(recursos_utilizados['trabalhadores'] * 1.15),
                    'dinheiro': int(recursos_utilizados['dinheiro'] * 1.15)
                }
            
            except Exception as e:
                print(f"Erro na iteração {iteracao + 1}: {e}")
                break
        
        print(f"Calibração finalizada após {min(iteracao + 1, max_iteracoes)} iterações")
        
        # Calcular receita total esperada
        receita_total = sum(
            quantidade * custos_otimizados[produto]['preco_venda'] 
            for produto, quantidade in producao_esperada.items()
        )
        
        lucro_esperado = receita_total - recursos_utilizados['dinheiro']
        
        # Modelo gerado
        modelo = {
            'producao_fixa': producao_esperada,
            'parametros_otimizados': recursos_finais,
            'custos_produtos_otimizados': custos_otimizados,
            'recursos_utilizados': recursos_utilizados,
            'receita_esperada': receita_total,
            'lucro_esperado': lucro_esperado,
            'timestamp': time.time()
        }
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Modelo gerado com sucesso - parâmetros otimizados para cenário realista',
            'modelo': modelo,
            'aplicar_para': aplicar_para
        })
        
    except Exception as e:
        return jsonify({
            'sucesso': False, 
            'mensagem': f'Erro ao gerar modelo: {str(e)}'
        }), 500

@admin_bp.route('/api/aplicar-modelo-default', methods=['POST'])
@admin_required
@csrf_required
def aplicar_modelo_default():
    """Aplicar modelo default gerado"""
    dados = request.get_json()
    
    if not dados:
        return jsonify({'sucesso': False, 'mensagem': 'Dados não fornecidos'}), 400
    
    modelo = dados.get('modelo')
    aplicar_para = dados.get('aplicar_para', 'nova')
    
    if not modelo:
        return jsonify({'sucesso': False, 'mensagem': 'Modelo não fornecido'}), 400
    
    try:
        parametros_otimizados = modelo['parametros_otimizados']
        producao_fixa = modelo['producao_fixa']
        custos_produtos = modelo.get('custos_produtos_otimizados')
        
        aplicadas = 0
        erros = []
        
        if aplicar_para == 'todas':
            # Aplicar para todas empresas existentes
            for nome_empresa in game_state.empresas.keys():
                if _aplicar_modelo_empresa(nome_empresa, parametros_otimizados, producao_fixa, custos_produtos):
                    aplicadas += 1
                else:
                    erros.append(f'Erro ao aplicar para {nome_empresa}')
            
            mensagem = f'Modelo aplicado para {aplicadas} empresas'
            
        elif aplicar_para == 'nova':
            # Salvar como modelo default para próximas empresas
            game_state.modelo_default = {
                'recursos_base': parametros_otimizados,
                'producao_sugerida': producao_fixa,
                'custos_produtos_otimizados': custos_produtos,
                'ativo': True
            }
            mensagem = 'Modelo salvo como default para próximas empresas'
            
        else:
            # Aplicar para empresa específica
            if aplicar_para in game_state.empresas:
                if _aplicar_modelo_empresa(aplicar_para, parametros_otimizados, producao_fixa, custos_produtos):
                    aplicadas = 1
                    mensagem = f'Modelo aplicado para {aplicar_para}'
                else:
                    erros.append(f'Erro ao aplicar para {aplicar_para}')
                    mensagem = 'Erro ao aplicar modelo'
            else:
                return jsonify({'sucesso': False, 'mensagem': 'Empresa não encontrada'}), 400
        
        if erros:
            mensagem += f'. Erros: {"; ".join(erros)}'
        
        return jsonify({
            'sucesso': True,
            'mensagem': mensagem,
            'empresas_aplicadas': aplicadas,
            'erros': erros
        })
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao aplicar modelo: {str(e)}'
        }), 500

def _aplicar_modelo_empresa(nome_empresa, parametros_otimizados, producao_fixa, custos_produtos=None):
    """Aplicar modelo para uma empresa específica (função auxiliar)"""
    try:
        empresa = game_state.empresas[nome_empresa]
        
        # Atualizar recursos base
        empresa['recursos_base'] = parametros_otimizados.copy()
        empresa['recursos_disponiveis'] = parametros_otimizados.copy()
        
        # Aplicar produção fixa como decisão atual (não confirmada)
        empresa['decisao_atual'] = producao_fixa.copy()
        empresa['decisao_confirmada'] = False
        
        # Aplicar custos otimizados de produtos se fornecidos
        if custos_produtos:
            if 'produtos_customizados' not in empresa:
                empresa['produtos_customizados'] = {}
            empresa['produtos_customizados'] = custos_produtos.copy()
        
        # Marcar como tendo modelo aplicado
        empresa['modelo_aplicado'] = {
            'timestamp': time.time(),
            'parametros': parametros_otimizados,
            'producao': producao_fixa,
            'custos_produtos': custos_produtos
        }
        
        return True
    except Exception:
        return False

# Rota de validação removida - alunos devem enviar decisão sem pré-visualização
# Resultados são revelados apenas após o professor processar o turno
# @api_bp.route('/validar-decisao', methods=['POST'])
# @empresa_required
# def validar_decisao():
#     """Validar decisão manualmente"""
#     pass
