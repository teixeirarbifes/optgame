# 📸 GUIA VISUAL - Jogo de Produção Web

## 🎨 Características Visuais

### 🏠 Página Inicial
- Design moderno com gradiente purple/blue
- Cards grandes para Admin e Alunos
- Ícones do Bootstrap Icons
- Responsivo (mobile-first)

### 👨‍🏫 Área Administrativa

#### Dashboard Principal
- **Estatísticas em Cards**:
  - Iteração Atual (grande, centralizado)
  - Total de Empresas (com ícone de prédio)
  - Empresas Pendentes (amarelo de aviso)
  - Lucro Médio (verde/vermelho condicional)

- **Barra de Progresso**:
  - Iteração X de 12
  - Cor verde indicando avanço
  - Percentual exibido

- **Controles do Jogo**:
  - Botão "Processar Turno" (verde, grande)
  - Botão "Abrir Próxima Iteração" (azul)
  - Botão "Resetar Jogo" (vermelho)
  - Badge de status (Aberta/Fechada)

- **Ranking em Tempo Real**:
  - Tabela com posições
  - Troféus para top 3 (🥇🥈🥉)
  - Badges coloridos para lucros
  - Nome da empresa e equipe

- **Status das Empresas**:
  - Lista de todas empresas
  - Badge de status (Confirmada/Pendente)
  - Botão de remoção
  - Botão "Nova Empresa"

- **Gráfico de Evolução**:
  - Chart.js line chart
  - Múltiplas linhas (uma por empresa)
  - Cores diferenciadas
  - Legenda automática
  - Hover interativo

#### Gerenciar Empresas
- **Cards de Empresas**:
  - Nome e equipe
  - Senha visível (em code tag)
  - Lucro total
  - Recursos disponíveis listados
  - Botão de remover

- **Modal de Nova Empresa**:
  - Campo nome (obrigatório)
  - Campo equipe (opcional)
  - Campo senha com botão "Gerar"
  - Gerador automático de senhas

### 👨‍🎓 Área dos Alunos

#### Dashboard da Empresa
- **Header com Info**:
  - Nome da empresa (grande)
  - Nome da equipe
  - Iteração atual
  - Badge de status (Aberta/Fechada)

- **Cards de Recursos** (4 cards coloridos):
  - 💰 Dinheiro (azul)
  - 📦 Matéria-Prima (laranja)
  - ⚡ Energia (amarelo)
  - 👥 Trabalhadores (roxo)
  - Valores grandes e legíveis

- **Lucro Acumulado**:
  - Card centralizado
  - Valor grande
  - Verde se positivo, vermelho se negativo

- **Formulário de Decisão**:
  - Para cada produto:
    - Nome com emoji
    - Preço de venda e custo
    - Slider (0-100)
    - Input numérico (sincronizado)
    - Info de recursos por unidade
  
  - Botões:
    - "Validar Decisão" (azul)
    - "Enviar Decisão" (verde, grande)
  
  - Alert de confirmação (verde) se já enviou

- **Análise em Tempo Real**:
  - **Métricas Projetadas** (4 boxes):
    - Receita
    - Custo
    - Lucro (colorido)
    - Margem (%)
  
  - **Consumo de Recursos**:
    - Barra de progresso para cada recurso
    - Texto: usado / disponível
    - Cores: verde (<80%), amarelo (80-100%), vermelho (>100%)
  
  - **Alertas de Validação**:
    - Alert vermelho: recursos insuficientes
    - Lista de deficits
    - Alert verde: decisão válida

- **Histórico de Decisões**:
  - Tabela compacta
  - Turno e Lucro
  - Badges coloridos por resultado

- **Gráfico de Recursos**:
  - Chart.js line chart
  - 4 linhas (recursos)
  - Cores fixas por recurso
  - Legenda na parte inferior

## 🎯 Interatividade AJAX

### Sem Recarregar Página:
1. **Validação de Decisão**:
   - Sliders movem → input atualiza
   - Input muda → slider atualiza
   - Após 500ms → valida automaticamente
   - Atualiza métricas em tempo real
   - Atualiza barras de progresso
   - Mostra/esconde alertas

