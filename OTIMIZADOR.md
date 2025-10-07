# Sistema de Otimização com PuLP

## 📊 Visão Geral

Sistema implementado para calcular e aplicar automaticamente a **solução ótima de produção** para cada empresa usando programação linear (PuLP).

## 🎯 Funcionalidades

### Para o Professor (Admin)

1. **Calcular Solução Ótima** 📊
   - Botão `🧮` (Calcular) na tabela de empresas
   - Mostra a produção ótima em modal
   - Exibe lucro esperado e recursos utilizados

2. **Aplicar Solução Ótima** ⚡
   - Botão `⚡ Ótimo` na tabela de empresas
   - Aplica automaticamente a melhor decisão
   - Empresa fica pronta para processar turno

## 🔧 Modelo Matemático

### Função Objetivo
```
Maximizar: Lucro = Receita - Custos

Receita = Σ (quantidade_i × preço_venda_i)

Custos = Σ (quantidade_i × consumo_materia_i × custo_materia) +
         Σ (quantidade_i × consumo_energia_i × custo_energia) +
         Σ (quantidade_i × consumo_trabalhadores_i × custo_trabalho)
```

### Restrições
1. **Matéria-prima**: Σ (qtd_i × consumo_materia_i) ≤ materia_disponivel
2. **Energia**: Σ (qtd_i × consumo_energia_i) ≤ energia_disponivel
3. **Trabalhadores**: Σ (qtd_i × consumo_trabalhadores_i) ≤ trabalhadores_disponiveis
4. **Dinheiro**: Custos_totais ≤ dinheiro_disponivel
5. **Não-negatividade**: quantidade_i ≥ 0 e inteiro

## 📈 Recursos e Produtos Balanceados

### Recursos Base (por iteração)
- 💰 Dinheiro: R$ 50.000
- 📦 Matéria-prima: 20.000 unidades
- ⚡ Energia: 15.000 kWh
- 👥 Trabalhadores: 600 horas

### Custos Unitários
- Matéria-prima: R$ 1,20/unidade
- Energia: R$ 0,65/kWh
- Trabalho: R$ 22,00/hora

### Produtos (Balanceados para Produção Mista)

| Produto | Matéria | Energia | Trabalho | Preço | Característica |
|---------|---------|---------|----------|-------|----------------|
| 📱 Smartphone | 12 | 7 | 0,5h | R$ 95 | Médio trabalho |
| 💻 Laptop | 30 | 15 | 0,8h | R$ 165 | Alto em matéria |
| 🖥️ Desktop | 45 | 22 | 1,2h | R$ 220 | Alto em tudo |
| ⌚ Smartwatch | 8 | 4 | 0,35h | R$ 58 | Baixo consumo |
| 🖨️ Impressora | 25 | 18 | 0,6h | R$ 135 | Alto em energia |
| 📷 Câmera | 18 | 9 | 0,7h | R$ 110 | Equilibrado |

## 🎓 Uso Pedagógico

### Cenários de Uso

1. **Demonstração da Solução Ótima**
   - Professor mostra qual seria a melhor decisão possível
   - Estudantes comparam com suas decisões

2. **Análise de Trade-offs**
   - Cada produto tem gargalos diferentes
   - Solução ótima geralmente envolve MIX de produtos
   - Nenhum produto domina todos os outros

3. **Estudo de Caso**
   - Aplicar ótimo para uma empresa
   - Outras empresas competem normalmente
   - Comparar desempenhos

## 💻 Arquivos Criados/Modificados

### Novos Arquivos
- `src/web_app/optimizer.py` - Classe ProductionOptimizer com PuLP

### Modificados
- `src/web_app/game_state.py` - Métodos calcular_solucao_otima() e aplicar_solucao_otima()
- `src/web_app/routes.py` - Rotas /api/otimizar e /api/aplicar-otimizacao
- `src/web_app/templates/admin/dashboard.html` - Botões e modal de otimização
- `src/config/constants.py` - Recursos e produtos balanceados
- `pyproject.toml` - Dependência pulp ^2.8.0

## 🚀 Como Usar

### 1. Instalar Dependências
```bash
poetry install
```

### 2. No Dashboard Admin

#### Calcular Ótimo (🧮):
1. Clique no botão 🧮 ao lado da empresa
2. Modal mostra:
   - Produção recomendada
   - Lucro esperado
   - Recursos utilizados/restantes

#### Aplicar Ótimo (⚡):
1. Clique no botão ⚡ Ótimo
2. Confirme a ação
3. Decisão é aplicada automaticamente
4. Modal mostra detalhes da solução aplicada

### 3. Processar Turno
- Após aplicar, basta processar o turno normalmente
- Empresa terá o melhor resultado possível

## ⚠️ Observações

- **Solução Ótima** é calculada com os recursos ATUAIS da empresa
- Se empresa já usou recursos, a solução será diferente
- Cada iteração reseta recursos ao valor base
- PuLP usa solver CBC (incluído na biblioteca)

## 🎯 Resultados Esperados

Com os valores atuais, a solução ótima deve resultar em:
- **Mix de 3-4 produtos diferentes**
- Aproveitamento de ~95% dos recursos disponíveis
- Lucro entre R$ 15.000 - R$ 25.000 por turno

## 🔍 Troubleshooting

### Erro "PuLP não instalado"
```bash
poetry add pulp
```

### Solução retorna apenas 1 produto
- Ajustar valores em `src/config/constants.py`
- Aumentar/diminuir preços de venda
- Modificar consumos de recursos

### Solução não é viável
- Verificar se recursos são suficientes
- Custos podem estar muito altos
- Preços de venda podem estar muito baixos
