# 🚀 DEPLOYMENT - Hospedagem em Servidor Python

## 📋 Opções de Hospedagem

### 1. 🏠 Servidor Local (LAN/Intranet)

#### Configuração:
```bash
# Já está configurado!
python web_server.py
```

**Acesso**:
- Local: `http://localhost:5000`
- Rede: `http://[IP-DA-MÁQUINA]:5000`

**Vantagens**:
- ✅ Gratuito
- ✅ Controle total
- ✅ Sem limitações
- ✅ Dados privados

**Desvantagens**:
- ❌ Só funciona na rede local
- ❌ Computador precisa ficar ligado
- ❌ Não acessível pela internet

---

### 2. 🌐 PythonAnywhere (Recomendado para Iniciantes)

**Site**: https://www.pythonanywhere.com

#### Plano Gratuito:
- ✅ 1 aplicação web
- ✅ 512MB de espaço
- ✅ Domínio: `seuusuario.pythonanywhere.com`

#### Passo a Passo:

1. **Criar conta** no PythonAnywhere

2. **Upload dos arquivos**:
   - Dashboard → Files
   - Upload todos os arquivos .py
   - Upload pasta `src/` completa
   - Upload `requirements_web.txt`

3. **Abrir Console Bash**:
```bash
# Criar virtual environment
mkvirtualenv --python=/usr/bin/python3.9 optgame

# Instalar dependências
pip install -r requirements_web.txt

# Criar empresas demo (opcional)
python setup_demo.py
```

4. **Configurar Web App**:
   - Dashboard → Web
   - Add new web app
   - Framework: Flask
   - Python version: 3.9
   - Path to Flask app: `/home/seuusuario/web_server.py`
   - Virtualenv: `/home/seuusuario/.virtualenvs/optgame`

5. **WSGI Configuration**:
   - Clique em "WSGI configuration file"
   - Edite:
```python
import sys
path = '/home/seuusuario'
if path not in sys.path:
    sys.path.append(path)

from web_server import app as application
```

6. **Reload** e acesse: `https://seuusuario.pythonanywhere.com`

---

### 3. 🐳 Heroku

**Site**: https://www.heroku.com

#### Configuração:

1. **Criar arquivos necessários**:

`Procfile`:
```
web: gunicorn web_server:app
```

`runtime.txt`:
```
python-3.9.13
```

2. **Instalar Heroku CLI e fazer deploy**:
```bash
heroku login
heroku create nome-do-app
git push heroku main
```

**Custo**: Gratuito (com limitações) ou $7/mês

---

### 4. ☁️ AWS / DigitalOcean / Azure

Para servidores mais robustos:

#### DigitalOcean Droplet ($5/mês):

1. **Criar Droplet** (Ubuntu 22.04)

2. **SSH no servidor**:
```bash
ssh root@seu-ip
```

3. **Instalar dependências**:
```bash
apt update
apt install python3 python3-pip nginx -y

# Upload arquivos (via SCP ou Git)
git clone seu-repositorio.git /var/www/optgame
cd /var/www/optgame

# Instalar dependências Python
pip3 install -r requirements_web.txt
pip3 install gunicorn
```

4. **Criar serviço systemd** (`/etc/systemd/system/optgame.service`):
```ini
[Unit]
Description=Jogo de Produção Web
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/optgame
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:8000 web_server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Configurar Nginx** (`/etc/nginx/sites-available/optgame`):
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

6. **Ativar e iniciar**:
```bash
systemctl enable optgame
systemctl start optgame
systemctl status optgame

