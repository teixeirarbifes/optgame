# 📋 CHANGELOG

Histórico de versões e mudanças do Jogo de Produção.

---

## [2.1.0] - 2025-10-06 🎓 MODO EDUCACIONAL PURO

### 🔄 Modificado
- **Remoção Total de Pré-visualização** (Importante!)
  - Removido botão "Validar Decisão"
  - Removida rota API `/api/validar-decisao`
  - Removidas todas as funções JavaScript de validação
  - Alunos enviam decisão sem ver projeções ou simulações

- **Dashboard com Análise Histórica**
  - Seção "Análise da Última Decisão" mostra resultados do turno anterior processado
  - Barras de progresso mostram consumo de recursos do último turno (não projeção)
  - Métricas do último turno (receita, custo, lucro, margem)
  - Tabela compacta de produtos com preços e custos de recursos
  - Interface limpa focada em dados históricos reais

- **Sistema de Análise de Violações** ✨ NOVO
  - Após processamento, dashboard mostra quais restrições foram violadas
  - Detalhes de cada violação: recurso, necessário, disponível e déficit
  - Alertas visuais coloridos (vermelho para violações, verde para sucesso)
  - Dicas contextuais para ajudar a corrigir problemas na próxima iteração
  - Análise de prejuízo mesmo sem violações de recursos

- **Fluxo Simplificado**
  1. Aluno vê recursos disponíveis atuais
  2. Aluno analisa resultados do turno anterior (incluindo violações)
  3. Aluno ajusta sliders baseado em cálculos manuais e feedback
  4. Aluno envia decisão diretamente
  5. Aguarda professor processar para ver resultado real

### 🎯 Justificativa
- Preservar mecânica educacional original do jogo
- Alunos devem calcular e planejar estrategicamente sem "dicas"
- Desenvolvimento de habilidades de análise e cálculo manual
- Foco em planejamento ao invés de tentativa e erro
- Resultados revelados apenas após processamento pelo professor
- Feedback pós-processamento ajuda na aprendizagem sem "entregar" a resposta

---

## [2.0.0] - 2025-10-06 🚀 VERSÃO WEB

### 🎉 Adicionado
- **Versão Web Completa**
  - Interface web responsiva com Bootstrap 5
  - Dashboard administrativo
  - Dashboard para alunos
  - Sistema multiplayer real
  
- **Área Administrativa**
  - Login com senha: admin1064*
  - Dashboard com estatísticas em tempo real
  - Controles do jogo (processar, abrir iteração, resetar)
  - Ranking de empresas
  - Gráfico de evolução (Chart.js)
  - Gerenciamento de empresas (criar/remover)
  - Gerador automático de senhas
  
- **Área dos Alunos**
  - Login por empresa
  - Dashboard interativo
  - Formulário de decisão com sliders
  - Validação em tempo real via AJAX
  - Métricas projetadas (receita, custo, lucro, margem)
  - Barras de progresso de recursos
  - Alertas de violação
  - Histórico de decisões
  - Gráfico de evolução de recursos
  
- **API REST**
  - Endpoints públicos (status, ranking, produtos)
  - Endpoints admin (processar, abrir, resetar, criar/remover)
  - Endpoints alunos (enviar decisão, validar)
  - Responses JSON
  - Documentação completa
  
- **Documentação**
  - README_WEB.md (completo)
  - QUICK_START.md (início rápido)
  - VISUAL_GUIDE.md (guia visual)
  - DEPLOYMENT.md (hospedagem)
  - TECHNICAL_NOTES.md (notas técnicas)
  - API_REFERENCE.md (documentação API)
  - SUMMARY.md (resumo do projeto)
  
- **Scripts de Instalação**
  - install_web.bat (Windows)
  - install_web.sh (Linux/Mac)
  - setup_demo.py (criar empresas demo)
  - requirements_web.txt (dependências pip)
  - .env.example (exemplo de configuração)

### 🎨 Design
- Paleta de cores moderna
- Gradientes e sombras
- Animações suaves (hover, transitions)
- Ícones do Bootstrap Icons
- Toast notifications
- Loading spinners
- Progress bars animadas
- Badges coloridos
- Cards elevados com hover

