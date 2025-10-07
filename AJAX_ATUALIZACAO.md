# 🔄 Sistema de Atualização Automática via AJAX

## Implementação Completa

### 📱 TELA DO JOGADOR (Aluno)

#### Atualização Automática (a cada 3 segundos)
✅ **Recursos disponíveis** - Atualiza valores sem recarregar página:
- 💰 Dinheiro
- 📦 Matéria-Prima
- ⚡ Energia
- 👥 Trabalhadores

✅ **Lucro do último turno** - Atualiza valor e cor (verde/vermelho)

✅ **Barras de progresso** - Atualiza percentual visual dos recursos

✅ **Detecção de mudança de iteração**:
- Quando admin abre nova iteração → recarrega página
- Quando admin fecha iteração → recarrega página

✅ **Preservação dos inputs**:
- Sliders e inputs numéricos **NÃO** são alterados durante atualizações
- Apenas atualiza quando muda de iteração (nova rodada)

✅ **Preenchimento automático**:
- No início de nova iteração, os inputs são preenchidos com os valores da iteração anterior
- Facilita ajustes incrementais da estratégia

#### Endpoint da API
```
GET /aluno/api/estado
```

Retorna:
```json
{
    "iteracao_atual": 3,
    "iteracao_aberta": true,
    "recursos": {
        "dinheiro": 45000,
        "materia_prima": 18000,
        "energia": 15000,
        "trabalhadores": 650
    },
    "recursos_maximos": { ... },
    "lucro_ultimo_turno": 2500.50,
    "decisao_anterior": {
        "📱 Smartphone": 10,
        "💻 Laptop": 5
    },
    "decisao_confirmada": true
}
```

---

### 👔 TELA DO ADMIN

#### Atualização Automática

**Gráfico de Lucros** (a cada 30 segundos):
- Atualiza automaticamente o gráfico comparativo
- Mostra evolução de todas as empresas

**Lista de Empresas** (a cada 3 segundos):
- ✅ Status de decisão (Confirmada/Pendente)
- ✅ Contador de empresas confirmadas
- ✅ Total de empresas
- ✅ Badges de status com cores dinâmicas

#### Endpoints da API
```
GET /api/ranking
```

Retorna empresas com campo adicional:
```json
[
    {
        "nome": "Empresa A",
        "equipe": "Equipe 1",
        "lucro_total": 5000,
        "recursos": { ... },
        "decisao_confirmada": true
    }
]
```

---

## 🎯 Comportamento Esperado

### Abertura de Nova Iteração (Admin)

1. **Admin clica em "Abrir Próxima Iteração"**
2. Backend executa `abrir_proxima_iteracao()`:
   - Define `iteracao_aberta = True`
   - Copia última decisão para `decisao_atual` de cada empresa
   - Marca todas como `decisao_confirmada = False`

3. **Tela dos Alunos** (via AJAX):
   - Detecta mudança de iteração
   - Recarrega página automaticamente
   - Formulário aparece preenchido com valores anteriores
   - Aluno pode ajustar e enviar nova decisão

4. **Tela do Admin** (via AJAX):
   - Atualiza contadores
   - Mostra status "Pendente" para todas empresas
   - Badge muda para amarelo ⏰

### Envio de Decisão (Aluno)

1. **Aluno ajusta valores e clica em "Confirmar Decisão"**
2. Backend registra decisão
3. Marca `decisao_confirmada = True`

4. **Tela do Admin** (via AJAX):
   - Status da empresa muda para "Confirmada" ✅
   - Badge fica verde
   - Contador de confirmadas aumenta

### Processamento de Turno (Admin)

1. **Admin clica em "Processar Turno Atual"**
2. Backend calcula resultados, consome recursos
3. Fecha iteração (`iteracao_aberta = False`)

4. **Tela dos Alunos** (via AJAX):
   - Detecta fechamento da iteração
   - Recarrega página
   - Formulário some (iteração fechada)
   - Mostra resultados do turno processado

---

## ⚙️ Configurações

### Intervalos de Atualização

**Jogadores:**
```javascript
setInterval(atualizarEstadoJogo, 3000); // 3 segundos
```

**Admin - Lista de Empresas:**
```javascript
setInterval(atualizarListaEmpresas, 3000); // 3 segundos
```

**Admin - Gráficos:**
```javascript
setInterval(atualizarGrafico, 30000); // 30 segundos
```

---

## 🛡️ Proteções Implementadas

✅ **Não altera inputs durante digitação**:
- Apenas lê valores quando muda de iteração
- Preserva o que o jogador está digitando

✅ **Detecção de mudança de estado**:
- Compara `iteracao_atual` e `iteracao_aberta` 
- Só recarrega quando realmente mudou

✅ **Tratamento de erros**:
- `console.error()` em caso de falha
- Não trava a interface

✅ **Performance**:
- Requisições leves (apenas JSON)
- Intervalos ajustados (3s vs 30s)

---

## 🧪 Como Testar

1. **Abra duas abas**: uma como admin, outra como aluno
2. **Como admin**: abra nova iteração
3. **Veja a tela do aluno**: deve recarregar e mostrar formulário
4. **Como aluno**: envie uma decisão
5. **Veja a tela do admin**: status deve mudar para "Confirmada" ✅
6. **Como admin**: processe o turno
7. **Veja a tela do aluno**: deve recarregar e esconder formulário

---

## 📝 Arquivos Modificados

1. `src/web_app/templates/aluno/dashboard.html`
   - JavaScript de atualização automática
   - IDs nos elementos HTML

2. `src/web_app/templates/admin/dashboard.html`
   - JavaScript de atualização automática
   - IDs e data-attributes

3. `src/web_app/routes.py`
   - Endpoint `/aluno/api/estado`
   - Atualização do `/api/ranking`

4. `src/web_app/game_state.py`
   - Lógica de preenchimento automático em `abrir_proxima_iteracao()`

---

## ✨ Benefícios

✅ **Experiência fluida**: Atualizações sem reload constante
✅ **Feedback visual**: Admin vê confirmações em tempo real
✅ **Continuidade**: Decisões anteriores como ponto de partida
✅ **Autonomia**: Cada jogador vê seu próprio estado
✅ **Sincronização**: Todos veem mudanças de iteração imediatamente