ln -s /etc/nginx/sites-available/optgame /etc/nginx/sites-enabled/
systemctl restart nginx
```

---

### 5. 🐍 Repl.it

**Site**: https://replit.com

#### Configuração:

1. **Criar novo Repl** (Python)
2. **Upload arquivos**
3. **Instalar deps**: Clique em "Packages" e adicione Flask
4. **Run**: Clica em Run

**Vantagens**:
- ✅ Muito fácil
- ✅ IDE integrada
- ✅ Deploy automático

**Desvantagens**:
- ❌ Repl pode "dormir" se não usado
- ❌ Performance limitada

---

## 🔒 Segurança para Produção

### 1. Mudar Senha Admin:

`src/web_app/game_state.py`:
```python
def __init__(self):
    # ... código existente ...
    self.admin_password = os.environ.get('ADMIN_PASSWORD', 'SENHA_FORTE_AQUI')
```

### 2. Secret Key Segura:

`src/web_app/__init__.py`:
```python
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
```

### 3. Variáveis de Ambiente:

Crie `.env`:
```
ADMIN_PASSWORD=sua_senha_super_secreta
SECRET_KEY=chave_aleatoria_longa
FLASK_ENV=production
```

Instale: `pip install python-dotenv`

Em `web_server.py`, adicione no topo:
```python
from dotenv import load_dotenv
load_dotenv()
```

### 4. HTTPS (SSL):

**Let's Encrypt** (gratuito):
```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d seu-dominio.com
```

### 5. Rate Limiting:

Instale: `pip install flask-limiter`

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)
```

### 6. Firewall:

```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

---

## 📊 Monitoramento

### Logs:
```bash
# Ver logs em tempo real
tail -f /var/log/nginx/access.log
journalctl -u optgame -f
```

### Status:
```bash
systemctl status optgame
systemctl status nginx
```

### Recursos:
```bash
htop  # CPU e RAM
df -h # Disco
```

---

## 🔄 Atualizações

### Atualizar código:
```bash
cd /var/www/optgame
git pull origin main
systemctl restart optgame
```

### Backup antes:
```bash
# Salvar estado do jogo
cp flask_session/* backup/
# Ou exportar via interface admin
```

---

## 💾 Backup Automático

Script `backup.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/optgame"
mkdir -p $BACKUP_DIR
cp -r /var/www/optgame/flask_session $BACKUP_DIR/session_$DATE
echo "Backup criado: $BACKUP_DIR/session_$DATE"
```

Agendar com cron:
```bash
crontab -e
# Adicionar: backup diário às 23h
0 23 * * * /var/www/optgame/backup.sh
```

---

## 🧪 Teste de Carga

Antes de usar com muitos alunos:

```bash
# Instalar
pip install locust

# Criar locustfile.py
# Executar
locust -f locustfile.py --host=http://localhost:5000
```

---

## 📱 Domínio Próprio

### Gratuito:
- **Freenom**: .tk, .ml, .ga (grátis por 1 ano)
- **No-IP**: DNS dinâmico gratuito

### Pago:
- **Namecheap**: ~$10/ano
- **GoDaddy**: ~$12/ano
- **Registro.br**: ~R$40/ano (.br)

### Configurar DNS:
```
Tipo: A
Nome: @
Valor: [IP-DO-SERVIDOR]
TTL: 3600
```

---

## ✅ Checklist Pre-Deploy

- [ ] Senha admin alterada
- [ ] Secret key aleatória configurada
- [ ] Variáveis de ambiente em uso
- [ ] Teste local funcionando
- [ ] Backup dos dados atuais
- [ ] HTTPS configurado (se aplicável)
- [ ] Firewall ativo
- [ ] Logs monitorados
- [ ] Performance testada
- [ ] Documentação atualizada

---

## 🆘 Troubleshooting Comum

### "Module not found":
```bash
pip install -r requirements_web.txt
```

### "Port already in use":
```bash
# Matar processo na porta 5000
lsof -ti:5000 | xargs kill -9
```

### "Permission denied":
```bash
sudo chown -R $USER:$USER /var/www/optgame
```

### "500 Internal Server Error":
```bash
# Ver logs detalhados
journalctl -u optgame -n 50
```

---

**Pronto para o mundo! 🌍🚀**
