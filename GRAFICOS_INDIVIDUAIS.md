# 📊 Gráficos Individuais de Recursos com Linha de Meta

## Nova Funcionalidade Implementada

### 🎯 Objetivo
Permitir que o usuário visualize a evolução de cada recurso **individualmente**, com uma **linha de meta/limite superior** mostrando o valor inicial/objetivo.

---

## 📍 Como Funciona

### Interface Atualizada

No card **"Evolução de Recursos"**, agora há botões de seleção:

```
┌─────────────────────────────────────────────────────────┐
│ 📊 Evolução de Recursos    [Todos] [💰] [📦] [⚡] [👥]  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│                    GRÁFICO AQUI                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Opções de Visualização

| Botão | Recurso | Descrição |
|-------|---------|-----------|
| **Todos** | Todos os recursos | Visão geral com todas as linhas |
| **💰** | Dinheiro | Gráfico individual com meta R$ 50.000 |
| **📦** | Matéria-Prima | Gráfico individual com meta 25.000 un |
| **⚡** | Energia | Gráfico individual com meta 18.000 kWh |
| **👥** | Trabalhadores | Gráfico individual com meta 800 h-trab |

---

## 🎨 Linha de Meta (Limite Superior)

### Visual
Quando você seleciona um recurso individual, aparece:

1. **Linha principal (sólida):** Evolução real do recurso
2. **Linha tracejada vermelha:** Meta/valor inicial do recurso

```
Exemplo: Gráfico de Matéria-Prima

  25.000 -------- . -------- . -------- . -------- (linha vermelha tracejada)
         \                                    
  20.000  \____                              
              \____                          
  15.000          \____/‾\                   (linha sólida colorida)
                        \                    
  10.000                 \____               
```

### Interpretação

#### ✅ Acima da Linha Vermelha
- **BOM!** Você está mantendo os recursos
- Gestão eficiente
- Sustentável no longo prazo

#### ⚠️ Abaixo da Linha Vermelha
- **ATENÇÃO!** Recursos em declínio
- Consumo maior que reposição
- Risco de ficar sem recursos

---

## 🔍 Detalhes Técnicos

### Valores de Meta/Inicial

| Recurso | Meta/Valor Inicial | Unidade |
|---------|-------------------|---------|
| 💰 Dinheiro | 50.000 | R$ |
| 📦 Matéria-Prima | 25.000 | unidades |
| ⚡ Energia | 18.000 | kWh |
| 👥 Trabalhadores | 800 | horas-trabalhador |

### Formatação por Recurso

**Dinheiro:**
```javascript
R$ 50.000,00
R$ 48.342,75
```

**Matéria-Prima:**
```javascript
25.000 un
23.450,5 un
```

**Energia:**
```javascript
18.000 kWh
15.234,8 kWh
```

**Trabalhadores:**
```javascript
800 h
528,6 h
```

---

## 📈 Recursos dos Gráficos Individuais

### 1. **Visualização Ampliada**
- Foco em um único recurso
- Escala otimizada para aquele recurso
- Pontos maiores e mais visíveis

### 2. **Linha de Referência**
- Linha tracejada vermelha
- Sempre no valor inicial/meta
- Facilita comparação visual

### 3. **Informação Contextual**
Abaixo do gráfico aparece:

```
ℹ️ A linha vermelha tracejada mostra o valor inicial/meta (25.000 un). 
   Mantenha-se acima para ter recursos disponíveis!
