# 📐 Modelo Matemático Corrigido e Balanceado

## 🎯 Estrutura do Modelo

### 1. **Recursos Disponíveis (R_j)**

```
💰 Dinheiro:           50.000  (capital inicial)
📦 Matéria-Prima:      25.000  (unidades)
⚡ Energia:            18.000  (kWh)
👥 Trabalhadores:         800  (horas-trabalhador)
```

---

### 2. **Custos Unitários dos Recursos (r_j)**

```
📦 Matéria-Prima:    R$ 1,50 por unidade
⚡ Energia:          R$ 0,80 por kWh
👥 Trabalhadores:    R$ 25,00 por hora-trabalhador
```

---

### 3. **Produtos e Consumos (c_ij)**

| Produto | 📦 Matéria | ⚡ Energia | 👥 Trabalho | 💵 Preço | 💰 Margem* |
|---------|-----------|-----------|-------------|----------|-----------|
| 📱 Smartphone | 15 | 8 | 0,4 | R$ 85 | R$ 52,10 (61%) |
| 💻 Laptop | 35 | 18 | 1,2 | R$ 180 | R$ 92,90 (52%) |
| 🖥️ Desktop | 50 | 25 | 1,8 | R$ 250 | R$ 120,00 (48%) |
| ⌚ Smartwatch | 8 | 4 | 0,3 | R$ 45 | R$ 22,30 (50%) |
| 🖨️ Impressora | 28 | 12 | 0,8 | R$ 120 | R$ 60,40 (50%) |
| 📷 Câmera | 22 | 10 | 0,6 | R$ 95 | R$ 48,20 (51%) |

**Margem = Preço - (Σ consumo × custo_unitário)*

---

### 4. **Cálculo de Custos**

#### Fórmula Geral:
```
CUSTO_PRODUTO_i = Σ (c_ij × r_j)

Onde:
  c_ij = consumo do recurso j para produzir 1 unidade do produto i
  r_j = custo unitário do recurso j
```

#### Exemplo: Custo de 1 Smartphone
```
Custo = (15 × R$ 1,50) + (8 × R$ 0,80) + (0,4 × R$ 25,00)
Custo = R$ 22,50 + R$ 6,40 + R$ 10,00
Custo = R$ 38,90
```

#### Exemplo: Lucro de 1 Smartphone
```
Lucro = Preço_Venda - Custo
Lucro = R$ 85,00 - R$ 38,90
Lucro = R$ 46,10
```

---

### 5. **Modelo de Otimização**

#### Variáveis de Decisão:
```
q_i = quantidade a produzir do produto i (i = 1, 2, ..., 6)
```

#### Função Objetivo (Maximizar):
```
Z = Σ (p_i × q_i) - Σ Σ (c_ij × r_j × q_i)

Onde:
  Z = lucro total
  p_i = preço de venda do produto i
  q_i = quantidade produzida do produto i
  c_ij = consumo do recurso j para produzir 1 unidade do produto i
  r_j = custo unitário do recurso j
```

#### Restrições:

**1. Restrição de Matéria-Prima:**
```
Σ (c_i,materia × q_i) ≤ 25.000
```

**2. Restrição de Energia:**
```
Σ (c_i,energia × q_i) ≤ 18.000
```

**3. Restrição de Trabalhadores:**
```
Σ (c_i,trabalho × q_i) ≤ 800
```

**4. Restrição de Capital:**
```
Σ (custo_total_i × q_i) ≤ 50.000
```

**5. Não-negatividade:**
```
q_i ≥ 0, para todo i
```

---

### 6. **Análise de Trade-offs**

#### Comparação por Margem Unitária:
```
📱 Smartphone:  R$ 46,10  (🏆 MELHOR margem em R$)
💻 Laptop:      R$ 92,90  (🏆🏆 MUITO BOA margem)
🖥️ Desktop:     R$ 120,00 (🏆🏆🏆 ÓTIMA margem, mas consome muito)
⌚ Smartwatch:  R$ 22,30  (Baixa margem, mas pouco consumo)
🖨️ Impressora:  R$ 60,40  (Boa margem intermediária)
📷 Câmera:      R$ 48,20  (Boa margem intermediária)
```

#### Comparação por Eficiência de Recursos:

**Lucro por Unidade de Matéria-Prima:**
```
⌚ Smartwatch:  R$ 22,30 ÷ 8  = R$ 2,79 (🏆 MELHOR)
📱 Smartphone:  R$ 46,10 ÷ 15 = R$ 3,07 (🏆🏆 MUITO BOM)
📷 Câmera:      R$ 48,20 ÷ 22 = R$ 2,19
💻 Laptop:      R$ 92,90 ÷ 35 = R$ 2,65
🖨️ Impressora:  R$ 60,40 ÷ 28 = R$ 2,16
🖥️ Desktop:     R$ 120,00 ÷ 50 = R$ 2,40
```

