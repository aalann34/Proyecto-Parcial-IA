"""
enemy_behaviors.py - Comportamientos específicos para cada tipo de enemigo (CORREGIDO)
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
    Tipo: Puede volverse INVISIBLE temporalmente y aparece en lugares inesperados
    """
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        super().__init__(enemy_data, pathfinder, player_pos_getter, all_enemies)
        self.last_move_time = 0
        self.move_delay = 0.4  # Más lento para balance
        
        # SISTEMA DE INVISIBILIDAD MEJORADO
        self.is_invisible = False
        self.invisibility_start_time = 0
        self.invisibility_duration = 2.5  # Invisible por 2.5 segundos
        self.invisibility_cooldown = 4.0  # Cooldown de 4 segundos (más frecuente)
        self.last_invisibility_time = 0
        
        print(f"👻 Fantasma inicializado - puede volverse invisible cada {self.invisibility_cooldown}s por {self.invisibility_duration}s")
        
        self._create_behavior_tree()
        
    def _create_behavior_tree(self):
        """Crea el árbol de comportamiento para el fantasma"""
        
        # Selector principal
        root_selector = Selector("GhostMainSelector")
        
        # Secuencia de invisibilidad
        invisibility_sequence = Sequence("InvisibilitySequence")
        invisibility_sequence.add_child(Condition(self._can_become_invisible, "CanBecomeInvisible"))
        invisibility_sequence.add_child(Action(self._activate_invisibility, "ActivateInvisibility"))
        
        # Secuencia de huida (cuando está visible y jugador cerca)
        flee_sequence = Sequence("FleeSequence")
        flee_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        flee_sequence.add_child(Condition(self._is_visible, "IsVisible"))
        flee_sequence.add_child(Condition(self._player_nearby, "PlayerNearby"))
        flee_sequence.add_child(Action(self._flee_from_player, "FleeFromPlayer"))
        
        # Secuencia de vagar (cuando está visible y jugador lejos)
        wander_sequence = Sequence("WanderSequence")
        wander_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        wander_sequence.add_child(Condition(self._is_visible, "IsVisible"))
        wander_sequence.add_child(Action(self._wander, "Wander"))
        
        # Ensamblar el árbol (prioridad: invisibilidad > huida > vagar)
        root_selector.add_child(invisibility_sequence)
        root_selector.add_child(flee_sequence)
        root_selector.add_child(wander_sequence)
        
        self.behavior_tree = BehaviorTree(root_selector, "GhostBehavior")
        
    def _can_move_now(self, blackboard):
        """Controla la velocidad del fantasma"""
        current_time = blackboard["current_time"]
        return current_time - self.last_move_time >= self.move_delay
        
    def _player_nearby(self, blackboard):
        """Verifica si el jugador está cerca"""
        return blackboard["distance_to_player"] <= 4.0
    
    def _is_visible(self, blackboard):
        """Verifica si el fantasma está visible"""
        current_time = blackboard["current_time"]
        
        # Actualizar estado de invisibilidad
        if self.is_invisible:
            if current_time - self.invisibility_start_time >= self.invisibility_duration:
                self.is_invisible = False
                print("👻 Fantasma se vuelve VISIBLE")
                
        return not self.is_invisible
    
    def _can_become_invisible(self, blackboard):
        """Verifica si puede volverse invisible"""
        current_time = blackboard["current_time"]
        distance = blackboard["distance_to_player"]
        
        # Puede volverse invisible si ha pasado el cooldown y el jugador está a distancia razonable
        return (not self.is_invisible and 
                current_time - self.last_invisibility_time >= self.invisibility_cooldown and 
                1.5 <= distance <= 8.0)  # Rango más amplio
    
    def _activate_invisibility(self, blackboard):
        """Activa la invisibilidad del fantasma"""
        current_time = blackboard["current_time"]
        
        self.is_invisible = True
        self.invisibility_start_time = current_time
        self.last_invisibility_time = current_time
        
        print("👻 Fantasma se vuelve INVISIBLE por 3 segundos")
        
        # Mientras está invisible, se mueve aleatoriamente
        self._invisible_teleport(blackboard)
        
        return True
    
    def _invisible_teleport(self, blackboard):
        """Teletransporte aleatorio cuando está invisible"""
        try:
            # Encontrar una posición aleatoria válida cerca del jugador
            player_pos = blackboard["player_pos"]
            
            for _ in range(10):  # 10 intentos
                # Posición aleatoria en un radio de 3-7 tiles del jugador
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(3, 7)
                
                new_x = int(player_pos[0] + distance * math.cos(angle))
                new_y = int(player_pos[1] + distance * math.sin(angle))
                
                if self.pathfinder.is_valid_position(new_x, new_y):
                    self.enemy["pos"] = [new_x, new_y]
                    print(f"👻 Fantasma se teletransportó a [{new_x}, {new_y}] mientras estaba invisible")
                    return True
            
            return False
        except:
            return False
        
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
    
    def is_currently_invisible(self):
        """Retorna si el fantasma está actualmente invisible (para el main.py)"""
        current_time = time.time()
        
        # Actualizar estado de invisibilidad
        if self.is_invisible:
            if current_time - self.invisibility_start_time >= self.invisibility_duration:
                self.is_invisible = False
                
        return self.is_invisible

