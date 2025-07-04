"""
enemy_behaviors.py - Comportamientos específicos para cada tipo de enemigo (BALANCEADO)
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

class AlienBehavior(EnemyBehavior):
    """
    Comportamiento del Alien (👽)
    Tipo: Usa A* para perseguir al jugador de forma inteligente (BALANCEADO)
    """
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        super().__init__(enemy_data, pathfinder, player_pos_getter, all_enemies)
        self.last_move_time = 0
        self.move_delay = 0.3  # Delay para no ser demasiado agresivo
        self._create_behavior_tree()
        
    def _create_behavior_tree(self):
        """Crea el árbol de comportamiento para el alien"""
        
        # Secuencia principal con control de velocidad
        root_sequence = Sequence("AlienMainSequence")
        
        # Condición: ¿Puede moverse ahora?
        can_move = Condition(self._can_move_now, "CanMoveNow")
        
        # Condición: ¿Puede perseguir al jugador?
        can_chase = Condition(self._can_chase_player, "CanChasePlayer")
        
        # Acción: Perseguir usando A*
        chase_action = Action(self._smart_chase, "SmartChase")
        
        # Armar la secuencia
        root_sequence.add_child(can_move)
        root_sequence.add_child(can_chase)
        root_sequence.add_child(chase_action)
        
        self.behavior_tree = BehaviorTree(root_sequence, "AlienBehavior")
        
    def _can_move_now(self, blackboard):
        """Controla la velocidad del alien"""
        current_time = blackboard["current_time"]
        return current_time - self.last_move_time >= self.move_delay
        
    def _can_chase_player(self, blackboard):
        """Verifica si puede perseguir al jugador"""
        return blackboard["distance_to_player"] > 0.5
        
    def _smart_chase(self, blackboard):
        """Persigue al jugador usando A* con control de velocidad"""
        self.last_move_time = blackboard["current_time"]
        return self._move_toward_player(blackboard)

class GhostBehavior(EnemyBehavior):
    """
    Comportamiento del Fantasma (👻)
    Tipo: Evade al jugador - huye cuando está cerca (BALANCEADO)
    """
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        super().__init__(enemy_data, pathfinder, player_pos_getter, all_enemies)
        self.last_move_time = 0
        self.move_delay = 0.4  # Más lento para balance
        self._create_behavior_tree()
        
    def _create_behavior_tree(self):
        """Crea el árbol de comportamiento para el fantasma"""
        
        # Selector principal con control de velocidad
        root_selector = Selector("GhostMainSelector")
        
        # Secuencia de huida (cuando el jugador está cerca)
        flee_sequence = Sequence("FleeSequence")
        flee_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        flee_sequence.add_child(Condition(self._player_nearby, "PlayerNearby"))
        flee_sequence.add_child(Action(self._flee_from_player, "FleeFromPlayer"))
        
        # Secuencia de vagar (cuando el jugador no está cerca)
        wander_sequence = Sequence("WanderSequence")
        wander_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        wander_sequence.add_child(Action(self._wander, "Wander"))
        
        # Ensamblar el árbol
        root_selector.add_child(flee_sequence)
        root_selector.add_child(wander_sequence)
        
        self.behavior_tree = BehaviorTree(root_selector, "GhostBehavior")
        
    def _can_move_now(self, blackboard):
        """Controla la velocidad del fantasma"""
        current_time = blackboard["current_time"]
        return current_time - self.last_move_time >= self.move_delay
        
    def _player_nearby(self, blackboard):
        """Verifica si el jugador está cerca"""
        return blackboard["distance_to_player"] <= 4.0  # Reducido para mejor balance
        
    def _flee_from_player(self, blackboard):
        """Huye del jugador"""
        self.last_move_time = blackboard["current_time"]
        return self._move_away_from_player(blackboard)
        
    def _wander(self, blackboard):
        """Vaga aleatoriamente cuando no hay peligro"""
        try:
            self.last_move_time = blackboard["current_time"]
            enemy_pos = blackboard["enemy_pos"]
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            dx, dy = random.choice(directions)
            
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
    Tipo: Se mueve de forma completamente aleatoria (BALANCEADO)
    """
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        super().__init__(enemy_data, pathfinder, player_pos_getter, all_enemies)
        self.last_move_time = 0
        self.move_delay = 1.0  # Zombies son muy lentos
        self._create_behavior_tree()
        
    def _create_behavior_tree(self):
        """Crea el árbol de comportamiento para el zombie"""
        
        # Secuencia principal con delay largo
        root_sequence = Sequence("ZombieMainSequence")
        
        # Condición: ¿Puede moverse ahora? (zombie muy lento)
        can_move = Condition(self._can_move_now, "CanMoveNow")
        
        # Acción: Movimiento aleatorio
        random_move = Action(self._random_move, "RandomMove")
        
        # Armar la secuencia
        root_sequence.add_child(can_move)
        root_sequence.add_child(random_move)
        
        self.behavior_tree = BehaviorTree(root_sequence, "ZombieBehavior")
        
    def _can_move_now(self, blackboard):
        """Verifica si puede moverse (zombie muy lento)"""
        current_time = blackboard["current_time"]
        return current_time - self.last_move_time >= self.move_delay
        
    def _random_move(self, blackboard):
        """Movimiento completamente aleatorio"""
        try:
            self.last_move_time = blackboard["current_time"]
            enemy_pos = blackboard["enemy_pos"]
            
            # Direcciones posibles
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            dx, dy = random.choice(directions)
            
            new_x = enemy_pos[0] + dx
            new_y = enemy_pos[1] + dy
            
            if self.pathfinder.is_valid_position(new_x, new_y):
                self.enemy["pos"] = [new_x, new_y]
                self.enemy["dir"] = [dx, dy]
                return True
            return False
        except:
            return False

