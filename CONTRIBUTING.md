# 🤝 GUIA DE CONTRIBUIÇÃO

Obrigado por considerar contribuir com o Jogo de Produção!

---

## 🎯 Como Posso Contribuir?

### 🐛 Reportar Bugs
1. Verifique se o bug já foi reportado
2. Use um título claro e descritivo
3. Descreva os passos para reproduzir
4. Explique o comportamento esperado vs atual
5. Inclua screenshots se aplicável
6. Mencione versão do Python e navegador

### 💡 Sugerir Melhorias
1. Use um título claro e descritivo
2. Explique por que seria útil
3. Forneça exemplos de uso
4. Considere alternativas

### 📝 Melhorar Documentação
- Corrigir typos
- Clarificar instruções
- Adicionar exemplos
- Traduzir para outros idiomas

### 💻 Contribuir com Código
1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Faça suas alterações
4. Teste completamente
5. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
6. Push para a branch (`git push origin feature/MinhaFeature`)
7. Abra um Pull Request

---

## 📋 Checklist para Pull Requests

- [ ] Código segue o estilo do projeto
- [ ] Comentários em partes complexas
- [ ] Documentação atualizada
- [ ] Testes adicionados (se aplicável)
- [ ] Testes existentes passam
- [ ] Commit messages claros
- [ ] Branch atualizada com main

---

## 🎨 Padrões de Código

### Python (PEP 8)
```python
# Imports
import os
import sys
from typing import List, Dict

# Constantes
MAX_EMPRESAS = 50
TIMEOUT_SECONDS = 30

# Classes (PascalCase)
class GameState:
    def __init__(self):
        pass

# Funções (snake_case)
def processar_turno():
    pass

# Variáveis (snake_case)
nome_empresa = "TechCorp"
lucro_total = 0.0
```

### JavaScript
```javascript
// Constantes
const MAX_RETRIES = 3;

// Funções (camelCase)
function validarDecisao() {
    // código
}

// Variáveis (camelCase)
let nomeEmpresa = "TechCorp";
let lucroTotal = 0.0;

// jQuery
$(document).ready(function() {
    // código
});
```

### HTML/Jinja2
```html
<!-- Indentação: 4 espaços -->
<div class="container">
    {% for item in items %}
    <div class="card">
        {{ item.nome }}
    </div>
    {% endfor %}
</div>
```

### CSS
```css
/* Classes (kebab-case) */
.stat-card {
    padding: 20px;
    border-radius: 15px;
}

/* IDs (camelCase) */
#loadingSpinner {
    display: none;
}
```

---

## 🔧 Configuração para Desenvolvimento

### 1. Clonar Repositório
```bash
git clone https://github.com/teixeirarbifes/optgame.git
cd optgame
```

### 2. Criar Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar Dependências
```bash
pip install -r requirements_web.txt
pip install -r requirements_dev.txt  # Se existir
```

### 4. Configurar Ambiente
```bash
cp .env.example .env
# Editar .env conforme necessário
```

### 5. Rodar Testes
```bash
pytest tests/  # Se existir
```

### 6. Iniciar Servidor
```bash
python web_server.py
```

---

## 🧪 Testes

### Estrutura
```
tests/
├── test_game_state.py
├── test_routes.py
├── test_api.py
└── test_mechanics.py
```

### Executar Testes
```bash
# Todos
pytest

# Específico
pytest tests/test_game_state.py

# Com cobertura
pytest --cov=src tests/
```

### Escrever Testes
```python
import pytest
from src.web_app.game_state import GameState

def test_adicionar_empresa():
    game = GameState()
    sucesso = game.adicionar_empresa("Teste", "Equipe", "senha")
    assert sucesso == True
    assert "Teste" in game.empresas
```

---

## 📁 Estrutura do Projeto

