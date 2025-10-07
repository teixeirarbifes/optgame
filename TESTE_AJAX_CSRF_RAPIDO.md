# 🧪 GUIA DE TESTE RÁPIDO - AJAX + CSRF

## ⚡ Testes Essenciais (5 minutos)

### 1️⃣ **Iniciar Servidor**
```powershell
cd c:\projetos\optgame
python web_server.py
```

Aguarde mensagem: `🎮 SERVIDOR WEB DO JOGO DE PRODUÇÃO`

---

### 2️⃣ **Teste: Login de Aluno via AJAX**

1. Abra: http://localhost:5000/aluno/login
2. Pressione **F12** (DevTools) → Aba **Network**
3. Selecione uma empresa e faça login
4. Na aba Network, clique na requisição `login`

**✅ Validações:**
- Request Headers contém: `Content-Type: application/json`
- Request Payload é JSON: `{"nome":"...", "senha":"..."}`
- Response é JSON: `{"sucesso": true, "redirect": "..."}`
- **SEM reload da página** até sucesso

---

### 3️⃣ **Teste: CSRF Token Presente**

1. No dashboard do aluno (ou admin)
2. DevTools → **Console**
3. Digite e execute:
```javascript
$('meta[name="csrf-token"]').attr('content')
```

**✅ Validação:**
- Retorna string de 64 caracteres (ex: `a1b2c3d4e5f6...`)

---

### 4️⃣ **Teste: Envio de Decisão (Aluno)**

1. No dashboard do aluno
2. Altere quantidades dos produtos
3. Clique **"Enviar Decisão"**
4. DevTools → **Network** → Requisição `enviar-decisao`

**✅ Validações:**
- Request Headers: `X-CSRF-Token: [64 chars]`
- Request Headers: `Content-Type: application/json`
- Request Payload: JSON com produtos
- Response: `{"sucesso": true, "mensagem": "..."}`
- Toast verde aparece: "Decisão enviada com sucesso!"
- **Página NÃO recarrega**

---

### 5️⃣ **Teste: Processar Turno (Admin)**

1. Faça login como admin (senha: `admin1064*`)
2. No dashboard, clique **"Processar Turno Atual"**
3. Confirme o dialog
4. DevTools → **Network** → Requisição `processar-turno`

**✅ Validações:**
- Request Headers: `X-CSRF-Token: [64 chars]`
- Response: `{"sucesso": true, ...}`
- Toast verde: "Turno processado com sucesso!"
- **Dados atualizam automaticamente sem reload**

---

### 6️⃣ **Teste: Criar Empresa (Admin)**

1. No dashboard admin, clique **"+ Nova Empresa"**
2. Preencha: Nome, Equipe, Senha
3. Clique **"Criar Empresa"**
4. DevTools → **Network** → Requisição `criar-empresa`

**✅ Validações:**
- Request URL: `/api/admin/criar-empresa`
- Request Headers: `X-CSRF-Token: [presente]`
- Request Payload: `{"nome":"...", "equipe":"...", "senha":"..."}`
- Response: `{"sucesso": true, "mensagem": "..."}`
- Modal fecha automaticamente
- Tabela atualiza com nova empresa **SEM reload**

---

### 7️⃣ **Teste: Proteção CSRF (Bloqueio)**

1. DevTools → **Console**
2. Execute comando SEM token:
```javascript
$.ajax({
    url: '/admin/processar-turno',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({}),
    headers: {} // Sem X-CSRF-Token!
});
```

**✅ Validações:**
- Response Status: **403 Forbidden**
- Response JSON: `{"sucesso": false, "erro": "Token CSRF inválido"}`
- Toast vermelho: "Token inválido..."

---

### 8️⃣ **Teste: Renovação Automática CSRF**

1. Ainda no Console, execute:
```javascript
// Simular token inválido
$('meta[name="csrf-token"]').attr('content', 'token_invalido_12345');

// Tentar ação
$.ajax({
    url: '/admin/processar-turno',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({})
});
```

