# 🧪 GUIA RÁPIDO DE TESTE - Correções 06/10/2025

## ⚡ Teste em 5 Minutos

---

## 1. INICIE O SERVIDOR

```powershell
cd c:\projetos\optgame
python web_server.py
```

Acesse: **http://localhost:5000**

---

## 2. TESTE ITERAÇÕES INDEPENDENTES

### Passo a Passo:
1. Faça login como empresa (ou crie nova)
2. **Anote os valores dos cards:**
   - 💰 Dinheiro: R$ 50.000,00
   - 📦 Matéria: 25.000
   - ⚡ Energia: 18.000
   - 👥 Trabalho: 800

3. Envie uma decisão (ex: 300 Smartphones)
4. Admin: Processe o turno
5. Admin: Abra próxima iteração
6. **VERIFIQUE:** Valores dos cards voltaram aos anotados no passo 2! ✅

---

## 3. TESTE CAPACIDADE E USO

### Nos Cards (topo da página):
```
Deve mostrar:

💰 Dinheiro
R$ 50.000,00  ← Capacidade fixa
Capacidade: R$ 50.000,00
Uso: R$ 37.800,00 | Lucro: R$ 22.200,00

📦 Matéria-Prima
25.000  ← Capacidade fixa
Capacidade: 25.000
Uso: 12.000 (48%)
```

**Verificar:**
- ✅ Valor grande = Capacidade (sempre 25.000 / 18.000 / 800)
- ✅ Info adicional mostra "Capacidade" e "Uso"
- ✅ Percentual de uso está correto

---

## 4. TESTE SEÇÃO CONSUMO

### Role até "Consumo de Recursos (Último Turno)"

```
Deve mostrar:

📦 Matéria-Prima
Uso: 12.000 / Capacidade: 25.000
Restante: 13.000
[████████████████░░░░░░░░░░░░] 48%
```

**Verificar:**
- ✅ Capacidade = 25.000 (fixa)
- ✅ Uso = consumo da iteração
- ✅ Restante = Capacidade - Uso (25.000 - 12.000 = 13.000) ✅
- ✅ Barra mostra 48% (12.000/25.000)

---

## 5. TESTE CÁLCULO MANUAL

### Faça esta conta:
1. Veja "Capacidade" na seção Consumo
2. Veja "Uso" na seção Consumo
3. Calcule: Capacidade - Uso
4. Compare com "Restante" mostrado

**Exemplo:**
```
Capacidade: 25.000
Uso: 12.000
Cálculo: 25.000 - 12.000 = 13.000
Restante mostrado: 13.000 ✅
```

Se bater, está correto! ✅

---

## ✅ CHECKLIST RÁPIDO

- [ ] Recursos voltam ao base após abrir nova iteração
- [ ] Cards mostram capacidade fixa (não muda)
- [ ] Info adicional mostra "Capacidade" e "Uso (%)"
- [ ] Seção Consumo usa "Uso / Capacidade"
- [ ] Cálculo "Restante" está correto (Capacidade - Uso)
- [ ] AJAX atualiza tudo automaticamente

---

## 🐛 SE ALGO NÃO FUNCIONA

### Problema: Valores não voltam ao base
**Solução:** Reinicie o servidor e crie uma nova empresa

### Problema: Cálculo "Restante" errado
**Solução:** Recarregue a página (Ctrl+F5)

### Problema: Cards mostram valores estranhos
**Solução:** Verifique se há histórico (precisa processar pelo menos 1 turno)

---

## 🎯 RESULTADO ESPERADO

Após os testes, você deve ver:

✅ **Capacidade fixa** em todos os cards  
✅ **Uso e percentual** da última iteração  
✅ **Restante calculado corretamente** (Capacidade - Uso)  
✅ **Recursos voltando ao base** a cada nova iteração  
✅ **Interface clara e consistente** em todos os lugares  

---

## 📝 ANOTAÇÕES

Se encontrar algum problema, anote aqui:

**Problema 1:**
- [ ] Descreva o problema
- [ ] Passos para reproduzir
- [ ] Comportamento esperado vs. observado

**Problema 2:**
- [ ] ...

---

## ✅ STATUS

Se todos os testes passaram: **SISTEMA FUNCIONANDO PERFEITAMENTE! 🎉**

Aproveite as melhorias! 🚀
