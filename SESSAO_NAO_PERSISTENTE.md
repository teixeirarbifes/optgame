# 🔒 Sistema de Sessão Não-Persistente

## 📋 Como Funciona

### Conceito
O sistema usa **sessionStorage** do navegador combinado com validação no servidor para garantir que a sessão seja **realmente não-persistente** - ou seja, ao recarregar a página, o usuário deve fazer login novamente.

---

## 🔐 Fluxo de Autenticação

### 1. **Login do Aluno**
**Arquivo:** `src/web_app/routes.py` - Função `login()`

```python
if game_state.autenticar_empresa(nome, senha):
    # Gerar UUID único para esta sessão
    session_id = str(uuid.uuid4())
    
    # Salvar no servidor
    session['empresa_nome'] = nome
    session['session_id'] = session_id
    session['login_time'] = time.time()
    
    # Retornar session_id para o cliente
    return jsonify({
        'sucesso': True,
        'session_id': session_id,  # Cliente vai salvar isso
        'redirect': '/aluno/dashboard'
    })
```

**Arquivo:** `src/web_app/templates/aluno/login.html`

```javascript
$.ajax({
    url: '/aluno/login',
    method: 'POST',
    data: JSON.stringify({ nome, senha }),
    success: function(response) {
        if (response.sucesso) {
            // Salvar no sessionStorage (NÃO no localStorage)
            sessionStorage.setItem('optgame_session_id', response.session_id);
            
            // Redirecionar
            window.location.href = response.redirect;
        }
    }
});
```

---

### 2. **Validação no Dashboard**
**Arquivo:** `src/web_app/templates/aluno/dashboard.html`

```javascript
// Executado assim que a página carrega
(function() {
    const sessionId = sessionStorage.getItem('optgame_session_id');
    
    if (!sessionId) {
        // Não tem session_id = página foi recarregada
        window.location.href = '/aluno/login';
        return;
    }
    
    // Configurar para enviar em todas requisições
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader('X-Session-Id', sessionId);
        }
    });
})();
```

---

### 3. **Validação no Servidor**
**Arquivo:** `src/web_app/routes.py` - Decorator `@empresa_required`

```python
def empresa_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        empresa_nome = session.get('empresa_nome')
        session_id_server = session.get('session_id')
        
        if not empresa_nome:
            return redirect(url_for('aluno.login'))
        
        # Para páginas HTML (GET), validar session_id
        if not request.is_json and request.method == 'GET':
            session_id_client = request.headers.get('X-Session-Id')
            
            if not session_id_client or session_id_client != session_id_server:
                # Session IDs não batem = página recarregada
                session.clear()
                return redirect(url_for('aluno.login'))
        
        # ... resto da validação (timeout, etc)
```

---

### 4. **Logout**
**Arquivo:** `src/web_app/routes.py`

```python
@aluno_bp.route('/logout')
def logout():
    session.clear()
    return render_template('aluno/logout.html')
```

**Arquivo:** `src/web_app/templates/aluno/logout.html`

```html
<script>
    // Limpar sessionStorage
    sessionStorage.removeItem('optgame_session_id');
    sessionStorage.clear();
    
    // Redirecionar
    window.location.href = '/';
</script>
```

---

## 🎯 Comportamentos Esperados

### ✅ Cenário 1: Login Normal
1. Usuário faz login
2. `session_id` é salvo no sessionStorage
3. Dashboard carrega normalmente
4. Requisições AJAX funcionam

### ✅ Cenário 2: Recarregar Página (F5)
1. Usuário pressiona F5
2. sessionStorage **é mantido** (ainda não fechou aba)
3. Dashboard valida session_id
4. Como o session_id ainda existe, dashboard funciona

**🚨 Mas espera! Queremos que expire ao recarregar!**

### ✅ Cenário 3: Nova Aba/Janela
1. Usuário abre nova aba
2. sessionStorage **NÃO é compartilhado** entre abas
3. Nova aba não tem session_id
4. Redireciona para login ✅

