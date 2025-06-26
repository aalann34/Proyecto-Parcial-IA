"""
enemy_behaviors.py - Comportamientos específicos para cada tipo de enemigo
Autor: Alan Alberto Martinez Ubiera - 23-EISN-2-062
"""

import random
import time
import math
from .behavior_tree import (
    BehaviorTree, BehaviorState, Selector, Sequence, 
    Action, Condition, Inverter, Timer
)

class EnemyBehavior:
    """Clase base para comportamientos de enemigos"""
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        self.enemy = enemy_data
        self.pathfinder = pathfinder
        self.get_player_pos = player_pos_getter
        self.all_enemies = all_enemies or []
        self.behavior_tree = None
        self.last_update = time.time()
        self.state_memory = {}
        
    def update(self):
        """Actualiza el comportamiento del enemigo"""
        if self.behavior_tree:
            # Actualizar datos en la pizarra
            self._update_blackboard()
            return self.behavior_tree.execute()
        return BehaviorState.FAILURE
        
    def _update_blackboard(self):
        """Actualiza la información compartida del árbol"""
        player_pos = self.get_player_pos()
        enemy_pos = self.enemy["pos"]
        
        blackboard = self.behavior_tree.blackboard
        blackboard["enemy_pos"] = enemy_pos
        blackboard["player_pos"] = player_pos
        blackboard["enemy_type"] = self.enemy["type"]
        blackboard["all_enemies"] = self.all_enemies
        blackboard["pathfinder"] = self.pathfinder
        blackboard["state_memory"] = self.state_memory
        blackboard["current_time"] = time.time()
        
        # Calcular distancia al jugador
        distance = math.sqrt((enemy_pos[0] - player_pos[0])**2 + (enemy_pos[1] - player_pos[1])**2)
        blackboard["distance_to_player"] = distance
        
    def _move_toward_player(self, blackboard):
        """Mueve al enemigo hacia el jugador usando A*"""
        try:
            enemy_pos = blackboard["enemy_pos"]
            player_pos = blackboard["player_pos"]
            
            dx, dy = self.pathfinder.get_next_move(
                enemy_pos[0], enemy_pos[1],
                player_pos[0], player_pos[1]
            )
            
            new_x = enemy_pos[0] + dx
            new_y = enemy_pos[1] + dy
            
            if self.pathfinder.is_valid_position(new_x, new_y):
                self.enemy["pos"] = [new_x, new_y]
                self.enemy["dir"] = [dx, dy]
                return True
            return False
        except:
            return False
            
    def _move_away_from_player(self, blackboard):
        """Mueve al enemigo alejándose del jugador"""
        try:
            enemy_pos = blackboard["enemy_pos"]
            player_pos = blackboard["player_pos"]
            
            # Calcular dirección opuesta al jugador
            dx = enemy_pos[0] - player_pos[0]
            dy = enemy_pos[1] - player_pos[1]
            
            # Normalizar direcciones
            if dx != 0:
                dx = 1 if dx > 0 else -1
            if dy != 0:
                dy = 1 if dy > 0 else -1
                
            new_x = enemy_pos[0] + dx
            new_y = enemy_pos[1] + dy
            
            if self.pathfinder.is_valid_position(new_x, new_y):
                self.enemy["pos"] = [new_x, new_y]
                self.enemy["dir"] = [dx, dy]
                return True
            return False
        except:
            return False

class GhostBehavior(EnemyBehavior):
    """
    Comportamiento del Fantasma (👻)
    Tipo: Agresivo - Persigue siempre al jugador
    """
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        super().__init__(enemy_data, pathfinder, player_pos_getter, all_enemies)
        self._create_behavior_tree()
        
    def _create_behavior_tree(self):
        """Crea el árbol de comportamiento para el fantasma"""
        
        # Secuencia principal: Detectar -> Perseguir
        root_sequence = Sequence("GhostMainSequence")
        
        # Condición: ¿Puede moverse hacia el jugador?
        can_chase = Condition(self._can_chase_player, "CanChasePlayer")
        
        # Acción: Perseguir al jugador
        chase_action = Action(self._chase_player, "ChasePlayer")
        
        # Armar la secuencia
        root_sequence.add_child(can_chase)
        root_sequence.add_child(chase_action)
        
        self.behavior_tree = BehaviorTree(root_sequence, "GhostBehavior")
        
    def _can_chase_player(self, blackboard):
        """Verifica si puede perseguir al jugador"""
        return blackboard["distance_to_player"] > 0.5  # Siempre persigue si no está encima
        
    def _chase_player(self, blackboard):
        """Persigue al jugador agresivamente"""
        return self._move_toward_player(blackboard)

