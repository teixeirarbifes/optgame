# Sistema de GAP% e Otimização Automática

## Resumo

Implementado sistema completo de cálculo de GAP% (diferença entre lucro atual e lucro ótimo) com controles no dashboard do administrador.

## Funcionalidades Implementadas

### 1. Campos Adicionados às Empresas

Cada empresa agora possui:
- `solucao_otima`: Dict com a produção ótima calculada (guardada internamente)
- `lucro_otimo`: Float com o lucro máximo possível
- `gap_percentual`: Float com o GAP% = ((lucro_otimo - lucro_atual) / lucro_otimo) * 100

### 2. Flag de Controle

- `calcular_otimo_ao_criar` (padrão: `False`)
  - Quando ativada, calcula automaticamente a solução ótima ao criar nova empresa
  - Pode ser ativada/desativada via endpoint `/admin/api/toggle-calcular-otimo-ao-criar`

### 3. Novos Métodos em GameState

#### `_calcular_e_guardar_otimo(nome_empresa)`
- Método privado auxiliar
- Calcula e guarda solução ótima internamente
- Retorna bool indicando sucesso
- Usado ao criar empresa (se flag ativada)

#### `enviar_solucao_para_empresa(nome_empresa)`
- Envia solução ótima para a tela da empresa
- Preenche `decisao_atual` mas **NÃO confirma** (`decisao_confirmada = False`)
- Empresa pode ver os valores e modificar antes de confirmar
- Usado pelo botão "📤 Enviar Ótimo"

#### `calcular_otimo_sem_mostrar(nome_empresa)`
- Calcula solução ótima SEM MOSTRAR na tela
- Retorna apenas: lucro_atual, lucro_otimo, gap_percentual
- Usado pelo botão de "Calcular GAP%"

#### `calcular_otimo_todas_empresas()`
- Calcula solução ótima para TODAS as empresas
- Retorna resumo: total_empresas, calculados, falhas, resultados[]
- Usado pelo botão "Calcular Todas"

#### `enviar_otimo_todas_empresas()`
- Envia solução ótima para TODAS as empresas (SEM confirmar)
- Empresas podem modificar antes de confirmar
- Retorna resumo: total_empresas, enviados, falhas
- Usado pelo botão "📤 Enviar para Todas"

#### `aplicar_otimo_todas_empresas()`
- Aplica E CONFIRMA solução ótima em TODAS as empresas
- Define GAP = 0% para todas
- Empresas NÃO podem modificar
- Retorna resumo: total_empresas, aplicados, falhas
- Usado pelo botão "⚡ Aplicar em Todas"

### 4. Novos Endpoints (routes.py)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/admin/api/calcular-otimo-sem-mostrar/<nome_empresa>` | POST | Calcular GAP% sem mostrar solução |
| `/admin/api/calcular-otimo-todas` | POST | Calcular ótimo para todas empresas |
| `/admin/api/enviar-otimizacao/<nome_empresa>` | POST | Enviar ótimo para empresa (pode modificar) |
| `/admin/api/aplicar-otimizacao/<nome_empresa>` | POST | Aplicar e confirmar ótimo (GAP 0%) |
| `/admin/api/enviar-otimo-todas` | POST | Enviar ótimo para todas (podem modificar) |
| `/admin/api/aplicar-otimo-todas` | POST | Aplicar e confirmar em todas (GAP 0%) |
| `/admin/api/toggle-calcular-otimo-ao-criar` | POST | Ativar/desativar cálculo ao criar |
| `/admin/api/status-calcular-otimo-ao-criar` | GET | Obter status da flag |

### 5. Interface do Dashboard Admin

#### Tabela de Empresas

**Nova coluna "GAP%":**
- Badge colorido:
  - 🟢 Verde: GAP ≤ 5% (excelente)
  - 🟡 Amarelo: GAP ≤ 20% (bom)
  - 🔴 Vermelho: GAP > 20% (pode melhorar)
- Mostra "-" se não calculado ainda

**Novos botões por empresa:**
- **% (Calcular GAP)**: Calcula solução ótima sem mostrar, exibe apenas GAP%
- **🧮 (Calcular Ótimo)**: Calcula e MOSTRA solução ótima em modal
- **⚡ (Aplicar Ótimo)**: Aplica solução ótima (GAP 0%)

**Informações adicionais:**
- Mostra "Ótimo: R$ X.XX" abaixo do lucro acumulado (quando calculado)

#### Botões Globais

Adicionados na seção "Controles do Jogo":

- **🔢 Calcular Todas**: Calcula solução ótima para todas empresas
- **⚡ Aplicar Ótimo em Todas**: Aplica solução ótima em todas (GAP 0%)