### ✅ Cenário 4: Fechar e Reabrir Navegador
1. Usuário fecha navegador
2. sessionStorage **é apagado**
3. Ao reabrir e acessar /aluno/dashboard
4. Não tem session_id → Redireciona para login ✅

---

## 🔧 Ajuste para Expirar ao Recarregar

Se você quer que expire **até mesmo ao dar F5**, podemos usar uma técnica diferente:

### Opção A: Usar `performance.navigation.type`

**Adicionar no dashboard:**
```javascript
(function() {
    // Detectar se é reload
    if (performance.navigation.type === 1) {
        // É reload (F5) - limpar sessão
        sessionStorage.removeItem('optgame_session_id');
        window.location.href = '/aluno/login';
        return;
    }
    
    // Verificar session_id normalmente
    const sessionId = sessionStorage.getItem('optgame_session_id');
    if (!sessionId) {
        window.location.href = '/aluno/login';
        return;
    }
})();
```

### Opção B: Usar Timestamp + Timeout Curto

**Arquivo:** `src/web_app/routes.py`
```python
# Reduzir timeout para 5 minutos
if login_time and (time.time() - login_time) > 300:  # 5 minutos
    session.clear()
    return redirect(url_for('aluno.login'))
```

### Opção C: Invalidar Sessão a Cada Página

**Mais drástico - sempre pede login:**
```python
@aluno_bp.route('/dashboard')
@empresa_required
def dashboard():
    # Invalidar sessão após renderizar
    session.pop('session_id', None)
    
    # Próxima requisição precisará fazer login novamente
    return render_template('aluno/dashboard.html', ...)
```

---

## 📊 Comparação: sessionStorage vs localStorage

| Característica | sessionStorage | localStorage |
|----------------|----------------|--------------|
| Duração | Até fechar aba | Permanente |
| Entre abas | ❌ Não compartilha | ✅ Compartilha |
| Ao recarregar (F5) | ✅ Mantém | ✅ Mantém |
| Ao fechar navegador | ❌ Apaga | ✅ Mantém |

**Escolhemos sessionStorage** porque:
- ❌ Não persiste entre abas
- ❌ Não persiste ao fechar navegador
- ✅ Perfeito para sessões temporárias

---

## 🧪 Como Testar

### Teste 1: Sessão Normal
```
1. Faça login como aluno
2. Dashboard abre normalmente
3. Envie uma decisão
4. ✅ Funciona
```

### Teste 2: Nova Aba
```
1. Já logado, abra nova aba
2. Cole URL: http://localhost:5000/aluno/dashboard
3. ✅ Redireciona para login (sem session_id na nova aba)
```

### Teste 3: Fechar e Reabrir
```
1. Faça login
2. Feche o navegador completamente
3. Reabra e acesse /aluno/dashboard
4. ✅ Redireciona para login (sessionStorage foi apagado)
```

### Teste 4: Recarregar Página (Atual)
```
1. Faça login
2. Pressione F5 no dashboard
3. ⚠️ Ainda funciona (sessionStorage mantém)
```

### Teste 4 (Modificado): Recarregar = Logout
```
Se implementar Opção A acima:
1. Faça login
2. Pressione F5
3. ✅ Redireciona para login (detectou reload)
```

---

## 🚀 Implementação Atual

✅ **Já Implementado:**
- Login gera `session_id` único
- `session_id` salvo no sessionStorage
- Dashboard valida `session_id` ao carregar
- Logout limpa sessionStorage
- Sessões expiram após 30 minutos

⚠️ **Comportamento Atual:**
- F5 (reload) ainda mantém sessão
- Nova aba força novo login ✅
- Fechar navegador força novo login ✅

---

## 💡 Recomendação

Se você quer **máxima segurança** (forçar login até em reload):

**Adicione ao dashboard.html:**
```javascript
// Logo no início do <script>
if (performance.navigation.type === 1) {
    sessionStorage.clear();
    window.location.href = '{{ url_for("aluno.login") }}';
}
```

Isso detecta reload (F5, Ctrl+R) e força logout.

---

*Documentação criada em: 06 de Outubro de 2025*
