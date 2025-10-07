# Guia Rápido de Teste - Sistema GAP%

## Como Testar o Sistema de GAP%

### 1. Iniciar o Servidor

```powershell
cd c:\projetos\optgame
python web_server.py
```

Acesse: http://localhost:5000

### 2. Login Admin

- URL: http://localhost:5000/admin/login
- Senha: `admin123`

### 3. Criar Empresa de Teste

1. No dashboard, clique em **"+ Cadastrar Empresa"**
2. Preencha:
   - Nome: `Empresa Teste`
   - Equipe: `Time A`
   - Senha: `123`
3. Clique **"Cadastrar"**
4. Empresa será criada SEM calcular ótimo (flag padrão: False)

### 4. Testar Cálculo de GAP Individual

#### 4.1 Calcular GAP sem Mostrar Solução

1. Na tabela de empresas, localize `Empresa Teste`
2. Clique no botão **% (primeiro botão azul)**
3. ✅ Deve aparecer toast: `GAP%: X.X% (Ótimo: R$ Y.YY)`
4. ✅ Coluna GAP% deve mostrar badge colorido
5. ✅ Abaixo do lucro deve aparecer: `Ótimo: R$ Y.YY`

#### 4.2 Calcular e Mostrar Solução

1. Clique no botão **🧮 (segundo botão verde)**
2. ✅ Modal deve abrir mostrando a solução ótima detalhada
3. ✅ GAP% também é atualizado

#### 4.3 Aplicar Solução Ótima

1. Clique no botão **⚡ (terceiro botão verde)**
2. Confirme na mensagem
3. ✅ Decisão da empresa é substituída pela solução ótima
4. ✅ Badge de status muda para "Confirmada"
5. ✅ GAP% deve ficar em 0% (ou próximo)

### 5. Testar Botões Globais

#### 5.1 Calcular Todas as Empresas

1. Crie pelo menos 2-3 empresas
2. Na seção "Controles do Jogo", clique **"% Calcular Todas"**
3. Confirme
4. ✅ Toast mostra: `Cálculo concluído: N empresas processadas`
5. ✅ Todas as empresas devem ter GAP% calculado

#### 5.2 Aplicar Ótimo em Todas

1. Clique no botão **"⚡ Aplicar Ótimo em Todas"**
2. Leia o aviso e confirme
3. ✅ Toast mostra: `Solução ótima aplicada em N empresas (GAP 0%)`
4. ✅ Todas as empresas devem ter GAP% = 0% (ou próximo)
5. ✅ Todas devem estar com status "Confirmada"

### 6. Testar Flag Auto-Cálculo ao Criar

#### Via API (usando PowerShell ou terminal):

```powershell
# Ativar
curl -X POST http://localhost:5000/admin/api/toggle-calcular-otimo-ao-criar `
  -H "Content-Type: application/json" `
  -d '{"enabled": true}' `
  -b "session=<sua_sessao>"

# Verificar status
curl http://localhost:5000/admin/api/status-calcular-otimo-ao-criar `
  -b "session=<sua_sessao>"
```

**Ou via JavaScript no Console do navegador:**

```javascript
// Ativar
fetch('/admin/api/toggle-calcular-otimo-ao-criar', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content
    },
    body: JSON.stringify({enabled: true})
}).then(r => r.json()).then(console.log);

// Criar empresa para testar
// ... criar empresa normalmente ...

// Verificar se GAP% já foi calculado automaticamente
```

### 7. Cenário Completo de Teste

```
1. Login admin
2. Criar 3 empresas (A, B, C)
3. Processar turno (lucros serão 0, empresas não enviaram decisões)
4. Abrir nova iteração
5. Clicar "Calcular Todas" → Todas ficam com GAP%
6. Para empresa A: clicar "Calcular e Mostrar" → Ver solução no modal
7. Para empresa B: clicar "Aplicar Ótimo" → GAP = 0%
8. Para empresa C: deixar sem ação → GAP alto
9. Processar turno
10. Verificar ranking:
    - Empresa B deve ter melhor lucro (GAP 0%)
    - Empresas A e C devem ter lucro menor
11. Clicar "Aplicar Ótimo em Todas"
12. Processar turno
13. Todas devem ter lucro máximo possível
```

### 8. Verificações Visuais

✅ **Badge GAP%:**
- Verde (≤5%): Excelente
- Amarelo (≤20%): Bom
- Vermelho (>20%): Pode melhorar

✅ **Informações na linha da empresa:**
```
Empresa Teste
Última: R$ 9500.00
Acum: R$ 28500.00
Ótimo: R$ 10000.00
```

✅ **Coluna GAP% deve mostrar:**
```
[5.0%]  ← Badge verde
```

### 9. Testar Backward Compatibility

1. Se tiver saves antigos, carregue um
2. ✅ Empresas devem ter campos novos adicionados automaticamente
3. ✅ Não deve dar erro
4. ✅ GAP% deve aparecer como "-" (não calculado)
5. Clicar "Calcular Todas" para preencher

### 10. Testar com Múltiplas Iterações

```
Iteração 1:
  - Criar empresas
  - Calcular ótimo todas
  - Aplicar ótimo em todas
  - Processar turno
  - ✅ Lucros devem ser máximos

Iteração 2:
  - Empresas decidem manualmente (subótimo)
  - Processar turno
  - Calcular GAP
  - ✅ GAP% deve ser > 0
  
Iteração 3:
  - Aplicar ótimo em todas
  - Processar turno
  - ✅ GAP% volta para 0
```

## Endpoints para Teste Manual

### Calcular GAP sem mostrar:
```bash
POST /admin/api/calcular-otimo-sem-mostrar/EmpresaTeste
```

### Calcular todas:
```bash
POST /admin/api/calcular-otimo-todas
```

### Aplicar em todas:
```bash
POST /admin/api/aplicar-otimo-todas
```

### Toggle flag auto-cálculo:
```bash
POST /admin/api/toggle-calcular-otimo-ao-criar
Body: {"enabled": true}
```

### Status flag:
```bash
GET /admin/api/status-calcular-otimo-ao-criar
```

## Problemas Comuns e Soluções

### GAP% não aparece
- **Causa**: Solução ótima não foi calculada
- **Solução**: Clicar botão "%" ou "Calcular Todas"

### GAP% = 0% mas lucro baixo
- **Causa**: Empresa não processou turno ainda
- **Solução**: Processar turno para ver lucro real

### Botão "Aplicar Ótimo" não funciona
- **Causa**: Iteração fechada
- **Solução**: Abrir nova iteração

### Badge GAP% não atualiza
- **Causa**: Navegador cacheou página
- **Solução**: Clicar "Atualizar Dashboard" ou F5

## Sucesso do Teste

✅ Todos os botões funcionam
✅ GAP% é calculado e exibido corretamente
✅ Cores do badge mudam conforme GAP%
✅ "Calcular Todas" processa todas empresas
✅ "Aplicar em Todas" define GAP = 0%
✅ Solução ótima não é exposta desnecessariamente
✅ Flag auto-cálculo funciona ao criar empresa
✅ Saves antigos carregam sem erro

## Log Esperado no Console

```
[OTIMO] Empresa Teste: Lucro ótimo = R$ 10000.00, GAP = 5.0%
[OTIMO] Empresa A: Lucro ótimo = R$ 10000.00, GAP = 15.5%
[OTIMO] Empresa B: Lucro ótimo = R$ 10000.00, GAP = 0.0%
```