**✅ Validações:**
- Toast vermelho aparece
- Na aba **Network**, veja requisição automática para `/api/csrf-token`
- Novo token é obtido e atualizado no meta tag

---

### 9️⃣ **Teste: Timeout de Sessão** ⏱️

**Opção A - Teste Rápido (alterar código temporariamente):**
1. Abra: `src/web_app/routes.py`
2. Linha ~65, altere `1800` para `30`:
```python
if time.time() - login_time > 30:  # 30 segundos
```
3. Reinicie servidor
4. Faça login e espere 31 segundos
5. Tente enviar decisão

**Opção B - Teste Manual (não alterar código):**
1. DevTools → **Application** → **Session Storage**
2. Delete a chave `login_time`
3. Tente uma ação (enviar decisão, etc.)

**✅ Validações:**
- Response Status: **401 Unauthorized**
- Toast amarelo: "Sessão expirada. Faça login novamente."
- Redirecionamento automático para login após 2 segundos

---

### 🔟 **Teste: Polling de Estado (Auto-refresh)**

1. No dashboard do aluno
2. DevTools → **Network**
3. Aguarde 3 segundos
4. Veja requisição automática: `/api/estado`

**✅ Validações:**
- Requisição GET a cada 3 segundos
- Response com dados atualizados
- Status do jogo atualiza automaticamente
- **Zero reloads de página**

---

## 🎯 Checklist Completo

| Teste | Status |
|-------|--------|
| ✅ Login via AJAX (JSON) | ⬜ |
| ✅ CSRF Token no meta tag | ⬜ |
| ✅ Envio decisão com CSRF | ⬜ |
| ✅ Processar turno sem reload | ⬜ |
| ✅ Criar empresa via AJAX | ⬜ |
| ✅ Proteção CSRF bloqueia | ⬜ |
| ✅ Renovação automática token | ⬜ |
| ✅ Timeout de sessão | ⬜ |
| ✅ Polling de estado | ⬜ |

---

## 🐛 Troubleshooting

### Problema: "CSRF Token inválido" em toda requisição
**Solução:**
1. Limpe sessão: DevTools → Application → Clear storage
2. Recarregue página
3. Faça login novamente

### Problema: Polling não funciona
**Solução:**
1. Verifique console do navegador por erros
2. Confirme que função `atualizarEstado()` existe no template
3. Veja se `setInterval` está sendo chamado

### Problema: Timeout não redireciona
**Solução:**
1. Verifique handler global em base.html: `$(document).ajaxError(...)`
2. Confirme que rota retorna status 401
3. Teste manualmente deletando `login_time` da sessão

---

## 📊 Resultado Esperado

Após completar todos os testes:

✅ **AJAX Funcionando:**
- Todas ações via requisições assíncronas
- Zero reloads desnecessários
- Feedback instantâneo com toasts

✅ **CSRF Protegendo:**
- Todas modificações requerem token válido
- Bloqueio de requisições não autorizadas
- Renovação automática em erros

✅ **Sessões Seguras:**
- Timeout automático após 30 minutos
- Redirecionamento em sessão expirada
- Cookies não-persistentes

---

## 🚀 Próximos Passos (Opcional)

### Para Ambiente de Produção:
1. **HTTPS obrigatório:**
   ```python
   app.config['SESSION_COOKIE_SECURE'] = True
   ```

2. **Rate Limiting robusto:**
   ```bash
   pip install Flask-Limiter
   ```

3. **Logs de segurança:**
   ```python
   import logging
   logging.warning(f'CSRF inválido: {request.remote_addr}')
   ```

4. **Variáveis de ambiente:**
   ```bash
   export SECRET_KEY="your-secret-key-here"
   export FLASK_ENV="production"
   ```

---

*Guia criado em: 06 de Outubro de 2025*  
*Tempo estimado de testes: 5-10 minutos*
