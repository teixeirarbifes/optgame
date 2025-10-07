# Correções de Bugs - 06/10/2025

## 1. Ranking não atualiza automaticamente após processar turno

**Problema:** Quando o professor processava o turno, o lucro total no ranking não atualizava automaticamente sem recarregar a página.

**Causa:** Referência a `lucro_acumulado` (que não existe mais) na função `atualizarListaEmpresas()`.

**Correção:** `src/web_app/templates/admin/dashboard.html` linha ~1190
```javascript
// ANTES - com erro
rankingRow.find('td:eq(2)').html(`
    <span class="badge ${lucroClass}">R$ ${empresa.lucro_total...}</span>
    <br><small class="text-muted">Acum: R$ ${empresa.lucro_acumulado...}</small>
`);

// DEPOIS - corrigido
rankingRow.find('td:eq(2)').html(`
    <span class="badge ${lucroClass}">R$ ${empresa.lucro_total...}</span>
`);
```

**Resultado:** ✅ Ranking atualiza automaticamente via AJAX a cada 3 segundos.

---

## 2. Sliders não atualizam ao enviar solução ótima

**Problema:** Quando o admin clica em "Enviar Ótimo" ou "Aplicar Ótimo", os valores são preenchidos no backend, mas os sliders na tela do aluno não atualizam automaticamente.

**Causa:** 
1. API `/aluno/api/estado` não retornava `decisoes_nao_confirmadas`
2. JavaScript não verificava e atualizava sliders com decisões pendentes

**Correção 1:** `src/web_app/routes.py` linha ~708
```python
return jsonify({
    'iteracao_atual': game_state.iteracao_atual,
    'iteracao_aberta': game_state.iteracao_aberta,
    # ... outros campos ...
    'decisoes_nao_confirmadas': empresa.get('decisoes_nao_confirmadas', {}),  # NOVO
    'historico': empresa.get('historico', [])
})
```

**Correção 2:** `src/web_app/templates/aluno/dashboard.html` linha ~1270
```javascript
// Atualizar sliders se houver decisões não confirmadas
if (data.decisoes_nao_confirmadas && Object.keys(data.decisoes_nao_confirmadas).length > 0 && !data.decisao_confirmada) {
    console.log('Atualizando sliders com decisões pendentes:', data.decisoes_nao_confirmadas);
    
    // Atualizar cada produto
    Object.keys(data.decisoes_nao_confirmadas).forEach(function(produto) {
        const quantidade = data.decisoes_nao_confirmadas[produto];
        
        // Atualizar input numérico
        const input = $('input[data-produto="' + produto + '"]');
        if (input.length) {
            input.val(quantidade);
        }
        
        // Atualizar slider correspondente
        const sliderId = input.attr('id');
        if (sliderId) {
            const sliderIndex = sliderId.split('_')[1];
            const slider = $('#slider_' + sliderIndex);
            if (slider.length) {
                slider.val(quantidade);
            }
        }
        
        // Trigger do evento para atualizar displays
        input.trigger('input');
    });
    
    // Recalcular recursos após atualizar sliders
    calcularRecursos();
}
```

**Resultado:** ✅ Sliders atualizam automaticamente via AJAX quando admin envia solução ótima.

---

## 3. Gráfico de evolução mostra lucro negativo ao invés de custo positivo

**Problema:** No gráfico "Evolução de Recursos", o eixo do Dinheiro mostrava valores negativos (lucro negativo) ao invés do custo positivo.

**Causa:** Para dinheiro, `recursos_disponiveis` = `recursos_base` + `receita` - `custo`
Ao calcular `recursos_base - recursos_disponiveis`, obtinha-se `custo - receita` (lucro negativo), não o custo.

**Lógica Incorreta:**
```javascript
// ANTES
dinheiro: dadosRecursos.dinheiro.map(d => recursos_base.dinheiro - d)
// Resultado: 50000 - (50000 + receita - custo) = custo - receita ❌
```

**Correção:** `src/web_app/templates/aluno/dashboard.html` linha ~915
```javascript
// DEPOIS
// Histórico de custos (para calcular consumo de dinheiro corretamente)
const historicoCustos = {{ empresa.historico|tojson }};

// Calcular consumo
const dadosConsumo = {
    turnos: dadosRecursos.turnos,
    dinheiro: historicoCustos.map(h => h.custo || 0),  // CUSTO POSITIVO ✓
    materia_prima: dadosRecursos.materia_prima.map(m => recursos_base.materia_prima - m),
    energia: dadosRecursos.energia.map(e => recursos_base.energia - e),
    trabalhadores: dadosRecursos.trabalhadores.map(t => recursos_base.trabalhadores - t)
};
```