class AlienBehavior(EnemyBehavior):
    """
    Comportamiento del Alien (👽)
    Tipo: Estratégico - Patrulla -> Detecta -> Persigue -> Huye si está muy cerca
    """
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        super().__init__(enemy_data, pathfinder, player_pos_getter, all_enemies)
        self.patrol_points = [[5, 5], [10, 8], [8, 3]]
        self.current_patrol_target = 0
        self._create_behavior_tree()
        
    def _create_behavior_tree(self):
        """Crea el árbol de comportamiento para el alien"""
        
        # Selector principal
        root_selector = Selector("AlienMainSelector")
        
        # Secuencia de huida (si está muy cerca)
        flee_sequence = Sequence("FleeSequence")
        flee_sequence.add_child(Condition(self._too_close_to_player, "TooCloseCheck"))
        flee_sequence.add_child(Action(self._flee_from_player, "FleeAction"))
        
        # Secuencia de persecución (si detecta al jugador a distancia media)
        chase_sequence = Sequence("ChaseSequence")
        chase_sequence.add_child(Condition(self._player_detected, "PlayerDetected"))
        chase_sequence.add_child(Action(self._chase_player, "ChasePlayer"))
        
        # Acción de patrulla (comportamiento por defecto)
        patrol_action = Action(self._patrol, "PatrolAction")
        
        # Ensamblar el árbol
        root_selector.add_child(flee_sequence)
        root_selector.add_child(chase_sequence)
        root_selector.add_child(patrol_action)
        
        self.behavior_tree = BehaviorTree(root_selector, "AlienBehavior")
        
    def _too_close_to_player(self, blackboard):
        """Verifica si está demasiado cerca del jugador"""
        return blackboard["distance_to_player"] <= 2.0
        
    def _player_detected(self, blackboard):
        """Detecta si el jugador está en rango medio"""
        distance = blackboard["distance_to_player"]
        return 2.0 < distance <= 6.0
        
    def _flee_from_player(self, blackboard):
        """Huye del jugador"""
        return self._move_away_from_player(blackboard)
        
    def _chase_player(self, blackboard):
        """Persigue al jugador"""
        return self._move_toward_player(blackboard)
        
    def _patrol(self, blackboard):
        """Patrulla entre puntos predefinidos"""
        try:
            enemy_pos = blackboard["enemy_pos"]
            target = self.patrol_points[self.current_patrol_target]
            
            # Si llegó al punto objetivo, cambiar al siguiente
            if abs(enemy_pos[0] - target[0]) <= 1 and abs(enemy_pos[1] - target[1]) <= 1:
                self.current_patrol_target = (self.current_patrol_target + 1) % len(self.patrol_points)
                target = self.patrol_points[self.current_patrol_target]
            
            # Moverse hacia el punto de patrulla
            dx, dy = self.pathfinder.get_next_move(
                enemy_pos[0], enemy_pos[1],
                target[0], target[1]
            )
            
            new_x = enemy_pos[0] + dx
            new_y = enemy_pos[1] + dy
            
            if self.pathfinder.is_valid_position(new_x, new_y):
                self.enemy["pos"] = [new_x, new_y]
                self.enemy["dir"] = [dx, dy]
                return True
            return False
        except:
            return False