2. **Envio de Decisão**:
   - POST via AJAX
   - Loading spinner durante envio
   - Toast notification de sucesso/erro
   - Recarrega após 1.5s

3. **Processar Turno** (Admin):
   - Confirmação modal
   - Loading spinner
   - POST via AJAX
   - Toast notification
   - Recarrega dashboard

4. **Criar/Remover Empresa**:
   - Modal Bootstrap
   - POST/DELETE via AJAX
   - Validação client-side
   - Feedback via toast
   - Atualização automática da lista

5. **Auto-refresh** (Dashboard Admin):
   - Gráficos atualizam a cada 30s
   - Sem reload completo da página

## 🎨 Paleta de Cores

### Cores Principais:
- **Primary**: #2c3e50 (azul escuro)
- **Secondary**: #3498db (azul claro)
- **Success**: #27ae60 (verde)
- **Danger**: #e74c3c (vermelho)
- **Warning**: #f39c12 (laranja/amarelo)
- **Info**: #16a085 (turquesa)

### Recursos:
- **Dinheiro**: #1ABC9C (turquesa)
- **Matéria-Prima**: #E67E22 (laranja)
- **Energia**: #F39C12 (amarelo/ouro)
- **Trabalhadores**: #9B59B6 (roxo)

### Background:
- Gradiente purple/blue no body
- Cards brancos com sombra
- Navbar escuro (#1a252f)

## 📱 Responsividade

### Desktop (>1200px):
- 4 colunas de stats
- 2 colunas para dashboards
- Gráficos grandes (300px altura)

### Tablet (768px - 1200px):
- 2-3 colunas de stats
- 1-2 colunas para dashboards
- Gráficos médios

### Mobile (<768px):
- 1 coluna (tudo empilhado)
- Stats em 2 colunas (50% cada)
- Gráficos compactos (250px altura)
- Botões full-width
- Font sizes reduzidos

## ✨ Animações e Efeitos

### Hover:
- Cards: elevam (-5px) + sombra maior
- Botões: elevam (-2px) + sombra
- Transições suaves (0.3s ease)

### Loading:
- Spinner overlay (tela inteira)
- Fundo escuro semi-transparente
- Spinner Bootstrap branco e grande

### Toasts:
- Aparecem no canto superior direito
- Cores por tipo (success, danger, info, warning)
- Auto-dismiss após 5s
- Animação de slide-in

### Progress Bars:
- Cores dinâmicas baseadas em percentual
- Transições animadas
- Texto dentro da barra

## 🎮 UX Features

### Feedback Visual:
- Botões desabilitam durante operações
- Loading spinners em ações assíncronas
- Badges de status coloridos
- Alertas contextuais

### Validação:
- Client-side antes de enviar
- Mensagens claras de erro
- Campos obrigatórios marcados
- Feedback em tempo real

### Navegação:
- Navbar sempre visível
- Breadcrumbs contextuais
- Botões "Voltar"
- Links claros

### Acessibilidade:
- Labels em todos inputs
- Alt text em ícones importantes
- Contraste adequado
- Tamanhos de fonte legíveis
- Botões grandes em mobile

---

## 🎨 Customização Rápida

### Mudar Cores:
Edite `templates/base.html`, seção `:root`:
```css
:root {
    --primary-color: #SUA_COR;
    --secondary-color: #SUA_COR;
    /* ... */
}
```

### Mudar Logo/Título:
Edite navbar em `templates/base.html`:
```html
<a class="navbar-brand" href="...">
    <i class="bi bi-ICONE"></i> SEU TÍTULO
</a>
```

### Adicionar Produto:
Edite `src/config/constants.py`:
```python
PRODUTOS = {
    "🆕 Novo Produto": {
        "custo_materia": X,
        "custo_energia": Y,
        # ...
    }
}
```

---

**Interface moderna, responsiva e intuitiva! 🎨✨**
