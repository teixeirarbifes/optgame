# 🛠️ NOTAS TÉCNICAS

## ⚠️ Avisos do Linter

Se você ver erros/avisos no VS Code nos arquivos de template (`.html`), **ignore-os**. São falsos positivos porque:

1. **Jinja2 Templates**: Os arquivos HTML usam sintaxe Jinja2 (`{{ }}`, `{% %}`)
2. **Linter Confuso**: O linter JavaScript/CSS tenta analisar essas tags e falha
3. **Código Correto**: Os templates funcionam perfeitamente quando renderizados pelo Flask

### Exemplos de "erros" que são normais:
```html
<!-- Isso causa "erro" no linter, mas funciona perfeitamente -->
<div style="width: {{ porcentagem }}%"></div>
const dados = {{ variavel|tojson }};
{% if condicao %}...{% endif %}
```

### Como desabilitar avisos:
Adicione ao `.vscode/settings.json`:
```json
{
    "html.validate.scripts": false,
    "css.validate": false
}
```

---

## 🐍 Versões Python

### Testado com:
- Python 3.9.13 ✅
- Python 3.10.x ✅
- Python 3.11.x ✅

### Incompatível com:
- Python 3.8 ou inferior ❌
- Python 3.13+ (PySide6 pode ter problemas) ⚠️

---

## 📦 Dependências

### Principais:
- **Flask 3.0+** - Framework web
- **Flask-Session 0.5+** - Gerenciamento de sessões
- **Jinja2 3.1+** - Template engine (já vem com Flask)

### Opcionais (para versão desktop):
- PySide6 6.7+
- matplotlib 3.5+
- numpy 1.21+
- FastAPI 0.110+ (se quiser usar a API alternativa)

---

## 🔧 Configuração

### Variáveis de Ambiente
O sistema funciona sem variáveis de ambiente (usa defaults), mas você pode customizar:

```bash
# Windows (PowerShell)
$env:ADMIN_PASSWORD="minhasenha"
$env:PORT="8080"
python web_server.py

# Linux/Mac
export ADMIN_PASSWORD="minhasenha"
export PORT="8080"
python3 web_server.py
```

### Arquivo .env
Crie `.env` na raiz:
```
ADMIN_PASSWORD=minhasenha
SECRET_KEY=chave-aleatoria-longa
PORT=5000
```

Instale `python-dotenv`:
```bash
pip install python-dotenv
```

E adicione no `web_server.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 🗄️ Armazenamento de Dados

### Atualmente:
- **Em memória** (variável global `game_state`)
- **Flask-Session** (arquivos em `flask_session/`)

### Persistência:
Os dados são perdidos quando o servidor reinicia. Para persistir:

**Opção 1 - JSON** (simples):
```python
# Salvar ao processar turno
game_state.salvar_estado('backup.json')

# Carregar ao iniciar
if os.path.exists('backup.json'):
    game_state.carregar_estado('backup.json')
```

**Opção 2 - SQLite** (robusto):
```python
# Criar tabelas
# Salvar após cada operação
# Carregar na inicialização
```

---

## 🔒 Segurança

### Produção:
**SEMPRE MUDE**:
1. Senha do admin (default: `admin1064*`)
2. Secret key do Flask
3. Use HTTPS
4. Configure firewall

### Development:
- Pode usar senhas simples
- Debug mode ativado
- HTTP sem problema

---

## 🌐 Rede

### Localhost (127.0.0.1):
- Apenas você acessa
- Útil para testes

### LAN (0.0.0.0):
- Qualquer dispositivo na rede acessa
- IP: `192.168.x.x` ou `10.x.x.x`
- Descubra seu IP:
  - Windows: `ipconfig`
  - Linux/Mac: `ifconfig` ou `ip addr`

### Internet:
- Precisa de IP público ou domínio
- Configurar port forwarding no roteador
- OU usar serviço de hospedagem

---

## 📊 Performance

### Recursos Mínimos:
- **CPU**: 1 core
- **RAM**: 512MB
- **Disco**: 100MB

### Recomendado (para 20+ alunos):
- **CPU**: 2 cores
- **RAM**: 2GB
- **Disco**: 1GB
- **Rede**: 10Mbps

### Otimizações:
```python
# Usar Gunicorn em produção
gunicorn -w 4 -b 0.0.0.0:5000 web_server:app

# -w 4 = 4 workers (ajustar conforme CPUs)
```

---

## 🐛 Debug

### Modo Debug:
```python
# Em web_server.py, linha final:
app.run(debug=True)  # Mostra erros detalhados
```

### Logs:
```python
# Adicionar no código:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Console do Navegador:
- Pressione F12
- Veja erros JavaScript
- Inspecione requisições AJAX

---

## 🧪 Testes

### Manual:
1. Criar empresa
2. Login como empresa
3. Enviar decisão
4. Login como admin
5. Processar turno
6. Verificar resultados

### Automatizado (futuro):
```python
# pytest
pip install pytest
pytest tests/
```

---

## 📱 Compatibilidade de Navegadores

### Testado:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+

### Funcionalidades necessárias:
- JavaScript (obrigatório)
- Cookies/Sessions (obrigatório)
- CSS3 (para visual)
- Chart.js (via CDN)

### Internet:
- Necessária para CDNs (Bootstrap, Chart.js, jQuery)
- OU baixe bibliotecas localmente

---

## 🔄 Atualizações

### Git:
```bash
# Atualizar código
git pull origin main

# Reinstalar dependências
pip install -r requirements_web.txt

# Reiniciar servidor
# Ctrl+C e python web_server.py novamente
```

### Manual:
1. Backup dos dados (`flask_session/`)
2. Substituir arquivos
3. Verificar novas dependências
4. Reiniciar servidor

---

## 💡 Dicas

### Desenvolvimento:
- Use `debug=True` em desenvolvimento
- Teste em múltiplos navegadores
- Abra console (F12) para ver erros
- Use senhas simples para teste

### Produção:
- Use `debug=False`
- Configure HTTPS
- Use senhas fortes
- Configure backups automáticos
- Monitore logs
- Use Gunicorn ou uWSGI

### Sala de Aula:
- Teste TUDO antes da aula
- Prepare empresas antecipadamente
- Tenha senhas anotadas
- Explique o fluxo aos alunos
- Faça backup após cada iteração

---

## 📞 Suporte

### Problemas Comuns:

**Porta em uso:**
```
OSError: [Errno 98] Address already in use
```
→ Mude a porta ou mate o processo

**Módulo não encontrado:**
```
ModuleNotFoundError: No module named 'flask'
```
→ Instale: `pip install flask flask-session`

**Template não encontrado:**
```
TemplateNotFound: admin/dashboard.html
```
→ Verifique estrutura de pastas `templates/`

**Sessão não funciona:**
```
No such file or directory: 'flask_session'
```
→ Crie pasta: `mkdir flask_session`

**AJAX não funciona:**
→ Verifique console do navegador (F12)
→ Verifique se jQuery carregou
→ Verifique internet (para CDN)

---

## 📚 Referências

### Documentação:
- [Flask](https://flask.palletsprojects.com/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Chart.js](https://www.chartjs.org/)
- [Jinja2](https://jinja.palletsprojects.com/)

### Tutoriais:
- Flask Tutorial: https://flask.palletsprojects.com/tutorial/
- Bootstrap Examples: https://getbootstrap.com/docs/5.3/examples/
- Chart.js Samples: https://www.chartjs.org/docs/latest/samples/

---

**Desenvolvido para educação 📚**
