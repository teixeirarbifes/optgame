# 🎮 Jogo de Produção - Versão Web

Sistema web interativo e responsivo para simulação de gestão e otimização de produção empresarial.

## 🚀 Características

### ✨ Interface Moderna
- **Design Responsivo**: Funciona perfeitamente em desktop, tablet e mobile
- **Dashboard Interativo**: Gráficos em tempo real com Chart.js
- **AJAX Fluido**: Atualizações sem recarregar a página
- **Bootstrap 5**: Interface moderna e profissional

### 👨‍🏫 Área Administrativa
- Gerenciar empresas participantes
- Processar turnos do jogo
- Visualizar ranking e estatísticas
- Controlar abertura/fechamento de iterações
- **Senha**: `admin1064*`

### 👨‍🎓 Área dos Alunos
- Dashboard personalizado por empresa
- Envio de decisões de produção
- Validação em tempo real de recursos
- Gráficos de evolução
- Histórico de decisões

## 📋 Pré-requisitos

- Python 3.9 ou superior
- Poetry (gerenciador de dependências)

## 🔧 Instalação

1. **Clonar o repositório** (se aplicável)
```bash
cd projetos/optgame
```

2. **Instalar dependências**
```bash
poetry install
```

Ou com pip:
```bash
pip install flask flask-session
```

## ▶️ Como Executar

### Iniciar o servidor web:

```bash
python web_server.py
```

O servidor será iniciado em:
- **Local**: http://localhost:5000
- **Rede**: http://[seu-ip]:5000 (acessível por outros dispositivos na rede)

### Acessos:

#### 👨‍🏫 Professor (Admin):
1. Acesse: http://localhost:5000/admin
2. Senha: `admin1064*`
3. Crie empresas para os alunos
4. Gerencie o jogo

#### 👨‍🎓 Alunos:
1. Acesse: http://localhost:5000/aluno
2. Selecione sua empresa
3. Entre com a senha fornecida pelo professor
4. Envie suas decisões de produção

## 🎯 Fluxo do Jogo

### 1️⃣ Preparação (Professor)
- Acesse a área administrativa
- Crie empresas para cada equipe
- Anote as senhas de cada empresa

### 2️⃣ Distribuição (Professor)
- Informe aos alunos:
  - URL de acesso
  - Nome da empresa
  - Senha de acesso

### 3️⃣ Cada Iteração
1. **Alunos**: Acessam dashboard e planejam produção
2. **Alunos**: Validam decisão em tempo real
3. **Alunos**: Enviam decisão final
4. **Professor**: Verifica status (todas confirmadas?)
5. **Professor**: Clica em "Processar Turno"
6. **Sistema**: Calcula resultados, atualiza recursos
7. **Professor**: Clica em "Abrir Próxima Iteração"
8. **Ciclo**: Repete até completar 12 iterações

### 4️⃣ Fim do Jogo
- Visualizar ranking final
- Analisar estatísticas
- Comparar desempenho das empresas

## 📊 Funcionalidades Principais

### Dashboard Admin
- **Estatísticas Gerais**: Total de empresas, pendentes, lucro médio
- **Controles do Jogo**: Processar turno, abrir iteração, resetar
- **Ranking em Tempo Real**: Classificação por lucro
- **Status das Empresas**: Quem já enviou decisão
- **Gráfico de Evolução**: Lucros ao longo das iterações

### Dashboard Aluno
- **Recursos Disponíveis**: Visualização clara dos recursos
- **Formulário de Decisão**: Sliders e inputs sincronizados
- **Validação em Tempo Real**: Feedback instantâneo
- **Métricas Projetadas**: Receita, custo, lucro, margem
- **Consumo de Recursos**: Barras de progresso coloridas
- **Histórico**: Decisões e resultados anteriores
- **Gráfico de Evolução**: Recursos ao longo do tempo

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask**: Framework web Python
- **Flask-Session**: Gerenciamento de sessões
- **Python 3.9+**: Linguagem principal

### Frontend
- **Bootstrap 5**: Framework CSS responsivo
- **Chart.js**: Biblioteca de gráficos interativos
- **jQuery**: Manipulação DOM e AJAX
- **Bootstrap Icons**: Ícones vetoriais

### Arquitetura
- **MVC Pattern**: Separação de responsabilidades
- **RESTful API**: Comunicação cliente-servidor
- **AJAX**: Atualizações assíncronas
- **Session Management**: Autenticação de usuários

## 🌐 Hospedagem

### Opções para Hospedar:

#### 1. Servidor Local (LAN)
```bash
# Já configurado para aceitar conexões da rede
python web_server.py
# Acesse via: http://[ip-do-servidor]:5000
```

#### 2. PythonAnywhere
```bash
# Upload dos arquivos
# Configure web app Flask
# Aponte para web_server.py
```

#### 3. Heroku
```bash
# Criar Procfile:
web: python web_server.py
```

#### 4. DigitalOcean/AWS/Azure
```bash
# Deploy como aplicação Flask padrão
# Configure gunicorn para produção:
gunicorn -w 4 -b 0.0.0.0:5000 web_server:app
```

## 🔒 Segurança

### Produção:
Para ambiente de produção, considere:

1. **Trocar senha do admin**:
   - Edite `src/web_app/game_state.py`
   - Linha: `self.admin_password = "admin1064*"`

2. **Usar variáveis de ambiente**:
```python
import os
self.admin_password = os.environ.get('ADMIN_PASSWORD', 'admin1064*')
```

3. **HTTPS**: Use certificado SSL
4. **Secret Key**: Gere uma chave segura
5. **Rate Limiting**: Implemente para prevenir abuso

## 📝 API Endpoints

### Público
- `GET /` - Página inicial
- `GET /api/status` - Status do jogo
- `GET /api/ranking` - Ranking de empresas

### Admin
- `POST /admin/login` - Login administrativo
- `GET /admin/dashboard` - Dashboard admin
- `POST /admin/processar-turno` - Processar turno
- `POST /admin/abrir-iteracao` - Abrir iteração
- `POST /admin/resetar-jogo` - Resetar jogo
- `POST /api/admin/criar-empresa` - Criar empresa
- `DELETE /api/admin/remover-empresa/<nome>` - Remover empresa

### Aluno
- `POST /aluno/login` - Login da empresa
- `GET /aluno/dashboard` - Dashboard da empresa
- `POST /aluno/enviar-decisao` - Enviar decisão
- `POST /api/validar-decisao` - Validar decisão (tempo real)

## 🎨 Customização

### Cores e Temas
Edite `src/web_app/templates/base.html`:
```css
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    /* ... */
}
```

### Recursos Iniciais
Edite `src/config/constants.py`:
```python
RECURSOS_BASE = {
    "dinheiro": 38000,
    "materia_prima": 1200,
    # ...
}
```

### Produtos
Edite `src/config/constants.py`:
```python
PRODUTOS = {
    "📱 Smartphone": {
        "custo_materia": 28,
        # ...
    }
}
```

## 🐛 Troubleshooting

### Porta já em uso
```bash
# Mudar porta em web_server.py:
app.run(host='0.0.0.0', port=8080)  # Usar 8080 ao invés de 5000
```

### Sessões não funcionam
```bash
# Criar pasta para sessões:
mkdir flask_session
```

### Gráficos não aparecem
- Verificar conexão com internet (Chart.js via CDN)
- Ou baixar Chart.js localmente

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs no terminal
2. Abra o console do navegador (F12)
3. Revise este README

## 📄 Licença

Este projeto é educacional e pode ser usado livremente para fins acadêmicos.

---

**Desenvolvido para educação em gestão e otimização de produção** 🎓
