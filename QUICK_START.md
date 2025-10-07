# 🚀 INÍCIO RÁPIDO - Jogo de Produção Web

## ⚡ Instalação Express (5 minutos)

### Windows:
```bash
# 1. Instalar dependências
install_web.bat

# 2. Criar empresas demo
python setup_demo.py

# 3. Iniciar servidor
python web_server.py
```

### Linux/Mac:
```bash
# 1. Dar permissão ao script
chmod +x install_web.sh

# 2. Instalar dependências
./install_web.sh

# 3. Criar empresas demo
python3 setup_demo.py

# 4. Iniciar servidor
python3 web_server.py
```

## 🎯 Acesso Rápido

### 👨‍🏫 Professor (Admin)
- **URL**: http://localhost:5000/admin
- **Senha**: `admin123`

### 👨‍🎓 Alunos (Empresas Demo)
- **URL**: http://localhost:5000/aluno

#### Empresas Criadas:
1. **TechCorp** - Senha: `TECH2024`
2. **InnovaTech** - Senha: `INNO2024`
3. **GlobalProd** - Senha: `GLOB2024`
4. **MegaFactory** - Senha: `MEGA2024`

## 📱 Acesso pela Rede

Outros dispositivos na mesma rede podem acessar:
```
http://[IP-DO-SEU-PC]:5000
```

Para descobrir seu IP:
- **Windows**: `ipconfig` (procure por IPv4)
- **Linux/Mac**: `ifconfig` ou `ip addr`

## 🎮 Como Jogar

### 1️⃣ Professor: Preparar Jogo
1. Acesse `/admin` com senha `admin123`
2. Crie empresas (ou use as demo)
3. Anote as senhas das empresas

### 2️⃣ Alunos: Fazer Login
1. Acesse `/aluno`
2. Selecione sua empresa
3. Entre com a senha

### 3️⃣ Cada Rodada
1. **Alunos**: Decidem quantidades de produção
2. **Alunos**: Clicam em "Enviar Decisão"
3. **Professor**: Aguarda todos enviarem
4. **Professor**: Clica em "Processar Turno"
5. **Sistema**: Calcula resultados
6. **Professor**: Clica em "Abrir Próxima Iteração"
7. Repete até completar 12 iterações

### 4️⃣ Ver Resultados
- Dashboard mostra ranking em tempo real
- Gráficos de evolução
- Estatísticas detalhadas

## 🔧 Solução de Problemas

### Porta 5000 já em uso
Edite `web_server.py`, linha final:
```python
app.run(host='0.0.0.0', port=8080)  # Mudar para 8080
```

### Módulo não encontrado
```bash
pip install flask flask-session
```

### Erro de permissão (Linux/Mac)
```bash
sudo python3 web_server.py
```

## 📞 Precisa de Ajuda?

1. Leia `README_WEB.md` (documentação completa)
2. Verifique logs no terminal
3. Abra console do navegador (F12)

## ✅ Checklist Pré-Jogo

- [ ] Python 3.9+ instalado
- [ ] Dependências instaladas (`pip install -r requirements_web.txt`)
- [ ] Empresas criadas (via `setup_demo.py` ou manualmente)
- [ ] Servidor rodando (`python web_server.py`)
- [ ] Admin acessível em `/admin`
- [ ] Alunos conseguem fazer login em `/aluno`

---

**Pronto para jogar! 🎉**
