# Correções do Sistema de GAP%

## Mudanças Implementadas

### 1. ✅ Removido "Acum" do Ranking
**Antes:**
```
Empresa A
R$ 48.853,90
Acum: R$ 110.437,50  ← REMOVIDO
```

**Depois:**
```
Empresa A
R$ 48.853,90
```

**Motivo:** Ranking deve mostrar apenas o lucro da última iteração (atual), não o acumulado histórico.

---

### 2. ✅ Removido "Lucro Ótimo" da Tabela de Empresas
**Antes:**
```
Empresa A
Última: R$ 48.853,90
Acum: R$ 110.437,50
Ótimo: R$ 50.000,00  ← REMOVIDO
```

**Depois:**
```
Empresa A
Última: R$ 48.853,90
```

**Motivo:** Não deve exibir o lucro ótimo diretamente, apenas o GAP%.

---

### 3. ✅ Cálculo Correto do GAP%

**Fórmula:**
```python
GAP% = ((Lucro_Ótimo - Lucro_Atual) / Lucro_Ótimo) × 100
GAP% = max(0, GAP%)  # Nunca negativo
```

**Exemplos:**
- Atual = 48.853, Ótimo = 50.000 → GAP = 2,3% ✅
- Atual = 25.000, Ótimo = 50.000 → GAP = 50% ✅
- Atual = 0, Ótimo = 50.000 → GAP = 100% ✅
- Atual = -10.000, Ótimo = 50.000 → GAP = 120% ✅ (pode passar de 100%)
- Atual = 50.000, Ótimo = 50.000 → GAP = 0% ✅ (perfeito!)
- Atual = 55.000, Ótimo = 50.000 → GAP = 0% ✅ (melhor que ótimo = GAP 0%)

**Lógica:**
- GAP% = 0% significa que a empresa atingiu ou superou o lucro ótimo
- GAP% = 100% significa que a empresa teve lucro zero
- GAP% > 100% significa que a empresa teve prejuízo
- GAP% nunca é negativo

---

### 4. ✅ Atualização Automática do GAP ao Processar Turno

**Implementação:**
```python
# Após processar turno, recalcula GAP para todas empresas
for nome_empresa, empresa in self.empresas.items():
    if empresa.get('lucro_otimo', 0) > 0:
        lucro_atual = empresa.get('lucro_ultimo_turno', 0)
        lucro_otimo = empresa['lucro_otimo']
        
        if lucro_otimo > 0:
            gap = ((lucro_otimo - lucro_atual) / lucro_otimo) * 100
            empresa['gap_percentual'] = max(0, gap)
```

**Quando ocorre:**
- Automaticamente após cada `processar_turno()`
- Apenas para empresas que já tem solução ótima calculada
- Usa o `lucro_ultimo_turno` (não o acumulado)

---

### 5. ✅ Toast Atualizado

**Antes:**
```
GAP%: 2.3% (Ótimo: R$ 50.000,00)  ← Mostrava lucro ótimo
```

**Depois:**
```
GAP%: 2.3% (Última: R$ 48.853,90)  ← Mostra lucro atual
```

---

## Arquivos Modificados

### 1. `src/web_app/game_state.py`

**Método `calcular_solucao_otima()` (linhas 547-568):**
- ✅ Usa `recursos_base` (corrigido anteriormente)
- ✅ Calcula GAP com fórmula correta
- ✅ `max(0, gap)` para evitar GAP negativo
- ✅ Logs de debug

**Método `_calcular_e_guardar_otimo()` (linhas 690-706):**
- ✅ Mesma lógica de cálculo de GAP
- ✅ Logs apenas com GAP% (não mostra lucro ótimo)

**Método `processar_turno()` (linhas 350-361):**
- ✅ Recalcula GAP% automaticamente após processar
- ✅ Apenas para empresas com `lucro_otimo > 0`
- ✅ Logs de atualização

### 2. `src/web_app/templates/admin/dashboard.html`

**Ranking (linha 209):**
- ❌ Removido: `<small>Acum: R$ XXX</small>`
- ✅ Mostra apenas lucro da última iteração

**Tabela de Empresas (linha 234):**
- ❌ Removido: `<small>Acum: R$ XXX</small>`
- ❌ Removido: `<small>Ótimo: R$ XXX</small>`
- ✅ Mostra apenas lucro da última iteração

**Função `calcularGap()` (linha 896):**
- ✅ Toast mostra: `GAP%: X.X% (Última: R$ Y.YY)`
- ✅ Atualiza badge GAP com cores
- ✅ Atualiza lucro_ultima na tabela

---

## Comportamento Esperado

### Ao Calcular GAP:
```
1. Admin clica botão "%" na linha da empresa
2. Sistema calcula solução ótima (usa recursos_base)
3. Calcula GAP = (Ótimo - Última) / Ótimo * 100
4. Badge GAP% é atualizado com cor:
   - Verde: ≤5%
   - Amarelo: ≤20%
   - Vermelho: >20%
5. Toast mostra: "GAP%: X.X% (Última: R$ Y.YY)"
```

### Ao Processar Turno:
```
1. Admin clica "Processar Turno"
2. Sistema processa decisões de todas empresas
3. Calcula lucro_ultimo_turno de cada empresa
4. AUTOMATICAMENTE recalcula GAP% para empresas com lucro_otimo
5. Dashboard é atualizado com novos valores
```

### No Ranking:
```
1. Empresas ordenadas por lucro_ultimo_turno (não acumulado)
2. Mostra apenas lucro da última iteração
3. Sem informação de lucro acumulado
```

---

## Exemplos de Teste

### Cenário 1: Empresa com decisão ótima
```
Iteração 1:
- Calcular GAP → Ótimo: R$ 50.000
- Empresa aplica ótimo → Lucro: R$ 50.000
- Processar turno → GAP atualizado para 0% ✅

Iteração 2:
- Empresa não envia decisão (repete última)
- Processar turno → Lucro: R$ 50.000
- GAP continua 0% ✅
```

### Cenário 2: Empresa com decisão subótima
```
Iteração 1:
- Calcular GAP → Ótimo: R$ 50.000
- Empresa decide manualmente → Lucro: R$ 30.000
- Processar turno → GAP atualizado para 40% ✅

Iteração 2:
- Calcular GAP novamente → Ótimo: R$ 50.000
- Empresa melhora decisão → Lucro: R$ 45.000
- Processar turno → GAP atualizado para 10% ✅
```

### Cenário 3: Empresa com prejuízo
```
Iteração 1:
- Calcular GAP → Ótimo: R$ 50.000
- Empresa viola recursos → Lucro: R$ 0
- Processar turno → GAP atualizado para 100% ✅

Iteração 2:
- Empresa tenta produzir muito → Lucro: R$ -20.000
- Processar turno → GAP atualizado para 140% ✅ (passou de 100%)
```

---

## Verificação

✅ GAP usa lucro da última iteração (não acumulado)
✅ GAP nunca é negativo (mínimo 0%)
✅ GAP pode passar de 100% (prejuízo)
✅ GAP é recalculado automaticamente ao processar turno
✅ Interface não mostra lucro ótimo (apenas GAP%)
✅ Ranking mostra apenas lucro da última iteração
✅ Tabela mostra apenas lucro da última iteração

---

## Commit

```
fix: corrigir exibição e cálculo do GAP%

- Removido lucro acumulado do ranking e tabela
- Removido exibição do lucro ótimo
- GAP% agora é recalculado automaticamente ao processar turno
- GAP% nunca é negativo (mínimo 0%)
- GAP% pode passar de 100% em caso de prejuízo
- Interface simplificada mostra apenas última iteração
```
