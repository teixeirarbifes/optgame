# 🔧 FIX CRÍTICO: Iterações Independentes

## Data: 06/10/2025

---

## 🐛 PROBLEMA

Recursos estavam sendo **consumidos acumulativamente**, diminuindo a cada turno.

**ERRADO:**
```
Turno 1: 25.000 → 11.796 (consumiu 13.204)
Turno 2: 11.796 → 0 (tentou consumir mais)
```

---

## ✅ SOLUÇÃO

Cada iteração é **independente**, sempre parte dos recursos BASE.

**CORRETO:**
```
Turno 1: Base 25.000 → Consumiu 13.204
Turno 2: Base 25.000 → Consumiu 15.000
Turno 3: Base 25.000 → Consumiu 8.500
```

---

## 🔨 IMPLEMENTAÇÃO

### Backend (`game_state.py`)
```python
# Adicionado recursos_base (fixo)
'recursos_base': GameConfig.RECURSOS_BASE.copy()

# Em abrir_proxima_iteracao()
empresa['recursos_disponiveis'] = empresa['recursos_base'].copy()
```

### Frontend (dashboard.html)
```html
<!-- Mostra capacidade fixa -->
{{ empresa.recursos_base.materia_prima }}

<!-- Mostra uso da última tentativa -->
Uso: 13.204 (53%)
```

---

## 📊 CARDS ATUALIZADOS

**Formato:**
```
💰 Dinheiro: R$ 50.000 (capacidade)
Uso: R$ 32.450 | Lucro: R$ 8.750

📦 Matéria-Prima: 25.000 (capacidade)
Uso: 13.204 (53%)
```

---

## ✅ STATUS

**IMPLEMENTADO!** Recursos resetam a cada iteração.

Reinicie o servidor! 🚀