```
optgame/
├── web_server.py          # Ponto de entrada
├── setup_demo.py          # Setup inicial
├── requirements_web.txt   # Dependências
├── pyproject.toml        # Config Poetry
│
├── docs/                 # Documentação adicional
│   └── ...
│
├── src/
│   ├── config/          # Configurações
│   ├── controller/      # Controllers (desktop)
│   ├── mecanicas/       # Lógica de jogo
│   └── web_app/         # Aplicação web
│       ├── __init__.py
│       ├── game_state.py
│       ├── routes.py
│       └── templates/
│
├── tests/               # Testes unitários
│   └── ...
│
└── README.md           # Documentação principal
```

---

## 🎯 Áreas que Precisam de Contribuições

### Alta Prioridade 🔴
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Persistência em banco de dados
- [ ] Validação de segurança

### Média Prioridade 🟡
- [ ] Tutorial interativo
- [ ] Exportar relatórios (PDF/Excel)
- [ ] Modo sandbox
- [ ] Internacionalização (i18n)

### Baixa Prioridade 🟢
- [ ] Temas customizáveis
- [ ] Mais tipos de produtos
- [ ] Conquistas/badges
- [ ] Chat entre equipes

---

## 💬 Comunicação

### Issues
- Use templates quando disponíveis
- Seja claro e objetivo
- Forneça contexto suficiente
- Responda a perguntas

### Pull Requests
- Descreva o que foi alterado
- Explique o porquê
- Referencie issues relacionadas
- Responda a revisões

### Code Review
- Seja respeitoso
- Sugira, não imponha
- Explique o raciocínio
- Aprove quando apropriado

---

## 🔍 O Que Procuramos em PRs

### ✅ Bom
- Código limpo e legível
- Bem documentado
- Testado
- Segue padrões
- Commit messages claros
- PR pequeno e focado

### ❌ Evitar
- Código não testado
- Sem documentação
- Múltiplas features em um PR
- Commits genéricos ("fix" "update")
- Quebrar funcionalidades existentes
- Ignorar feedback de revisão

---

## 📝 Commit Messages

### Formato
```
tipo(escopo): assunto

[corpo opcional]

[rodapé opcional]
```

### Tipos
- **feat**: Nova feature
- **fix**: Correção de bug
- **docs**: Documentação
- **style**: Formatação (não afeta lógica)
- **refactor**: Refatoração
- **test**: Testes
- **chore**: Tarefas de manutenção

### Exemplos
```
feat(admin): adiciona botão para exportar ranking

fix(validacao): corrige cálculo de recursos disponíveis

docs(readme): atualiza instruções de instalação

style(dashboard): ajusta espaçamento dos cards

refactor(api): simplifica lógica de autenticação

test(game_state): adiciona testes para processar_turno

chore(deps): atualiza Flask para 3.0.1
```

---

## 🏷️ Labels

### Tipo
- `bug` - Algo não funciona
- `enhancement` - Nova feature ou melhoria
- `documentation` - Documentação
- `question` - Pergunta

### Prioridade
- `priority: high` - Urgente
- `priority: medium` - Importante
- `priority: low` - Pode esperar

### Status
- `good first issue` - Bom para iniciantes
- `help wanted` - Precisa de ajuda
- `in progress` - Sendo trabalhado
- `blocked` - Bloqueado por algo

---

## 🎓 Recursos para Aprender

### Flask
- [Documentação Oficial](https://flask.palletsprojects.com/)
- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

### Bootstrap
- [Documentação Bootstrap 5](https://getbootstrap.com/docs/5.3/)
- [Bootstrap Examples](https://getbootstrap.com/docs/5.3/examples/)

### Chart.js
- [Documentação](https://www.chartjs.org/docs/latest/)
- [Samples](https://www.chartjs.org/docs/latest/samples/)

### Git/GitHub
- [Git Book](https://git-scm.com/book/pt-br/v2)
- [GitHub Guides](https://guides.github.com/)

---

## 🙏 Reconhecimento

Todos os contribuidores serão adicionados ao arquivo CONTRIBUTORS.md!

---

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto.

---

## ❓ Dúvidas?

- Abra uma issue com a label `question`
- Entre em contato com os mantenedores

---

**Obrigado por contribuir! 🎉**
