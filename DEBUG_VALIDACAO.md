# 🔍 DEBUG - Validação de Recursos

## Para identificar o problema

Execute o seguinte teste:

1. **Resetar o jogo** (para ter recursos iniciais)
2. **Criar decisão que CLARAMENTE viola**:
   - Produzir 500 Laptops
   - Isso consome: 500 × 35 = 17.500 matéria-prima
   - Inicial: 25.000 matéria-prima
   - Deve passar ✅

3. **Criar decisão que CLARAMENTE viola na 2ª rodada**:
   - Após consumir 17.500, sobram 7.500
   - Produzir 300 Laptops
   - Isso consome: 300 × 35 = 10.500 matéria-prima
   - Disponível: 7.500
   - Deve VIOLAR ❌

4. **Verificar os logs no terminal Python**

Você vai ver:
```
=== VALIDANDO EMPRESA: TesteDaEmpresa ===
Decisão: {'💻 Laptop': 300}
Consumo calculado: {'materia_prima': 10500, 'energia': 5400, 'trabalhadores': 360, 'dinheiro': 26100}
Recursos disponíveis: {'dinheiro': X, 'materia_prima': 7500, 'energia': Y, 'trabalhadores': Z}
  materia_prima: necessário=10500, disponível=7500
    ❌ VIOLAÇÃO! Déficit: 3000
```

Se NÃO aparecer a mensagem de violação, então o bug está na validação.
Se APARECER a mensagem mas o sistema executar mesmo assim, o bug está na lógica de aplicação.

## Teste agora e me mostre o log!