### ⚡ Performance
- AJAX para todas operações
- Sem reload de página
- Validação client-side
- Debounce em inputs
- Auto-refresh opcional
- Gráficos otimizados

### 📱 Responsividade
- Mobile-first design
- Breakpoints: mobile (<768px), tablet (768-1200px), desktop (>1200px)
- Layout adaptativo
- Touch-friendly (botões e sliders grandes)
- Font sizes responsivos

### 🔒 Segurança
- Session management (Flask-Session)
- Autenticação de admin
- Autenticação por empresa
- Decorators de proteção
- Validação server-side
- Senhas por empresa

### 🛠️ Tecnologias
- Flask 3.0+
- Flask-Session 0.5+
- Bootstrap 5.3
- Chart.js 4.4
- jQuery 3.7
- Bootstrap Icons 1.10
- Jinja2 3.1+

---

## [1.0.0] - Data Anterior 🖥️ VERSÃO DESKTOP

### Características
- Interface desktop com PySide6
- Single-player
- Sistema de múltiplas empresas local
- Gráficos matplotlib
- Histórico e validações
- Portal web básico (FastAPI)
- Salvamento automático

### Tecnologias
- PySide6
- matplotlib
- numpy
- FastAPI (portal)
- Uvicorn

---

## 🔄 Comparação de Versões

| Característica | v1.0 Desktop | v2.0 Web |
|---|---|---|
| Interface | PySide6 (Qt) | Flask (Web) |
| Acesso | Local | Remoto (rede/internet) |
| Multiplayer | ❌ | ✅ |
| Instalação Cliente | Necessária | Navegador apenas |
| Responsivo | ❌ | ✅ |
| AJAX | ❌ | ✅ |
| Dashboard Admin | Básico | Completo |
| Dashboard Aluno | N/A | Completo |
| API REST | FastAPI básica | Flask completa |
| Gráficos | matplotlib | Chart.js |
| Tempo Real | ❌ | ✅ |
| Mobile | ❌ | ✅ |

---

## 🎯 Roadmap Futuro

### v2.1.0 (Próximo)
- [ ] Persistência em banco de dados (SQLite)
- [ ] Exportar resultados (Excel/PDF)
- [ ] Modo sandbox (treino individual)
- [ ] Tutorial interativo
- [ ] Tooltips e ajuda contextual

### v2.2.0
- [ ] Demanda estocástica
- [ ] Eventos aleatórios de mercado
- [ ] Cenários personalizados
- [ ] Múltiplos jogos simultâneos
- [ ] Chat entre equipes

### v2.3.0
- [ ] Conquistas/badges
- [ ] Leaderboard histórico
- [ ] Sistema de níveis
- [ ] Modo competição
- [ ] Análise avançada de desempenho

### v3.0.0 (Longo Prazo)
- [ ] Autenticação OAuth (Google, Microsoft)
- [ ] Integração com Google Classroom
- [ ] Notificações por email
- [ ] Webhooks (Slack, Discord)
- [ ] Modo co-op (empresas aliadas)
- [ ] Marketplace (empresas trocam recursos)
- [ ] API pública documentada (Swagger/OpenAPI)

---

## 🐛 Correções por Versão

### v2.0.0
- ✅ Sincronização slider ↔ input
- ✅ Validação em tempo real
- ✅ Loading spinners em operações assíncronas
- ✅ Toast notifications
- ✅ Tratamento de erros AJAX
- ✅ Responsividade mobile
- ✅ Compatibilidade cross-browser

---

## 📝 Notas de Migração

### De v1.0 para v2.0

**Incompatível**: Dados salvos da v1.0 não podem ser importados diretamente para v2.0.

**Solução**: Exportar dados manualmente ou recriar empresas.

**Configurações**: Mover de `constants.py` (ainda compatível).

**Dependências**: Instalar novas: `pip install flask flask-session`

---

## 🙏 Agradecimentos

Versão web desenvolvida para facilitar o uso em sala de aula, permitindo acesso remoto e experiência multiplayer real.

---

## 📄 Licença

Projeto educacional. Uso livre para fins acadêmicos.

---

**Última atualização**: 6 de outubro de 2025

