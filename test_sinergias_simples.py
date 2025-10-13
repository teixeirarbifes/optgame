# -*- coding: utf-8 -*-
"""
Teste SIMPLES: Otimizador vs Processamento
"""
import sys
sys.path.insert(0, 'src')

# Primeiro teste: apenas imports
try:
    from web_app.optimizer import ProductionOptimizer
    print("✅ ProductionOptimizer importado")
    
    from web_app.game_state import GameState
    print("✅ GameState importado")
    
    from config.constants import GameConfig
    print("✅ GameConfig importado")
    
    print("\n" + "="*80)
    print("TESTE: SINERGIAS NO PROCESSAMENTO")
    print("="*80)
    
    # Criar estado
    game = GameState()
    game.reset_game()
    game.adicionar_empresa("TesteCorp", "Time1", "senha123")
    
    # Decisão com sinergia: Smartphone + Smartwatch
    decisao = {
        'Smartphone': 244.44,
        'Smartwatch': 244.44,
        'Impressora': 400.93,
        'Camera': 216.67
    }
    
    # Calcular bônus
    bonus = game._calcular_bonus_sinergias(decisao, GameConfig.PRODUTOS)
    print(f"\n💰 Bônus de Sinergias Calculado: R$ {bonus:,.2f}")
    
    # Calcular lucro base (sem sinergia)
    from mecanicas.mechanics import GameMechanics
    metricas = GameMechanics.calcular_metricas_plano(GameConfig.PRODUTOS, decisao)
    lucro_base = metricas['lucro']
    
    print(f"📊 Lucro Base (sem sinergia): R$ {lucro_base:,.2f}")
    print(f"🎯 Lucro Total (com sinergia): R$ {lucro_base + bonus:,.2f}")
    
    print("\n" + "="*80)
    print("✅ TESTE CONCLUÍDO")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
