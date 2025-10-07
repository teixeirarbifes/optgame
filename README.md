# 🎮 Jogo de Produção Empresarial

Simulador educacional de gestão e otimização de produção para ensino de Programação Linear, Pesquisa Operacional e Gestão de Recursos.

## 🚀 Versões Disponíveis

### 🌐 Versão Web (v2.0) - **RECOMENDADA** 
Interface web moderna, responsiva e multiplayer para uso em sala de aula.

**[📚 Documentação Completa da Versão Web →](README_WEB.md)**

#### Características:
- ✅ **Multiplayer Real**: Múltiplas empresas jogam simultaneamente
- ✅ **Acesso Remoto**: Qualquer dispositivo na rede
- ✅ **Dashboard Moderno**: Bootstrap 5 + Chart.js
- ✅ **AJAX Fluido**: Sem recarregar página
- ✅ **Área Admin**: Controle total do jogo
- ✅ **Área Alunos**: Dashboard interativo com validação em tempo real
- ✅ **Responsivo**: Mobile, tablet e desktop
- ✅ **Fácil Deploy**: Python + Flask

#### Início Rápido:
```bash
# Instalar dependências
pip install flask flask-session

# Criar empresas demo
python setup_demo.py

# Iniciar servidor
python web_server.py

# Acessar
# Admin: http://localhost:5000/admin (senha: admin1064*)
# Alunos: http://localhost:5000/aluno
```

📖 **Documentação**:
- [README_WEB.md](README_WEB.md) - Documentação completa
- [QUICK_START.md](QUICK_START.md) - Guia rápido (5 min)
- [DEPLOYMENT.md](DEPLOYMENT.md) - Como hospedar
- [API_REFERENCE.md](API_REFERENCE.md) - API REST

---

### 🖥️ Versão Desktop (v1.0)
Interface desktop com PySide6 para uso local/individual.

#### Características:
- Interface gráfica com Qt (PySide6)
- Múltiplas empresas localmente
- Gráficos matplotlib
- Portal web básico (FastAPI)

#### Instalação:

**Com Poetry:**
```bash
poetry install
poetry shell
python src/main.py
```

**Com pip:**
```bash
pip install PySide6 matplotlib numpy fastapi uvicorn
python src/main.py
```

---

## 📊 Sobre o Jogo

### Objetivo
Gerenciar uma empresa virtual, tomando decisões de produção que maximizem o lucro considerando recursos limitados (dinheiro, matéria-prima, energia e trabalhadores).

### Mecânica
1. **Planejamento**: Decidir quantidades de cada produto a produzir
2. **Validação**: Sistema verifica disponibilidade de recursos
3. **Execução**: Produção é realizada, recursos consumidos
4. **Resultados**: Lucro calculado, recursos atualizados
5. **Iteração**: Processo se repete por 12 turnos

### Produtos (Padrão)
- 📱 **Smartphone**: Lucro R$ 231.50, Recursos: 28/22/3.5
- 💻 **Laptop**: Lucro R$ 371.80, Recursos: 45/38/5.2
- 🖥️ **Desktop**: Lucro R$ 480.70, Recursos: 62/48/6.8

### Recursos Iniciais
- 💰 Dinheiro: R$ 38,000
- 📦 Matéria-Prima: 1,200 unidades
- ⚡ Energia: 1,500 kWh
- 👥 Trabalhadores: 90 horas

---

## 🎯 Para Educação

### Conceitos Aplicados
- Programação Linear
- Otimização com Restrições
- Análise de Trade-offs
- Gestão de Recursos Escassos
- Teoria da Decisão
- Planejamento Estratégico

### Disciplinas
- Pesquisa Operacional
- Administração da Produção
- Gestão de Operações
- Economia Empresarial
- Engenharia de Produção

---

## 📦 Requisitos

- **Python**: 3.9 ou superior
- **Navegador**: Chrome, Firefox, Edge ou Safari (para versão web)

---

## 📚 Documentação Completa

### Versão Web
- [README_WEB.md](README_WEB.md) - Guia completo
- [QUICK_START.md](QUICK_START.md) - Início rápido
- [VISUAL_GUIDE.md](VISUAL_GUIDE.md) - Guia visual
- [DEPLOYMENT.md](DEPLOYMENT.md) - Hospedagem
- [API_REFERENCE.md](API_REFERENCE.md) - API REST
- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md) - Notas técnicas

### Geral
- [SUMMARY.md](SUMMARY.md) - Resumo do projeto
- [CHANGELOG.md](CHANGELOG.md) - Histórico de versões
- [CONTRIBUTING.md](CONTRIBUTING.md) - Como contribuir

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

---

## 📄 Licença

Projeto educacional. Uso livre para fins acadêmicos.

---

## 👨‍💻 Autor

Desenvolvido para educação em gestão e otimização de produção.

## Desenvolvimento

### Ferramentas de desenvolvimento

Este projeto inclui várias ferramentas de desenvolvimento:

- **Black**: Formatação de código
- **isort**: Organização de imports
- **flake8**: Linting
- **mypy**: Verificação de tipos
- **pytest**: Testes

### Executando as ferramentas

```bash
# Formatação de código
poetry run black src/

# Organização de imports
poetry run isort src/

# Linting
poetry run flake8 src/

# Verificação de tipos
poetry run mypy src/

# Testes
poetry run pytest
```

## Estrutura do projeto

```
src/
├── main.py              # Ponto de entrada principal
├── emp_pyside6_orignal._py  # Código original (temporário)
├── config/              # Configurações
├── controller/          # Controladores
├── data/               # Dados
├── mecanicas/          # Mecânicas do jogo
├── utils/              # Utilitários
└── ux/                 # Interface do usuário
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.