### 6. Funções JavaScript Adicionadas

#### `calcularGap(nomeEmpresa)`
- Chama endpoint de calcular GAP sem mostrar solução
- Atualiza badge GAP% dinamicamente na tabela
- Mostra toast com resultado

#### `calcularOtimoTodas()`
- Chama endpoint para calcular todas
- Mostra confirmação antes
- Atualiza dashboard após conclusão

#### `aplicarOtimoTodas()`
- Chama endpoint para aplicar em todas
- Confirmação com aviso destacado
- Define GAP = 0% para todas empresas

## Fluxo de Uso

### Cenário 1: Calcular GAP de Uma Empresa

1. Admin clica botão **%** na linha da empresa
2. Sistema calcula solução ótima internamente
3. Mostra toast: "GAP: X.X% (Ótimo: R$ Y.YY)"
4. Badge GAP% é atualizado com cor apropriada
5. Solução NÃO é mostrada na tela

### Cenário 2: Calcular Todas as Empresas

1. Admin clica **Calcular Todas**
2. Sistema processa todas empresas sequencialmente
3. Toast mostra: "Cálculo concluído: N empresas processadas"
4. Dashboard é atualizado com todos os GAPs

### Cenário 3: Aplicar Ótimo em Todas

1. Admin clica **Aplicar Ótimo em Todas**
2. Confirmação destacada é exibida
3. Sistema aplica solução ótima em todas empresas
4. Todas as decisões são substituídas pela solução ótima
5. Todas empresas ficam com GAP = 0%

### Cenário 4: Criar Empresa com Auto-Cálculo

1. Admin ativa flag `calcular_otimo_ao_criar` (via endpoint)
2. Ao criar nova empresa:
   - Sistema cria a empresa normalmente
   - Automaticamente calcula solução ótima
   - Guarda lucro_otimo e solucao_otima
   - Empresa já tem GAP% calculado desde o início

## Compatibilidade com Saves Antigos

O método `carregar_estado()` foi atualizado para adicionar campos novos em saves antigos:

```python
if 'solucao_otima' not in empresa:
    empresa['solucao_otima'] = None
if 'lucro_otimo' not in empresa:
    empresa['lucro_otimo'] = 0
if 'gap_percentual' not in empresa:
    empresa['gap_percentual'] = None
```

## Cálculo do GAP%

```
GAP% = ((Lucro Ótimo - Lucro Atual) / Lucro Ótimo) × 100

Exemplos:
- Lucro Atual: R$ 9.500, Ótimo: R$ 10.000 → GAP = 5% 🟢
- Lucro Atual: R$ 8.000, Ótimo: R$ 10.000 → GAP = 20% 🟡
- Lucro Atual: R$ 5.000, Ótimo: R$ 10.000 → GAP = 50% 🔴
- Lucro Atual: R$ 10.000, Ótimo: R$ 10.000 → GAP = 0% (perfeito!)
```

## Segurança

- Todos os endpoints exigem autenticação de admin (`@admin_required`)
- Todos os POST exigem token CSRF (`@csrf_required`)
- Solução ótima é guardada internamente, não é exposta automaticamente
- Admin controla quando calcular e quando mostrar

## Arquivos Modificados

1. **src/web_app/game_state.py**
   - Adicionada flag `calcular_otimo_ao_criar`
   - Novos campos em empresa: `solucao_otima`, `lucro_otimo`, `gap_percentual`
   - Métodos: `_calcular_e_guardar_otimo`, `calcular_otimo_sem_mostrar`, `calcular_otimo_todas_empresas`, `aplicar_otimo_todas_empresas`
   - Backward compatibility em `carregar_estado()`

2. **src/web_app/routes.py**
   - 5 novos endpoints para controle de otimização global

3. **src/web_app/templates/admin/dashboard.html**
   - Nova coluna GAP% na tabela
   - Novos botões por empresa e botões globais
   - 4 novas funções JavaScript
   - Badge colorido para GAP%

## Benefícios

✅ **Transparência**: Admin pode ver eficiência de cada empresa
✅ **Controle**: Pode calcular sem mostrar solução
✅ **Produtividade**: Calcular/aplicar em massa
✅ **Feedback Visual**: Cores indicam performance
✅ **Flexibilidade**: Flag controla auto-cálculo ao criar
✅ **Privacidade**: Solução guardada internamente, não exposta

## Próximos Passos Possíveis

- [ ] Histórico de GAP% ao longo das iterações
- [ ] Gráfico de evolução do GAP%
- [ ] Ranking por melhor GAP% (quem está mais próximo do ótimo)
- [ ] Exportar relatório de GAP% para CSV
- [ ] Notificações quando GAP% melhora/piora significativamente