class ZombieBehavior(EnemyBehavior):
    """
    🧟 ZOMBIE MEJORADO: Persecución lenta pero implacable + comportamiento de horda
    Tipo: Te persigue constantemente pero MUY lento, como un verdadero zombie
    """
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        super().__init__(enemy_data, pathfinder, player_pos_getter, all_enemies)
        self.last_move_time = 0
        self.base_move_delay = 0.8  # Muy lento como zombie clásico
        self.current_move_delay = self.base_move_delay
        
        # NUEVO: Sistema de horda
        self.horde_radius = 3  # Radio para detectar otros zombies
        self.horde_boost = False  # Si está en horda se mueve más rápido
        self.last_horde_check = 0
        self.horde_check_interval = 1.0  # Verificar horda cada segundo
        
        # NUEVO: Sistema de "olfato" para perseguir incluso cuando el jugador está lejos
        self.scent_memory = []  # Memoria de dónde estaba el jugador
        self.max_scent_age = 5.0  # Tiempo que dura el "olfato"
        
        print(f"🧟 Zombie inicializado - persecución lenta pero implacable")
        self._create_behavior_tree()
        
    def _create_behavior_tree(self):
        """Crea el árbol de comportamiento para el zombie mejorado"""
        
        # Selector principal con detección de horda
        root_selector = Selector("ZombieMainSelector")
        
        # Secuencia de persecución directa (prioridad más alta)
        chase_sequence = Sequence("ChaseSequence")
        chase_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        chase_sequence.add_child(Condition(self._can_see_player, "CanSeePlayer"))
        chase_sequence.add_child(Action(self._relentless_chase, "RelentlessChase"))
        
        # Secuencia de seguir rastro (cuando perdió de vista al jugador)
        scent_sequence = Sequence("ScentSequence")
        scent_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        scent_sequence.add_child(Condition(self._has_scent_trail, "HasScentTrail"))
        scent_sequence.add_child(Action(self._follow_scent, "FollowScent"))
        
        # Vagar como último recurso (muy raro)
        wander_sequence = Sequence("WanderSequence")
        wander_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        wander_sequence.add_child(Action(self._zombie_wander, "ZombieWander"))
        
        # Ensamblar el árbol (prioridad: perseguir > seguir rastro > vagar)
        root_selector.add_child(chase_sequence)
        root_selector.add_child(scent_sequence)
        root_selector.add_child(wander_sequence)
        
        self.behavior_tree = BehaviorTree(root_selector, "ZombieBehavior")
        
    def _can_move_now(self, blackboard):
        """Controla la velocidad del zombie con boost de horda"""
        current_time = blackboard["current_time"]
        
        # Verificar si está en horda para acelerar
        self._check_horde_status(blackboard)
        
        return current_time - self.last_move_time >= self.current_move_delay
        
    def _check_horde_status(self, blackboard):
        """Verifica si el zombie está cerca de otros zombies (horda)"""
        current_time = blackboard["current_time"]
        
        # Solo verificar cada cierto tiempo
        if current_time - self.last_horde_check < self.horde_check_interval:
            return
            
        self.last_horde_check = current_time
        enemy_pos = blackboard["enemy_pos"]
        all_enemies = blackboard["all_enemies"]
        
        nearby_zombies = 0
        for other_enemy in all_enemies:
            if (other_enemy != self.enemy and 
                other_enemy.get("type") == "🧟"):  # Es otro zombie
                
                other_pos = other_enemy["pos"]
                distance = math.sqrt((enemy_pos[0] - other_pos[0])**2 + 
                                   (enemy_pos[1] - other_pos[1])**2)
                
                if distance <= self.horde_radius:
                    nearby_zombies += 1
        
        # Si hay 1+ zombies cerca, activar boost de horda
        old_horde_status = self.horde_boost
        self.horde_boost = nearby_zombies >= 1
        
        if self.horde_boost:
            self.current_move_delay = self.base_move_delay * 0.6  # 40% más rápido en horda
            if not old_horde_status:
                print(f"🧟 Zombie formó HORDA con {nearby_zombies} zombies - ¡Se mueve más rápido!")
        else:
            self.current_move_delay = self.base_move_delay
            if old_horde_status:
                print(f"🧟 Zombie perdió la horda - vuelve a velocidad normal")
        
    def _can_see_player(self, blackboard):
        """Verifica si puede 'ver' al jugador (distancia razonable)"""
        distance = blackboard["distance_to_player"]
        
        # Actualizar memoria de olfato
        self._update_scent_trail(blackboard)
        
        return distance <= 12.0  # Amplio rango de "vista" zombie
        
    def _update_scent_trail(self, blackboard):
        """Actualiza la memoria de olfato del zombie"""
        current_time = blackboard["current_time"]
        player_pos = blackboard["player_pos"]
        
        # Agregar posición actual del jugador al rastro
        self.scent_memory.append({
            'pos': player_pos.copy(),
            'time': current_time
        })
        
        # Limpiar rastros viejos
        self.scent_memory = [scent for scent in self.scent_memory 
                           if current_time - scent['time'] <= self.max_scent_age]
        
    def _relentless_chase(self, blackboard):
        """Persecución implacable pero lenta del jugador"""
        self.last_move_time = blackboard["current_time"]
        
        # MEJORA: Usar A* para perseguir inteligentemente
        success = self._move_toward_player(blackboard)
        
        if success and self.horde_boost:
            # Sonido de horda (opcional, se puede implementar después)
            pass
            
        return success
        
    def _has_scent_trail(self, blackboard):
        """Verifica si tiene rastro de olfato que seguir"""
        return len(self.scent_memory) > 0
        
    def _follow_scent(self, blackboard):
        """Sigue el rastro de olfato hacia la última posición conocida del jugador"""
        try:
            self.last_move_time = blackboard["current_time"]
            
            if not self.scent_memory:
                return False
                
            # Seguir la posición más reciente en el rastro
            target_scent = self.scent_memory[-1]
            target_pos = target_scent['pos']
            enemy_pos = blackboard["enemy_pos"]
            
            # Usar A* para ir hacia la posición del rastro
            dx, dy = self.pathfinder.get_next_move(
                enemy_pos[0], enemy_pos[1],
                target_pos[0], target_pos[1]
            )
            
            new_x = enemy_pos[0] + dx
            new_y = enemy_pos[1] + dy
            
            if self.pathfinder.is_valid_position(new_x, new_y):
                self.enemy["pos"] = [new_x, new_y]
                self.enemy["dir"] = [dx, dy]
                
                # Si llegó a la posición del rastro, eliminarla
                if [new_x, new_y] == target_pos:
                    self.scent_memory.pop()
                    
                return True
            return False
        except:
            return False
        
    def _zombie_wander(self, blackboard):
        """Vagar zombie (muy ocasional)"""
        try:
            self.last_move_time = blackboard["current_time"]
            enemy_pos = blackboard["enemy_pos"]
            
            # Movimiento lento y aleatorio
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