class ZombieBehavior(EnemyBehavior):
    """
    Comportamiento del Zombie (🧟)
    Tipo: Lento - Dormido -> Despierta si el jugador está cerca -> Persigue lentamente
    """
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        super().__init__(enemy_data, pathfinder, player_pos_getter, all_enemies)
        self.is_awake = False
        self.last_move_time = 0
        self.move_delay = 0.5  # Medio segundo entre movimientos
        self._create_behavior_tree()
        
    def _create_behavior_tree(self):
        """Crea el árbol de comportamiento para el zombie"""
        
        # Selector principal
        root_selector = Selector("ZombieMainSelector")
        
        # Secuencia de despertar
        wake_sequence = Sequence("WakeSequence")
        wake_sequence.add_child(Inverter(Condition(self._is_awake, "IsAwake"), "NotAwake"))
        wake_sequence.add_child(Condition(self._player_nearby, "PlayerNearby"))
        wake_sequence.add_child(Action(self._wake_up, "WakeUp"))
        
        # Secuencia de persecución lenta
        slow_chase_sequence = Sequence("SlowChaseSequence")
        slow_chase_sequence.add_child(Condition(self._is_awake, "IsAwake"))
        slow_chase_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        slow_chase_sequence.add_child(Action(self._slow_chase, "SlowChase"))
        
        # Acción de dormir (por defecto)
        sleep_action = Action(self._sleep, "Sleep")
        
        # Ensamblar el árbol
        root_selector.add_child(wake_sequence)
        root_selector.add_child(slow_chase_sequence)
        root_selector.add_child(sleep_action)
        
        self.behavior_tree = BehaviorTree(root_selector, "ZombieBehavior")
        
    def _is_awake(self, blackboard):
        """Verifica si el zombie está despierto"""
        return self.is_awake
        
    def _player_nearby(self, blackboard):
        """Verifica si el jugador está cerca para despertar"""
        return blackboard["distance_to_player"] <= 4.0
        
    def _wake_up(self, blackboard):
        """Despierta al zombie"""
        self.is_awake = True
        return True
        
    def _can_move_now(self, blackboard):
        """Verifica si puede moverse (zombie lento)"""
        current_time = blackboard["current_time"]
        return current_time - self.last_move_time >= self.move_delay
        
    def _slow_chase(self, blackboard):
        """Persigue lentamente al jugador"""
        self.last_move_time = blackboard["current_time"]
        return self._move_toward_player(blackboard)
        
    def _sleep(self, blackboard):
        """El zombie duerme"""
        return True

