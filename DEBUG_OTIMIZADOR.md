# Debug do Otimizador

## Problema Identificado

Empresa conseguiu lucro de **R$ 48.853,90** manualmente, mas otimizador diz que o máximo é **R$ 29.606,90**.

## Hipóteses

### 1. Recursos Diferentes
- Otimizador usa `recursos_disponiveis` 
- Pode estar usando recursos de uma iteração anterior
- Verificar se está usando `recursos_base` ou `recursos_disponiveis`

### 2. Fórmula de Lucro
**No Jogo (mechanics.py):**
```python
lucro = receita - custo_dinheiro
```
Onde:
```python
custo_dinheiro = Σ(quantidade × custo_financeiro_produto)
custo_financeiro_produto = consumo_materia × 1.20 + consumo_energia × 0.65 + consumo_trabalho × 22.00
```

**No Otimizador:**
```python
lucro = receita - (custo_materia + custo_energia + custo_trabalho)
custo_materia = Σ(quantidade × consumo_materia × 1.20)
custo_energia = Σ(quantidade × consumo_energia × 0.65)
custo_trabalho = Σ(quantidade × consumo_trabalho × 22.00)
```

**São equivalentes!**

### 3. Restrições do Otimizador

O otimizador tem 4 restrições:
1. `consumo_materia ≤ recursos_disponiveis['materia_prima']`
2. `consumo_energia ≤ recursos_disponiveis['energia']`
3. `consumo_trabalho ≤ recursos_disponiveis['trabalhadores']`
4. `custo_total ≤ recursos_disponiveis['dinheiro']`

**IMPORTANTE:** Se `recursos_disponiveis` estiver com valores menores que os reais, o otimizador vai encontrar uma solução subótima!

## Teste para Confirmar

### Passo 1: Ver os logs do otimizador
```
🔍 OTIMIZADOR - Recursos Disponíveis:
   💰 Dinheiro: R$ ???
   📦 Matéria-prima: ???
   ⚡ Energia: ???
   👷 Trabalhadores: ???
```

### Passo 2: Comparar com os recursos reais da empresa
Na tela do admin, verificar os recursos atuais da empresa.

### Passo 3: Ver a decisão que gerou R$ 48.853,90
Verificar quantas unidades de cada produto foram produzidas.

## Possível Causa

O método `calcular_solucao_otima` pode estar usando:
```python
recursos = empresa['recursos_disponiveis'].copy()
```

Mas `recursos_disponiveis` pode estar **DESATUALIZADO** (valores após última iteração).

Deveria usar `recursos_base` que são os recursos fixos!

## Solução

Modificar `game_state.py` para usar `recursos_base` em vez de `recursos_disponiveis` ao calcular solução ótima.

```python
# ERRADO (usa recursos após consumo da iteração anterior)
recursos = empresa['recursos_disponiveis'].copy()

# CORRETO (usa recursos base que resetam a cada iteração)
recursos = empresa['recursos_base'].copy()
```