**Lucro por Hora-Trabalhador:**
```
📱 Smartphone:  R$ 46,10 ÷ 0,4 = R$ 115,25 (🏆 MELHOR)
⌚ Smartwatch:  R$ 22,30 ÷ 0,3 = R$ 74,33
💻 Laptop:      R$ 92,90 ÷ 1,2 = R$ 77,42
📷 Câmera:      R$ 48,20 ÷ 0,6 = R$ 80,33
🖨️ Impressora:  R$ 60,40 ÷ 0,8 = R$ 75,50
🖥️ Desktop:     R$ 120,00 ÷ 1,8 = R$ 66,67
```

---

### 7. **Capacidade Produtiva Teórica**

#### Se produzir APENAS cada produto:

| Produto | Max por Matéria | Max por Energia | Max por Trabalho | Max por Dinheiro | **Limitante** |
|---------|----------------|----------------|-----------------|-----------------|---------------|
| 📱 Smartphone | 1.666 | 2.250 | 2.000 | 1.285 | **Dinheiro** (1.285) |
| 💻 Laptop | 714 | 1.000 | 666 | 543 | **Dinheiro** (543) |
| 🖥️ Desktop | 500 | 720 | 444 | 421 | **Dinheiro** (421) |
| ⌚ Smartwatch | 3.125 | 4.500 | 2.666 | 2.056 | **Dinheiro** (2.056) |
| 🖨️ Impressora | 892 | 1.500 | 1.000 | 862 | **Dinheiro** (862) |
| 📷 Câmera | 1.136 | 1.800 | 1.333 | 1.179 | **Dinheiro** (1.179) |

**Produção ótima total deve ficar em torno de 1.000 unidades combinadas**

---

### 8. **Exemplos de Estratégias**

#### Estratégia 1: Mix Balanceado
```
📱 Smartphone:  300 unidades
💻 Laptop:      150 unidades
🖥️ Desktop:     80 unidades
⌚ Smartwatch:  200 unidades
🖨️ Impressora:  100 unidades
📷 Câmera:      150 unidades

TOTAL: 980 unidades
```

#### Estratégia 2: Foco em Alta Margem
```
🖥️ Desktop:    250 unidades
💻 Laptop:     300 unidades
📱 Smartphone: 300 unidades

TOTAL: 850 unidades (menos volume, mas alta margem)
```

#### Estratégia 3: Alto Volume
```
⌚ Smartwatch:  600 unidades
📱 Smartphone:  400 unidades
📷 Câmera:      300 unidades

TOTAL: 1.300 unidades (mais volume, margem moderada)
```

---

### 9. **Cálculo do Lucro Total**

#### Fórmula:
```
LUCRO = Σ (p_i × q_i) - Σ (custo_i × q_i)

Onde:
  custo_i = Σ (c_ij × r_j)
```

#### Exemplo com Estratégia 1:
```
RECEITA:
  300 Smartphones × R$ 85    = R$ 25.500
  150 Laptops × R$ 180       = R$ 27.000
  80 Desktops × R$ 250       = R$ 20.000
  200 Smartwatches × R$ 45   = R$  9.000
  100 Impressoras × R$ 120   = R$ 12.000
  150 Câmeras × R$ 95        = R$ 14.250
  TOTAL RECEITA              = R$ 107.750

CUSTO:
  300 × R$ 38,90             = R$ 11.670
  150 × R$ 87,10             = R$ 13.065
  80 × R$ 130,00             = R$ 10.400
  200 × R$ 22,70             = R$  4.540
  100 × R$ 59,60             = R$  5.960
  150 × R$ 46,80             = R$  7.020
  TOTAL CUSTO                = R$ 52.655

LUCRO = R$ 107.750 - R$ 52.655 = R$ 55.095
```

---

## ✅ Vantagens do Novo Modelo

1. ✅ **Lógica Clara:** Consumo × Custo_Unitário = Custo_Total
2. ✅ **Trade-offs Interessantes:** Produtos diferentes têm vantagens em recursos diferentes
3. ✅ **Escala Realista:** ~1.000 unidades totais é um volume desafiador mas alcançável
4. ✅ **Margens Balanceadas:** Todos os produtos têm margem positiva (45-61%)
5. ✅ **Diversidade:** 6 produtos diferentes para escolher
6. ✅ **Recursos Limitados:** Cada recurso pode ser o gargalo dependendo da estratégia

---

## 🎓 Para os Alunos

### Como Decidir:

1. **Calcule o custo** de cada produto manualmente
2. **Compare as margens** unitárias
3. **Analise o consumo** de cada recurso
4. **Verifique seus recursos** disponíveis
5. **Teste combinações** diferentes
6. **Encontre o trade-off** ideal entre volume e margem

### Perguntas para Reflexão:

- É melhor produzir poucos itens de alta margem ou muitos itens de baixa margem?
- Qual recurso está limitando minha produção?
- Como posso usar melhor o recurso que está sobrando?
- Vale a pena produzir produtos com margem menor se eles consumem menos recursos?

---

**Data:** 6 de outubro de 2025  
**Versão:** 3.0 - Modelo Matemático Corrigido  
**Status:** ✅ Implementado
