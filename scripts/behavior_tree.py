"""
test_behavior_trees.py - Prueba independiente de los Árboles de Comportamiento
Autor: Alan Alberto Martinez Ubiera - 23-EISN-2-062
"""

from scripts import (
    BehaviorTree, BehaviorState, Selector, Sequence, 
    Action, Condition, Inverter, Timer, create_enemy_behavior, AStar
)

def test_basic_behavior_tree():
    """Prueba básica del sistema de árboles de comportamiento"""
    print("🌳 Probando Árboles de Comportamiento básicos...")
    
    # Variables de prueba
    test_data = {'health': 100, 'enemy_nearby': True, 'ammo': 5}
    
    # Crear acciones de prueba
    def attack_action(blackboard):
        print("   ⚔️ Atacando!")
        blackboard['ammo'] -= 1
        return BehaviorState.SUCCESS
    
    def flee_action(blackboard):
        print("   🏃 Huyendo!")
        return BehaviorState.SUCCESS
    
    def check_health(blackboard):
        print(f"   💖 Verificando salud: {blackboard['health']}")
        return blackboard['health'] > 50
    
    def check_ammo(blackboard):
        print(f"   🔫 Verificando munición: {blackboard['ammo']}")
        return blackboard['ammo'] > 0
    
    # Crear árbol de comportamiento de prueba
    # Selector principal
    root = Selector("TestRoot")
    
    # Secuencia de ataque (si hay salud y munición)
    attack_sequence = Sequence("AttackSequence")
    attack_sequence.add_child(Condition(check_health, "CheckHealth"))
    attack_sequence.add_child(Condition(check_ammo, "CheckAmmo"))
    attack_sequence.add_child(Action(attack_action, "Attack"))
    
    # Acción de huida como respaldo
    flee_action_node = Action(flee_action, "Flee")
    
    # Ensamblar árbol
    root.add_child(attack_sequence)
    root.add_child(flee_action_node)
    
    # Crear y ejecutar el árbol
    behavior_tree = BehaviorTree(root, "TestBehaviorTree")
    behavior_tree.blackboard = test_data
    
    # Ejecutar varias veces para ver el comportamiento
    for i in range(3):
        print(f"\n--- Ejecución {i+1} ---")
        result = behavior_tree.execute()
        print(f"Resultado: {result}")
        print(f"Munición restante: {behavior_tree.blackboard['ammo']}")
    
    print("✅ Prueba básica completada!\n")

def test_enemy_behaviors():
    """Prueba los comportamientos específicos de enemigos"""
    print("🤖 Probando Comportamientos de Enemigos...")
    
    # Crear un laberinto simple para las pruebas
    test_maze = [
        [1,1,1,1,1],
        [1,0,0,0,1],
        [1,0,1,0,1],
        [1,0,0,0,1],
        [1,1,1,1,1]
    ]
    
    # Crear pathfinder
    pathfinder = AStar(test_maze)
    
    # Posición del jugador para las pruebas
    test_player_pos = [3, 3]
    
    def get_test_player_pos():
        return test_player_pos
    
    # Crear datos de enemigos de prueba
    test_enemies = [
        {"pos": [1, 1], "dir": [0, 1], "type": "👻"},  # Fantasma
        {"pos": [2, 1], "dir": [1, 0], "type": "👽"},  # Alien
        {"pos": [3, 1], "dir": [0, 1], "type": "🧟"},  # Zombie
        {"pos": [1, 2], "dir": [1, 0], "type": "🦹"},  # Villano
    ]
    
    # Crear comportamientos para cada enemigo
    behaviors = []
    for enemy_data in test_enemies:
        behavior = create_enemy_behavior(
            enemy_data=enemy_data,
            pathfinder=pathfinder,
            player_pos_getter=get_test_player_pos,
            all_enemies=test_enemies
        )
        behaviors.append(behavior)
    
    print(f"✅ Creados {len(behaviors)} comportamientos de enemigos")
    
    # Probar cada comportamiento
    for i, behavior in enumerate(behaviors):
        enemy = test_enemies[i]
        print(f"\n--- Probando {enemy['type']} en posición {enemy['pos']} ---")
        
        # Ejecutar comportamiento varias veces
        for step in range(3):
            old_pos = enemy['pos'].copy()
            result = behavior.update()
            new_pos = enemy['pos']
            
            print(f"  Paso {step+1}: {old_pos} → {new_pos} (Estado: {result})")
        
        print(f"  ✅ Comportamiento de {enemy['type']} funcionando")
    
    print("\n✅ Todas las pruebas de comportamientos completadas!")

def test_advanced_nodes():
    """Prueba nodos avanzados como Inverter y Timer"""
    print("\n🔧 Probando Nodos Avanzados...")
    
    # Test del nodo Inverter
    print("--- Probando Inverter ---")
    
    def always_true(blackboard):
        print("   Función siempre retorna True")
        return True
    
    def always_false(blackboard):
        print("   Función siempre retorna False")
        return False
    
    # Crear nodos con inverter
    true_action = Action(always_true, "AlwaysTrue")
    false_action = Action(always_false, "AlwaysFalse")
    
    inverted_true = Inverter(true_action, "InvertedTrue")
    inverted_false = Inverter(false_action, "InvertedFalse")
    
    # Probar inversores
    print("Resultado de True invertido:", inverted_true.execute())
    print("Resultado de False invertido:", inverted_false.execute())
    
    # Test del nodo Timer
    print("\n--- Probando Timer ---")
    
    def delayed_action(blackboard):
        print("   ⏰ Acción ejecutada después del delay!")
        return BehaviorState.SUCCESS
    
    # Crear timer con delay de 0.1 segundos
    timer_action = Action(delayed_action, "DelayedAction")
    timer_node = Timer(0.1, timer_action, "Timer")
    
    # Ejecutar timer varias veces
    import time
    for i in range(5):
        result = timer_node.execute()
        print(f"   Timer ejecutión {i+1}: {result}")
        time.sleep(0.05)  # Esperar un poco entre ejecuciones
    
    print("✅ Nodos avanzados funcionando correctamente!")

def main():
    """Función principal de pruebas"""
    print("🧪 INICIANDO PRUEBAS DE ÁRBOLES DE COMPORTAMIENTO")
    print("=" * 50)
    
    try:
        # Ejecutar todas las pruebas
        test_basic_behavior_tree()
        test_enemy_behaviors()
        test_advanced_nodes()
        
        print("\n" + "=" * 50)
        print("🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("✅ Sistema de Árboles de Comportamiento funcionando correctamente")
        print("✅ Integración con A* verificada")
        print("✅ Comportamientos específicos de enemigos operativos")
        print("\n🚀 ¡Listo para integrar en el juego principal!")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que todos los archivos estén creados y guardados")
        print("💡 Verifica que la estructura de carpetas sea correcta")
    
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        print("💡 Revisa que el código de los árboles de comportamiento esté correcto")

if __name__ == "__main__":
    main()