class VillainBehavior(EnemyBehavior):
    """
    Comportamiento del Villano (🦹)
    Tipo: Mezcla entre persecución y emboscada (BALANCEADO)
    """
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        super().__init__(enemy_data, pathfinder, player_pos_getter, all_enemies)
        self.ambush_mode = False
        self.mode_switch_time = 0
        self.last_move_time = 0
        self.move_delay = 0.5  # Velocidad moderada
        self._create_behavior_tree()
        
    def _create_behavior_tree(self):
        """Crea el árbol de comportamiento para el villano"""
        
        # Selector principal con control de velocidad
        root_selector = Selector("VillainMainSelector")
        
        # Secuencia de emboscada
        ambush_sequence = Sequence("AmbushSequence")
        ambush_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        ambush_sequence.add_child(Condition(self._should_ambush, "ShouldAmbush"))
        ambush_sequence.add_child(Action(self._setup_ambush, "SetupAmbush"))
        
        # Secuencia de persecución directa
        chase_sequence = Sequence("ChaseSequence")
        chase_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        chase_sequence.add_child(Condition(self._should_chase, "ShouldChase"))
        chase_sequence.add_child(Action(self._chase_player, "ChasePlayer"))
        
        # Acción de patrulla por defecto
        patrol_sequence = Sequence("PatrolSequence")
        patrol_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        patrol_sequence.add_child(Action(self._patrol, "PatrolAction"))
        
        # Ensamblar el árbol
        root_selector.add_child(ambush_sequence)
        root_selector.add_child(chase_sequence)
        root_selector.add_child(patrol_sequence)
        
        self.behavior_tree = BehaviorTree(root_selector, "VillainBehavior")
        
    def _can_move_now(self, blackboard):
        """Controla la velocidad del villano"""
        current_time = blackboard["current_time"]
        return current_time - self.last_move_time >= self.move_delay
        
    def _should_ambush(self, blackboard):
        """Decide si debe hacer emboscada"""
        current_time = blackboard["current_time"]
        distance = blackboard["distance_to_player"]
        
        # Cambiar de modo cada 8 segundos (más lento)
        if current_time - self.mode_switch_time > 8.0:
            self.ambush_mode = not self.ambush_mode
            self.mode_switch_time = current_time
            
        return self.ambush_mode and distance > 2.0
        
    def _should_chase(self, blackboard):
        """Decide si debe perseguir directamente"""
        distance = blackboard["distance_to_player"]
        return not self.ambush_mode and distance <= 5.0
        
    def _setup_ambush(self, blackboard):
        """Configura una emboscada"""
        try:
            self.last_move_time = blackboard["current_time"]
            player_pos = blackboard["player_pos"]
            enemy_pos = blackboard["enemy_pos"]
            
            # Predecir donde estará el jugador (más conservador)
            predicted_positions = [
                [player_pos[0] + 2, player_pos[1]],
                [player_pos[0] - 2, player_pos[1]],
                [player_pos[0], player_pos[1] + 2],
                [player_pos[0], player_pos[1] - 2]
            ]
            
            # Elegir la posición más estratégica
            valid_positions = [pos for pos in predicted_positions 
                             if self.pathfinder.is_valid_position(pos[0], pos[1])]
            
            if valid_positions:
                target = min(valid_positions, key=lambda pos: 
                           math.sqrt((enemy_pos[0] - pos[0])**2 + (enemy_pos[1] - pos[1])**2))
                
                dx, dy = self.pathfinder.get_next_move(
                    enemy_pos[0], enemy_pos[1], target[0], target[1]
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
        
    def _chase_player(self, blackboard):
        """Persigue al jugador directamente"""
        self.last_move_time = blackboard["current_time"]
        return self._move_toward_player(blackboard)
        
    def _patrol(self, blackboard):
        """Patrulla cuando no hay objetivo claro"""
        self.last_move_time = blackboard["current_time"]
        return self._move_toward_player(blackboard)

class DemonBehavior(EnemyBehavior):
    """
    Comportamiento del Demonio (👺)
    Tipo: Se teletransporta en tramos (BALANCEADO)
    """
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        super().__init__(enemy_data, pathfinder, player_pos_getter, all_enemies)
        self.last_teleport_time = 0
        self.teleport_cooldown = 5.0  # Cooldown más largo
        self.last_move_time = 0
        self.move_delay = 0.6  # Movimiento normal más lento
        self._create_behavior_tree()
        
    def _create_behavior_tree(self):
        """Crea el árbol de comportamiento para el demonio"""
        
        # Selector principal
        root_selector = Selector("DemonMainSelector")
        
        # Secuencia de teletransporte
        teleport_sequence = Sequence("TeleportSequence")
        teleport_sequence.add_child(Condition(self._can_teleport, "CanTeleport"))
        teleport_sequence.add_child(Action(self._teleport_near_player, "TeleportNearPlayer"))
        
        # Movimiento normal como respaldo
        normal_move_sequence = Sequence("NormalMoveSequence")
        normal_move_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        normal_move_sequence.add_child(Action(self._normal_move, "NormalMove"))
        
        # Ensamblar el árbol
        root_selector.add_child(teleport_sequence)
        root_selector.add_child(normal_move_sequence)
        
        self.behavior_tree = BehaviorTree(root_selector, "DemonBehavior")
        
    def _can_move_now(self, blackboard):
        """Controla la velocidad del demonio"""
        current_time = blackboard["current_time"]
        return current_time - self.last_move_time >= self.move_delay
        
    def _can_teleport(self, blackboard):
        """Verifica si puede teletransportarse"""
        current_time = blackboard["current_time"]
        distance = blackboard["distance_to_player"]
        
        # Puede teletransportarse si ha pasado el cooldown y el jugador está lejos
        return (current_time - self.last_teleport_time >= self.teleport_cooldown and 
                distance > 6.0)  # Aumentado para mejor balance
        
    def _teleport_near_player(self, blackboard):
        """Se teletransporta cerca del jugador"""
        try:
            current_time = blackboard["current_time"]
            player_pos = blackboard["player_pos"]
            
            self.last_teleport_time = current_time
            
            # Posiciones cercanas al jugador para teletransportarse (más conservador)
            teleport_positions = []
            for radius in range(3, 5):  # Anillo más pequeño
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        if abs(dx) == radius or abs(dy) == radius:  # Solo el borde
                            new_x = player_pos[0] + dx
                            new_y = player_pos[1] + dy
                            if self.pathfinder.is_valid_position(new_x, new_y):
                                teleport_positions.append([new_x, new_y])
            
            if teleport_positions:
                new_pos = random.choice(teleport_positions)
                self.enemy["pos"] = new_pos
                self.enemy["dir"] = [0, 0]  # Sin dirección específica tras teletransporte
                return True
            return False
        except:
            return False
        
    def _normal_move(self, blackboard):
        """Movimiento normal cuando no puede teletransportarse"""
        self.last_move_time = blackboard["current_time"]
        return self._move_toward_player(blackboard)

class ClownBehavior(EnemyBehavior):
    """
    Comportamiento del Payaso (🤡)
    Tipo: Deja trampas y se mueve en patrones erráticos (BALANCEADO)
    """
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        super().__init__(enemy_data, pathfinder, player_pos_getter, all_enemies)
        self.traps = []  # Lista de trampas colocadas
        self.last_trap_time = 0
        self.trap_cooldown = 6.0  # Cooldown más largo
        self.movement_pattern = 0
        self.pattern_steps = 0
        self.last_move_time = 0
        self.move_delay = 0.5  # Velocidad moderada
        self._create_behavior_tree()
        
    def _create_behavior_tree(self):
        """Crea el árbol de comportamiento para el payaso"""
        
        # Selector principal
        root_selector = Selector("ClownMainSelector")
        
        # Secuencia de colocar trampa
        trap_sequence = Sequence("TrapSequence")
        trap_sequence.add_child(Condition(self._can_place_trap, "CanPlaceTrap"))
        trap_sequence.add_child(Action(self._place_trap, "PlaceTrap"))
        
        # Secuencia de movimiento errático
        erratic_sequence = Sequence("ErraticSequence")
        erratic_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        erratic_sequence.add_child(Action(self._erratic_movement, "ErraticMovement"))
        
        # Ensamblar el árbol
        root_selector.add_child(trap_sequence)
        root_selector.add_child(erratic_sequence)
        
        self.behavior_tree = BehaviorTree(root_selector, "ClownBehavior")
        
    def _can_move_now(self, blackboard):
        """Controla la velocidad del payaso"""
        current_time = blackboard["current_time"]
        return current_time - self.last_move_time >= self.move_delay
        
    def _can_place_trap(self, blackboard):
        """Verifica si puede colocar una trampa"""
        current_time = blackboard["current_time"]
        distance = blackboard["distance_to_player"]
        
        # Puede colocar trampa si ha pasado el cooldown y está cerca del jugador
        return (current_time - self.last_trap_time >= self.trap_cooldown and 
                3.0 <= distance <= 6.0)  # Rango más conservador
        
    def _place_trap(self, blackboard):
        """Coloca una trampa en la posición actual"""
        try:
            current_time = blackboard["current_time"]
            enemy_pos = blackboard["enemy_pos"]
            
            self.last_trap_time = current_time
            
            # Agregar trampa (nota: las trampas no están implementadas visualmente en este ejemplo)
            trap_pos = enemy_pos.copy()
            self.traps.append({
                'pos': trap_pos,
                'time': current_time
            })
            
            # Limpiar trampas viejas (después de 12 segundos)
            self.traps = [trap for trap in self.traps 
                         if current_time - trap['time'] < 12.0]
            
            return True
        except:
            return False
        
    def _erratic_movement(self, blackboard):
        """Movimiento errático en patrones"""
        try:
            self.last_move_time = blackboard["current_time"]
            enemy_pos = blackboard["enemy_pos"]
            
            # Cambiar patrón cada 7 pasos (más lento)
            if self.pattern_steps >= 7:
                self.movement_pattern = (self.movement_pattern + 1) % 4
                self.pattern_steps = 0
            
            self.pattern_steps += 1
            
            # Patrones de movimiento diferentes (más conservadores)
            if self.movement_pattern == 0:  # Zigzag horizontal
                dx = 1 if self.pattern_steps % 2 == 0 else -1
                dy = 0
            elif self.movement_pattern == 1:  # Zigzag vertical
                dx = 0
                dy = 1 if self.pattern_steps % 2 == 0 else -1
            elif self.movement_pattern == 2:  # Diagonal
                dx = 1 if self.pattern_steps % 2 == 0 else -1
                dy = 1 if self.pattern_steps % 2 == 0 else -1
            else:  # Completamente aleatorio
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                dx, dy = random.choice(directions)
            
            new_x = enemy_pos[0] + dx
            new_y = enemy_pos[1] + dy
            
            if self.pathfinder.is_valid_position(new_x, new_y):
                self.enemy["pos"] = [new_x, new_y]
                self.enemy["dir"] = [dx, dy]
                return True
            return False
        except:
            return False

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
    
    if enemy_type == "👽":  # Alien - A* inteligente balanceado
        return AlienBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    elif enemy_type == "👻":  # Fantasma - Evade al jugador balanceado
        return GhostBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    elif enemy_type == "🧟":  # Zombie - Movimiento aleatorio lento
        return ZombieBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    elif enemy_type == "🦹":  # Villano - Persecución y emboscada balanceada
        return VillainBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    elif enemy_type == "👺":  # Demonio - Teletransporte balanceado
        return DemonBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    elif enemy_type == "🤡":  # Payaso - Trampas y movimiento errático balanceado
        return ClownBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    else:
        # Comportamiento por defecto (Alien)
        return AlienBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)