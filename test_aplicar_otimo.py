"""
Script de teste para diagnosticar problema de aplicação de solução ótima
"""

from src.web_app.game_state import GameState
from src.config.constants import GameConfig

# Criar estado do jogo
game_state = GameState()

# Criar empresa de teste
print("=" * 60)
print("CRIANDO EMPRESA DE TESTE")
print("=" * 60)
game_state.criar_empresa("Teste Corp", "Equipe A", "senha123")

# Abrir iteração
print("\n" + "=" * 60)
print("ABRINDO ITERAÇÃO")
print("=" * 60)
game_state.abrir_iteracao()

# Tentar aplicar solução ótima
print("\n" + "=" * 60)
print("APLICANDO SOLUÇÃO ÓTIMA")
print("=" * 60)
resultado = game_state.aplicar_solucao_otima("Teste Corp")

print("\n" + "=" * 60)
print("RESULTADO FINAL")
print("=" * 60)
print(f"Sucesso: {resultado.get('sucesso')}")
print(f"Mensagem: {resultado.get('mensagem')}")

if resultado.get('sucesso'):
    print(f"\nProdução Ótima:")
    for produto, qtd in resultado.get('producao_otima', {}).items():
        print(f"  {produto}: {qtd}")
    print(f"\nLucro Esperado: R$ {resultado.get('lucro_esperado', 0):,.2f}")
    
    # Verificar estado da empresa
    empresa = game_state.empresas.get("Teste Corp")
    if empresa:
        print(f"\nDecisão confirmada: {empresa.get('decisao_confirmada')}")
        print(f"Decisão atual: {empresa.get('decisao_atual')}")
else:
    print("\n❌ FALHOU!")
    
print("\n" + "=" * 60)