class ClownBehavior(EnemyBehavior):
    """
    🤡 PAYASO MEJORADO: Comportamiento travieso e impredecible que confunde al jugador
    Tipo: Velocidad variable, imitación de movimientos, y efectos de confusión
    """
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        super().__init__(enemy_data, pathfinder, player_pos_getter, all_enemies)
        self.last_move_time = 0
        
        # NUEVO: Sistema de velocidad variable (travieso)
        self.speed_modes = ["slow", "normal", "fast", "crazy"]
        self.current_speed_mode = "normal"
        self.speed_change_time = 0
        self.speed_change_interval = 3.0  # Cambiar velocidad cada 3 segundos
        
        # NUEVO: Sistema de imitación de movimientos del jugador
        self.mimic_mode = False
        self.player_movement_history = []  # Historial de movimientos del jugador
        self.mimic_delay = 1.0  # Delay para imitar movimientos
        self.last_player_pos = [0, 0]
        
        # NUEVO: Sistema de confusión (movimientos erráticos)
        self.confusion_mode = False
        self.confusion_start_time = 0
        self.confusion_duration = 2.0
        self.confusion_cooldown = 6.0
        self.last_confusion_time = 0
        
        # NUEVO: Comportamiento de "burla" (se acerca y se aleja)
        self.taunt_mode = False
        self.taunt_phase = "approach"  # "approach" o "retreat"
        self.taunt_distance = 4.0
        
        print(f"🤡 Payaso travieso inicializado - comportamiento impredecible y confuso")
        self._create_behavior_tree()
        
    def _create_behavior_tree(self):
        """Crea el árbol de comportamiento para el payaso mejorado"""
        
        # Selector principal con múltiples comportamientos traviesos
        root_selector = Selector("ClownMainSelector")
        
        # Secuencia de confusión (máxima prioridad)
        confusion_sequence = Sequence("ConfusionSequence")
        confusion_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        confusion_sequence.add_child(Condition(self._should_activate_confusion, "ShouldActivateConfusion"))
        confusion_sequence.add_child(Action(self._activate_confusion, "ActivateConfusion"))
        
        # Secuencia de confusión activa
        confused_sequence = Sequence("ConfusedSequence")
        confused_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        confused_sequence.add_child(Condition(self._is_confused, "IsConfused"))
        confused_sequence.add_child(Action(self._confused_movement, "ConfusedMovement"))
        
        # Secuencia de burla (acercarse y alejarse)
        taunt_sequence = Sequence("TauntSequence")
        taunt_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        taunt_sequence.add_child(Condition(self._should_taunt, "ShouldTaunt"))
        taunt_sequence.add_child(Action(self._taunt_player, "TauntPlayer"))
        
        # Secuencia de imitación
        mimic_sequence = Sequence("MimicSequence")
        mimic_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        mimic_sequence.add_child(Condition(self._should_mimic, "ShouldMimic"))
        mimic_sequence.add_child(Action(self._mimic_player, "MimicPlayer"))
        
        # Movimiento errático por defecto
        erratic_sequence = Sequence("ErraticSequence")
        erratic_sequence.add_child(Condition(self._can_move_now, "CanMoveNow"))
        erratic_sequence.add_child(Action(self._erratic_movement, "ErraticMovement"))
        
        # Ensamblar el árbol (prioridad: confusión > burla > imitación > errático)
        root_selector.add_child(confusion_sequence)
        root_selector.add_child(confused_sequence)
        root_selector.add_child(taunt_sequence)
        root_selector.add_child(mimic_sequence)
        root_selector.add_child(erratic_sequence)
        
        self.behavior_tree = BehaviorTree(root_selector, "ClownBehavior")
        
    def _can_move_now(self, blackboard):
        """Controla la velocidad variable del payaso"""
        current_time = blackboard["current_time"]
        
        # Actualizar modo de velocidad
        self._update_speed_mode(current_time)
        
        # Actualizar historial de movimientos del jugador
        self._update_player_movement_history(blackboard)
        
        # Determinar delay según modo de velocidad
        speed_delays = {
            "slow": 0.8,     # Muy lento (burlón)
            "normal": 0.4,   # Velocidad normal
            "fast": 0.2,     # Rápido (agresivo)
            "crazy": 0.1     # Súper rápido (loco)
        }
        
        current_delay = speed_delays.get(self.current_speed_mode, 0.4)
        return current_time - self.last_move_time >= current_delay
        
    def _update_speed_mode(self, current_time):
        """Actualiza el modo de velocidad del payaso"""
        if current_time - self.speed_change_time >= self.speed_change_interval:
            old_mode = self.current_speed_mode
            self.current_speed_mode = random.choice(self.speed_modes)
            self.speed_change_time = current_time
            
            if old_mode != self.current_speed_mode:
                print(f"🤡 Payaso cambió velocidad: {old_mode} → {self.current_speed_mode}")
        
    def _update_player_movement_history(self, blackboard):
        """Actualiza el historial de movimientos del jugador"""
        current_time = blackboard["current_time"]
        player_pos = blackboard["player_pos"]
        
        # Si el jugador se movió, registrar el movimiento
        if player_pos != self.last_player_pos:
            movement = {
                'from': self.last_player_pos.copy(),
                'to': player_pos.copy(),
                'time': current_time
            }
            self.player_movement_history.append(movement)
            self.last_player_pos = player_pos.copy()
            
        # Limpiar historial viejo
        self.player_movement_history = [move for move in self.player_movement_history 
                                      if current_time - move['time'] <= 10.0]
        
    def _should_activate_confusion(self, blackboard):
        """Decide si debe activar modo de confusión"""
        current_time = blackboard["current_time"]
        distance = blackboard["distance_to_player"]
        
        return (not self.confusion_mode and 
                current_time - self.last_confusion_time >= self.confusion_cooldown and 
                2.0 <= distance <= 6.0)
        
    def _activate_confusion(self, blackboard):
        """Activa el modo de confusión"""
        current_time = blackboard["current_time"]
        
        self.confusion_mode = True
        self.confusion_start_time = current_time
        self.last_confusion_time = current_time
        
        print("🤡 Payaso activó MODO CONFUSIÓN - movimientos erráticos por 2 segundos")
        return True
        
    def _is_confused(self, blackboard):
        """Verifica si está en modo confusión"""
        current_time = blackboard["current_time"]
        
        if self.confusion_mode:
            if current_time - self.confusion_start_time >= self.confusion_duration:
                self.confusion_mode = False
                print("🤡 Payaso salió del modo confusión")
                
        return self.confusion_mode
        
    def _confused_movement(self, blackboard):
        """Movimiento súper errático durante confusión"""
        try:
            self.last_move_time = blackboard["current_time"]
            enemy_pos = blackboard["enemy_pos"]
            
            # Movimientos completamente aleatorios y rápidos
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
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
        
    def _should_taunt(self, blackboard):
        """Decide si debe burlarse del jugador"""
        distance = blackboard["distance_to_player"]
        
        # Alternar entre acercarse y alejarse
        if not self.taunt_mode:
            return 3.0 <= distance <= 8.0
        else:
            # Ya está en modo burla, continuar
            return True
        
    def _taunt_player(self, blackboard):
        """Comportamiento de burla: acercarse y alejarse"""
        try:
            self.last_move_time = blackboard["current_time"]
            distance = blackboard["distance_to_player"]
            
            if not self.taunt_mode:
                self.taunt_mode = True
                self.taunt_phase = "approach"
                print("🤡 Payaso inició BURLA - se acerca al jugador")
            
            if self.taunt_phase == "approach":
                # Acercarse hasta cierta distancia
                if distance > self.taunt_distance:
                    success = self._move_toward_player(blackboard)
                else:
                    # Cambiar a fase de retirada
                    self.taunt_phase = "retreat"
                    print("🤡 Payaso cambia a RETIRADA - se aleja burlándose")
                    success = self._move_away_from_player(blackboard)
            else:  # retreat
                # Alejarse hasta cierta distancia
                if distance < self.taunt_distance + 3:
                    success = self._move_away_from_player(blackboard)
                else:
                    # Terminar burla
                    self.taunt_mode = False
                    print("🤡 Payaso terminó la burla")
                    success = True
                    
            return success
        except:
            return False
        
    def _should_mimic(self, blackboard):
        """Decide si debe imitar al jugador"""
        distance = blackboard["distance_to_player"]
        
        # Solo imitar cuando está a distancia media y tiene historial
        return (4.0 <= distance <= 10.0 and 
                len(self.player_movement_history) > 0 and 
                random.random() < 0.3)  # 30% probabilidad
        
    def _mimic_player(self, blackboard):
        """Imita los movimientos del jugador con delay"""
        try:
            self.last_move_time = blackboard["current_time"]
            current_time = blackboard["current_time"]
            
            # Buscar un movimiento del jugador para imitar (con delay)
            for move in self.player_movement_history:
                if current_time - move['time'] >= self.mimic_delay:
                    # Calcular dirección del movimiento del jugador
                    player_dx = move['to'][0] - move['from'][0]
                    player_dy = move['to'][1] - move['from'][1]
                    
                    # Imitar ese movimiento
                    enemy_pos = blackboard["enemy_pos"]
                    new_x = enemy_pos[0] + player_dx
                    new_y = enemy_pos[1] + player_dy
                    
                    if self.pathfinder.is_valid_position(new_x, new_y):
                        self.enemy["pos"] = [new_x, new_y]
                        self.enemy["dir"] = [player_dx, player_dy]
                        
                        # Remover movimiento imitado
                        self.player_movement_history.remove(move)
                        print(f"🤡 Payaso imitó movimiento del jugador: [{player_dx}, {player_dy}]")
                        return True
            
            return False
        except:
            return False
        
    def _erratic_movement(self, blackboard):
        """Movimiento errático por defecto (más interesante)"""
        try:
            self.last_move_time = blackboard["current_time"]
            enemy_pos = blackboard["enemy_pos"]
            player_pos = blackboard["player_pos"]
            
            # Combinar movimiento aleatorio con ligera tendencia hacia/lejos del jugador
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            
            # 70% aleatorio, 30% hacia el jugador
            if random.random() < 0.7:
                dx, dy = random.choice(directions)
            else:
                # Calcular dirección hacia el jugador
                if player_pos[0] > enemy_pos[0]:
                    dx = 1
                elif player_pos[0] < enemy_pos[0]:
                    dx = -1
                else:
                    dx = 0
                    
                if player_pos[1] > enemy_pos[1]:
                    dy = 1
                elif player_pos[1] < enemy_pos[1]:
                    dy = -1
                else:
                    dy = 0
            
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
    Comportamiento del Demonio (👺) - CORREGIDO CON TELETRANSPORTE ALEATORIO
    Tipo: Se teletransporta a posiciones ALEATORIAS del mapa (no cerca del jugador)
    """
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        super().__init__(enemy_data, pathfinder, player_pos_getter, all_enemies)
        self.last_teleport_time = 0
        self.teleport_cooldown = 4.0  # Cada 4 segundos
        self.last_move_time = 0
        self.move_delay = 0.7  # Movimiento normal lento
        
        print(f"👺 Demonio inicializado - teletransporte ALEATORIO cada {self.teleport_cooldown}s")
        self._create_behavior_tree()
        
    def _create_behavior_tree(self):
        """Crea el árbol de comportamiento para el demonio"""
        
        # Selector principal
        root_selector = Selector("DemonMainSelector")
        
        # Secuencia de teletransporte ALEATORIO
        teleport_sequence = Sequence("TeleportSequence")
        teleport_sequence.add_child(Condition(self._can_teleport, "CanTeleport"))
        teleport_sequence.add_child(Action(self._teleport_randomly, "TeleportRandomly"))
        
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
        
        # Puede teletransportarse si ha pasado el cooldown
        return current_time - self.last_teleport_time >= self.teleport_cooldown
        
    def _teleport_randomly(self, blackboard):
        """CORREGIDO: Se teletransporta a una posición COMPLETAMENTE ALEATORIA del mapa"""
        try:
            current_time = blackboard["current_time"]
            self.last_teleport_time = current_time
            
            # NUEVO: Obtener el mapa actual para encontrar posiciones válidas
            # Nota: Necesitaremos acceso al mapa actual, lo simularemos aquí
            pathfinder = blackboard["pathfinder"]
            
            # Encontrar TODAS las posiciones válidas del mapa (no solo cerca del jugador)
            valid_positions = []
            
            # Buscar en todo el grid del pathfinder
            for y in range(1, pathfinder.height - 1):
                for x in range(1, pathfinder.width - 1):
                    if pathfinder.is_valid_position(x, y):
                        valid_positions.append([x, y])
            
            if valid_positions:
                # Elegir una posición COMPLETAMENTE ALEATORIA
                new_pos = random.choice(valid_positions)
                old_pos = self.enemy["pos"].copy()
                self.enemy["pos"] = new_pos
                self.enemy["dir"] = [0, 0]  # Sin dirección específica tras teletransporte
                
                print(f"👺 Demonio se teletransportó ALEATORIAMENTE de {old_pos} a {new_pos}")
                return True
            
            print("👺 No se encontraron posiciones válidas para teletransporte aleatorio")
            return False
            
        except Exception as e:
            print(f"❌ Error en teletransporte aleatorio del demonio: {e}")
            return False
        
    def _normal_move(self, blackboard):
        """Movimiento normal cuando no puede teletransportarse"""
        self.last_move_time = blackboard["current_time"]
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
    
    if enemy_type == "👽":  # Alien - A* inteligente balanceado
        return AlienBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    elif enemy_type == "👻":  # Fantasma - INVISIBILIDAD TEMPORAL
        return GhostBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    elif enemy_type == "🧟":  # Zombie - PERSECUCIÓN LENTA + HORDA (MEJORADO)
        return ZombieBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    elif enemy_type == "🦹":  # Villano - Persecución y emboscada balanceada
        return VillainBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    elif enemy_type == "👺":  # Demonio - TELETRANSPORTE ALEATORIO (CORREGIDO)
        return DemonBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    elif enemy_type == "🤡":  # Payaso - COMPORTAMIENTO TRAVIESO (MEJORADO)
        return ClownBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)
    else:
        # Comportamiento por defecto (Alien)
        return AlienBehavior(enemy_data, pathfinder, player_pos_getter, all_enemies)