# 🚀 Scripts de Inicialização do Web Portal

## Arquivos Criados

### 1. `start_web.bat`
Script para **iniciar o servidor web** usando Poetry.

**Uso:**
```cmd
start_web.bat
```

**O que faz:**
- Ativa o ambiente Poetry automaticamente
- Inicia o servidor Flask na porta 5000
- Mostra instruções de acesso
- Senha admin: admin123

**Acesso:**
- Admin: http://localhost:5000/admin/login
- Aluno: http://localhost:5000/aluno/login

---

### 2. `install_web_poetry.bat`
Script para **instalar dependências** do projeto usando Poetry.

**Uso:**
```cmd
install_web_poetry.bat
```

**O que faz:**
1. Verifica se Poetry está instalado
2. Instala todas as dependências do `pyproject.toml`
3. Testa importação dos pacotes principais
4. Executa testes de configuração
5. Mostra instruções para iniciar o servidor

---

## 🎯 Fluxo de Uso

### Primeira Vez (Instalação)
```cmd
1. install_web_poetry.bat  # Instala dependências
2. start_web.bat           # Inicia servidor
```

### Uso Diário
```cmd
start_web.bat  # Apenas iniciar servidor
```

---

## 📋 Pré-requisitos

### Poetry instalado
```powershell
# Verificar se está instalado
poetry --version

# Instalar se necessário
pip install poetry
```

### Python 3.9+
```powershell
python --version
```

---

## 🔧 Solução de Problemas

### Erro: "Poetry não encontrado"
```powershell
pip install poetry
# ou
python -m pip install poetry
```

### Erro: "ModuleNotFoundError: No module named 'flask'"
```cmd
install_web_poetry.bat
```

### Porta 5000 em uso
Edite `web_server.py` e mude:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
# para
app.run(host='0.0.0.0', port=8000, debug=True)
```

---

## 📁 Estrutura de Arquivos

```
optgame/
├── start_web.bat              ← NOVO! Inicia servidor
├── install_web_poetry.bat     ← NOVO! Instala dependências
├── web_server.py              ← Servidor Flask principal
├── pyproject.toml             ← Dependências do Poetry
├── poetry.lock                ← Lock file do Poetry
└── src/
    └── web_app/
        ├── routes.py
        ├── game_state.py
        └── templates/
```

---

## ⚡ Comandos Rápidos

### Iniciar servidor
```cmd
start_web.bat
```

### Instalar/atualizar dependências
```cmd
install_web_poetry.bat
```

### Parar servidor
```
Pressione Ctrl+C no terminal
```

### Resetar jogo (durante execução)
- Acesse admin: http://localhost:5000/admin/dashboard
- Clique em "Resetar Jogo"

---

## 🎓 Para Professores

### Configurar antes da aula:
1. Execute `install_web_poetry.bat` (uma vez)
2. Execute `start_web.bat`
3. Acesse http://localhost:5000/admin/login
4. Senha: `admin123`
5. Crie empresas para os alunos
6. Compartilhe link: http://localhost:5000/aluno/login

### Durante a aula:
- Abrir iteração: Botão "Abrir Próxima Iteração"
- Processar turno: Botão "Processar Turno Atual"
- Acompanhar: Veja status em tempo real via AJAX

---

## 🐛 Debug

### Ver logs detalhados
O terminal onde `start_web.bat` está rodando mostra:
- Requisições HTTP
- Validações de recursos
- Erros de Python

### Logs de validação
Após correção, os logs mostram:
```
=== VALIDANDO EMPRESA: NomeEmpresa ===
Decisão: {'💻 Laptop': 100}
Consumo calculado: {...}
Recursos disponíveis: {...}
  materia_prima: necessário=3500, disponível=25000
  ❌ VIOLAÇÃO! Déficit: XXX (se houver)
```

---

## ✅ Tudo Pronto!

Execute agora:
```cmd
start_web.bat
```

E acesse: http://localhost:5000