```

### 4. **Tooltips Detalhados**
Ao passar o mouse sobre os pontos:
```
💰 Dinheiro: R$ 48.342,75
📦 Matéria-Prima: 23.450,5 un
⚡ Energia: 15.234,8 kWh
👥 Trabalhadores: 528,6 h
```

---

## 🎯 Casos de Uso

### Caso 1: Monitorar Dinheiro
**Problema:** "Estou ficando sem dinheiro?"

**Solução:**
1. Clique no botão **💰**
2. Veja se a linha está abaixo de R$ 50.000
3. Se sim, você está tendo prejuízo acumulado
4. Ajuste estratégia: venda mais ou reduza custos

### Caso 2: Consumo de Matéria-Prima
**Problema:** "Meu estoque de matéria-prima está acabando?"

**Solução:**
1. Clique no botão **📦**
2. Se a linha está caindo, você está consumindo
3. A linha vermelha mostra seu estoque inicial (25.000)
4. Planeje reposição ou reduza produção

### Caso 3: Eficiência Energética
**Problema:** "Minha estratégia é sustentável em energia?"

**Solução:**
1. Clique no botão **⚡**
2. Se a linha sobe, você economiza energia
3. Se cai muito, escolha produtos menos energéticos
4. Compare com meta de 18.000 kWh

### Caso 4: Gestão de Horas-Trabalhador
**Problema:** "Estou sobrecarregando trabalhadores?"

**Solução:**
1. Clique no botão **👥**
2. Linha caindo = mais horas consumidas
3. Meta: 800 h-trab disponíveis
4. Escolha produtos que usam menos mão-de-obra

---

## 🎨 Cores e Identificação

| Recurso | Cor Principal | Cor da Meta |
|---------|--------------|-------------|
| 💰 Dinheiro | Verde (#28a745) | Vermelho tracejado |
| 📦 Matéria-Prima | Laranja (#e67e22) | Vermelho tracejado |
| ⚡ Energia | Amarelo (#f39c12) | Vermelho tracejado |
| 👥 Trabalhadores | Roxo (#9b59b6) | Vermelho tracejado |

---

## 🔄 Atualização Automática

Os gráficos individuais são atualizados automaticamente:
- **AJAX:** A cada 3 segundos
- **Após processar turno:** Reload automático
- **Todos os dados:** Sincronizados com servidor

---

## ✨ Benefícios Educacionais

### 1. **Análise Focada**
Estudantes podem analisar um recurso por vez sem distrações.

### 2. **Comparação com Meta**
A linha vermelha serve como referência constante.

### 3. **Detecção de Tendências**
Facilita ver se estão melhorando ou piorando.

### 4. **Tomada de Decisão**
```
Linha abaixo da meta = Preciso mudar estratégia
Linha acima da meta = Estratégia funcionando
Linha estável = Equilíbrio alcançado
```

---

## 📱 Responsividade

### Desktop
- Botões com texto e ícone
- Gráfico grande (350px altura)
- Tooltips completos

### Mobile
- Botões apenas com emoji
- Gráfico adaptado
- Touch-friendly

---

## 🚀 Como Usar

### Passo a Passo

1. **Acesse** o dashboard do aluno
2. **Role** até "Evolução de Recursos"
3. **Clique** no botão do recurso desejado:
   - **[Todos]** = Visão geral
   - **[💰]** = Só dinheiro + meta
   - **[📦]** = Só matéria-prima + meta
   - **[⚡]** = Só energia + meta
   - **[👥]** = Só trabalhadores + meta
4. **Observe** a linha vermelha tracejada (meta)
5. **Compare** sua linha colorida com a meta
6. **Ajuste** sua estratégia conforme necessário

---

## 📊 Exemplo Prático

### Cenário: Estudante jogou 5 turnos

**Visão Geral (Todos):**
```
Turno 0: Início
Turno 1-3: Crescimento de dinheiro, queda de recursos
Turno 4-5: Estabilização
```

**Gráfico Individual - Matéria-Prima (📦):**
```
Turno 0: 25.000 (linha vermelha na meta)
Turno 1: 22.000 (consumiu 3.000)
Turno 2: 19.500 (consumiu 2.500)
Turno 3: 17.800 (consumiu 1.700)
Turno 4: 16.200 (consumiu 1.600)
Turno 5: 14.800 (consumiu 1.400)

CONCLUSÃO: Linha muito abaixo da meta!
AÇÃO: Reduzir produção ou escolher produtos que usam menos matéria-prima.
```

---

## ✅ Status

✅ **IMPLEMENTADO** - Gráficos individuais com linha de meta funcionando!

Recarregue a página e teste os botões! 🚀

---

## 🎓 Dica Pedagógica

**Para professores:** Use os gráficos individuais para ensinar:
- Conceito de **sustentabilidade** (manter acima da meta)
- **Trade-offs** entre recursos
- **Planejamento de longo prazo**
- **Análise de tendências**

**Para alunos:** Use para:
- Identificar qual recurso está mais crítico
- Comparar estratégias entre turnos
- Visualizar impacto das decisões
- Planejar próximos movimentos