**Explicação:**
- **Outros recursos** (matéria-prima, energia, trabalhadores): `base - disponível` = consumo ✓
- **Dinheiro**: precisa usar `custo` diretamente do histórico, porque `recursos_disponiveis` inclui receita

**Resultado:** ✅ Gráfico mostra custo positivo corretamente para todos os recursos.

---

## Arquivos Modificados

1. **`src/web_app/templates/admin/dashboard.html`**
   - Linha ~1190: Removida referência a `lucro_acumulado`
   - Resultado: Ranking atualiza automaticamente

2. **`src/web_app/routes.py`**
   - Linha ~708: Adicionado `decisoes_nao_confirmadas` ao retorno da API
   - Resultado: Frontend pode detectar decisões pendentes

3. **`src/web_app/templates/aluno/dashboard.html`**
   - Linha ~915: Corrigido cálculo de consumo de dinheiro (usa histórico de custos)
   - Linha ~1270: Adicionada lógica para atualizar sliders com decisões pendentes
   - Resultado: Gráfico correto + sliders atualizam automaticamente

---

## Testes Recomendados

### Teste 1: Ranking
1. Como admin, processar turno
2. Verificar que lucros no ranking atualizam automaticamente (sem F5)
3. ✅ Esperado: Atualização em ~3 segundos

### Teste 2: Sliders
1. Como admin, clicar "Enviar Ótimo" para uma empresa
2. Logar como essa empresa (em outra aba/janela)
3. ✅ Esperado: Sliders mostram valores ótimos em ~3 segundos
4. Empresa pode modificar e confirmar

### Teste 3: Gráfico de Dinheiro
1. Como aluno, jogar algumas rodadas
2. Ver gráfico "Evolução de Recursos" → Dinheiro
3. ✅ Esperado: Linha de consumo sempre positiva, aumentando com custos

### Teste 4: Gráfico de outros recursos
1. Ver gráficos de Matéria-Prima, Energia, Trabalhadores
2. ✅ Esperado: Consumo positivo, mostrando quanto foi usado

---

## Comportamento Esperado

### Dashboard Admin - Ranking
```
┌─────────────────────────────┐
│ 🏆 Empresa A  R$ 15.234,56  │ <- Atualiza automaticamente
│ 🥈 Empresa B  R$ 12.543,21  │    sem recarregar página
│ 🥉 Empresa C  R$  9.876,54  │
└─────────────────────────────┘
```

### Dashboard Aluno - Sliders (após "Enviar Ótimo")
```
Produto A: [=========>     ] 450  <- Atualiza automaticamente
Produto B: [=====>         ] 200     após admin enviar ótimo
Produto C: [==>            ]  80
```

### Gráfico - Evolução de Recursos
```
Consumo de Dinheiro (R$)
  50k ┤ ┌─ Limite Superior (Vermelho tracejado)
      │ │
  40k ┤ │
      │ │    ┌──
  30k ┤ │  ┌─┘
      │ │ ┌┘
  20k ┤ │┌┘
      │┌┘  <- Consumo (sempre positivo)
  10k ┤┘
      │
    0 └─────────────────
      T1  T2  T3  T4  T5
```

---

## Compatibilidade

- ✅ Funciona com AJAX polling (3 segundos)
- ✅ Não requer recarga de página
- ✅ Mantém estado do jogo sincronizado
- ✅ Compatible com sistema GAP% existente
- ✅ Não interfere com save/load

---

## Notas Técnicas

**Por que dinheiro é diferente?**

No processamento do turno (game_state.py linha ~263):
```python
recursos_apos['dinheiro'] += receita_total  # Soma receita
recursos_apos['dinheiro'] -= custo_total    # Subtrai custo
```

Então `recursos_disponiveis['dinheiro']` não é simplesmente `base - consumo`, mas sim `base + receita - custo`.

Para os outros recursos (matéria-prima, energia, trabalhadores), não há "receita", apenas consumo:
```python
recursos_apos['materia_prima'] -= consumo['materia_prima']
```

Por isso o cálculo `base - disponível` funciona para eles, mas não para dinheiro.

**Solução:** Usar `historico[].custo` diretamente para o gráfico de dinheiro.