class VillainBehavior(EnemyBehavior):
    """
    Comportamiento del Villano (🦹)
    Tipo: Cooperativo - Coordina ataques con otros enemigos
    """
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        super().__init__(enemy_data, pathfinder, player_pos_getter, all_enemies)
        self._create_behavior_tree()
        
    def _create_behavior_tree(self):
        """Crea el árbol de comportamiento para el villano"""
        
        # Selector principal
        root_selector = Selector("VillainMainSelector")
        
        # Secuencia de ataque coordinado
        coordinated_attack = Sequence("CoordinatedAttack")
        coordinated_attack.add_child(Condition(self._allies_nearby, "AlliesNearby"))
        coordinated_attack.add_child(Action(self._coordinate_attack, "CoordinateAttack"))
        
        # Secuencia de flanqueo
        flank_sequence = Sequence("FlankSequence")
        flank_sequence.add_child(Condition(self._can_flank, "CanFlank"))
        flank_sequence.add_child(Action(self._flank_player, "FlankPlayer"))
        
        # Persecución normal como respaldo
        normal_chase = Action(self._chase_player, "NormalChase")
        
        # Ensamblar el árbol
        root_selector.add_child(coordinated_attack)
        root_selector.add_child(flank_sequence)
        root_selector.add_child(normal_chase)
        
        self.behavior_tree = BehaviorTree(root_selector, "VillainBehavior")
        
    def _allies_nearby(self, blackboard):
        """Verifica si hay aliados cerca para coordinación"""
        enemy_pos = blackboard["enemy_pos"]
        all_enemies = blackboard["all_enemies"]
        
        nearby_allies = 0
        for other_enemy in all_enemies:
            if other_enemy != self.enemy:
                other_pos = other_enemy["pos"]
                distance = math.sqrt((enemy_pos[0] - other_pos[0])**2 + (enemy_pos[1] - other_pos[1])**2)
                if distance <= 3.0:
                    nearby_allies += 1
                    
        return nearby_allies >= 1
        
    def _coordinate_attack(self, blackboard):
        """Coordina ataque con otros enemigos"""
        # Estrategia: moverse para cercar al jugador
        player_pos = blackboard["player_pos"]
        enemy_pos = blackboard["enemy_pos"]
        
        # Calcular posición de flanqueo
        offset_positions = [
            [player_pos[0] + 1, player_pos[1]],    # Derecha
            [player_pos[0] - 1, player_pos[1]],    # Izquierda
            [player_pos[0], player_pos[1] + 1],    # Abajo
            [player_pos[0], player_pos[1] - 1]     # Arriba
        ]
        
        # Elegir la posición más cercana al enemigo
        best_pos = min(offset_positions, key=lambda pos: 
                      math.sqrt((enemy_pos[0] - pos[0])**2 + (enemy_pos[1] - pos[1])**2))
        
        # Moverse hacia esa posición
        dx, dy = self.pathfinder.get_next_move(
            enemy_pos[0], enemy_pos[1],
            best_pos[0], best_pos[1]
        )
        
        new_x = enemy_pos[0] + dx
        new_y = enemy_pos[1] + dy
        
        if self.pathfinder.is_valid_position(new_x, new_y):
            self.enemy["pos"] = [new_x, new_y]
            self.enemy["dir"] = [dx, dy]
            return True
        return False
        
    def _can_flank(self, blackboard):
        """Verifica si puede flanquear al jugador"""
        return blackboard["distance_to_player"] <= 5.0
        
    def _flank_player(self, blackboard):
        """Intenta flanquear al jugador"""
        player_pos = blackboard["player_pos"]
        enemy_pos = blackboard["enemy_pos"]
        
        # Intentar moverse a una posición lateral al jugador
        flank_positions = [
            [player_pos[0] + 2, player_pos[1] + 1],
            [player_pos[0] - 2, player_pos[1] + 1],
            [player_pos[0] + 1, player_pos[1] + 2],
            [player_pos[0] - 1, player_pos[1] - 2]
        ]
        
        # Filtrar posiciones válidas
        valid_positions = [pos for pos in flank_positions 
                          if self.pathfinder.is_valid_position(pos[0], pos[1])]
        
        if valid_positions:
            target = random.choice(valid_positions)
            dx, dy = self.pathfinder.get_next_move(
                enemy_pos[0], enemy_pos[1],
                target[0], target[1]
            )
            
            new_x = enemy_pos[0] + dx
            new_y = enemy_pos[1] + dy
            
            if self.pathfinder.is_valid_position(new_x, new_y):
                self.enemy["pos"] = [new_x, new_y]
                self.enemy["dir"] = [dx, dy]
                return True
        
        return False
        
    def _chase_player(self, blackboard):
        """Persigue al jugador normalmente"""
        return self._move_toward_player(blackboard)

def create_enemy_behavior(enemy_data, pathfinder, player_pos_getter, all_enemies=None):
    """
    Factory function para crear el comportamiento apropiado según el tipo de enemigo
    
    Args:
        enemy_data: Diccionario con datos del enemigo
        pathfinder: Instancia de AStar para navegación
        player_pos_getter: Función que retorna la posición del jugador
        all_enemies: Lista de todos los enemigos (para comportamientos cooperativos)
    
    Returns:
        EnemyBehavior: Instancia del comportamiento apropiado
    """
    enemy_type = enemy_data.get("type", "👻")
    
    if enemy_type == "👻":  # Fantasma
        return GhostBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    elif enemy_type == "👽":  # Alien
        return AlienBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    elif enemy_type == "🧟":  # Zombie
        return ZombieBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    elif enemy_type == "🦹":  # Villano
        return VillainBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    else:
        # Comportamiento por defecto (Fantasma)
        return GhostBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)