# ========================================
# PERRO HÉROE - SISTEMA MEJORADO CON AIM BOT Y PAREDES INFERNALES
# ========================================
# Protagonista: Sprite del perro + sprites de enemigos + sprite de caca + portada + BLOQUE ROJO INFERNAL
# Estructura: assets/images/, assets/sounds/, assets/music/
# Cumple requisitos del examen parcial de IA
# ========================================

import pygame
import sys
import random
import time
import math
from scripts import AStar, create_enemy_behavior, GhostBehavior

# Inicializar Pygame
pygame.init()

# NUEVO: Inicializar sistema de joysticks/controles
pygame.joystick.init()

# NUEVO: Sistema de control Xbox 360
controller = None
controller_connected = False
last_button_a_state = False  # Para evitar disparos múltiples con botón A
last_button_b_state = False  # NUEVO: Para evitar navegación múltiple con botón B
last_space_state = False  # Para evitar disparos múltiples con teclado

def init_controller():
    """Inicializa el control Xbox 360 con mejor detección"""
    global controller, controller_connected
    
    # Detectar controles conectados
    joystick_count = pygame.joystick.get_count()
    
    if joystick_count > 0:
        controller = pygame.joystick.Joystick(0)
        controller.init()
        controller_connected = True
        print(f"🎮 Control detectado: {controller.get_name()}")
        print(f"🕹️ Ejes: {controller.get_numaxes()}")
        print(f"🔘 Botones: {controller.get_numbuttons()}")
        
        # NUEVO: Verificar que el botón A existe
        if controller.get_numbuttons() > 0:
            print("✅ Botón A (botón 0) disponible")
        else:
            print("⚠️ No se detectaron botones en el control")
    else:
        controller_connected = False
        print("🚫 No se detectó ningún control")

def get_controller_movement():
    """Obtiene el movimiento del joystick izquierdo y D-pad"""
    if not controller_connected:
        return [0, 0]
    
    try:
        # Leer joystick izquierdo (ejes 0 y 1)
        stick_x = controller.get_axis(0)  # Eje X del joystick izquierdo
        stick_y = controller.get_axis(1)  # Eje Y del joystick izquierdo
        
        # Leer D-pad (sombrero 0)
        if controller.get_numhats() > 0:
            hat_x, hat_y = controller.get_hat(0)
        else:
            hat_x, hat_y = 0, 0
        
        # Zona muerta para el joystick
        deadzone = 0.3
        if abs(stick_x) < deadzone:
            stick_x = 0
        if abs(stick_y) < deadzone:
            stick_y = 0
        
        # Combinar joystick y D-pad (prioridad al D-pad)
        if hat_x != 0 or hat_y != 0:
            return [hat_x, -hat_y]  # Invertir Y del D-pad
        else:
            return [stick_x, stick_y]
            
    except Exception as e:
        print(f"Error leyendo control: {e}")
        return [0, 0]

def get_controller_shoot():
    """MEJORADO: Detecta si se presiona el botón A - MÁS RESPONSIVO"""
    global last_button_a_state
    
    if not controller_connected:
        return False
    
    try:
        # Botón A es el botón 0 en Xbox 360
        button_a_pressed = controller.get_button(0)
        
        # MEJORADO: Sistema de detección más responsivo
        if button_a_pressed and not last_button_a_state:
            last_button_a_state = True
            print("🎮 ¡Botón A presionado! Disparando...")
            return True
        elif not button_a_pressed:
            last_button_a_state = False
            
        return False
    except Exception as e:
        print(f"❌ Error leyendo botón A: {e}")
        return False

# NUEVO: Función para detectar botón B en menús
def get_controller_button_b():
    """Detecta si se presiona el botón B - PARA NAVEGACIÓN EN MENÚS"""
    global last_button_b_state
    
    if not controller_connected:
        return False
    
    try:
        # Botón B es el botón 1 en Xbox 360
        button_b_pressed = controller.get_button(1)
        
        # Solo activar en el momento que se presiona (no mantener)
        if button_b_pressed and not last_button_b_state:
            last_button_b_state = True
            return True
        elif not button_b_pressed:
            last_button_b_state = False
            
        return False
    except Exception as e:
        return False

# NUEVO: Función para detectar botón A en menús (separada del disparo)
def get_controller_button_a_menu():
    """Detecta si se presiona el botón A - PARA NAVEGACIÓN EN MENÚS"""
    global last_button_a_state
    
    if not controller_connected:
        return False
    
    try:
        # Botón A es el botón 0 en Xbox 360
        button_a_pressed = controller.get_button(0)
        
        # Solo activar en el momento que se presiona (no mantener)
        if button_a_pressed and not last_button_a_state:
            last_button_a_state = True
            return True
        elif not button_a_pressed:
            last_button_a_state = False
            
        return False
    except Exception as e:
        return False

def normalize_direction(dx, dy):
    """Normaliza una dirección a 4 direcciones cardinales: ↑↓←→ (SIN diagonales)"""
    if dx == 0 and dy == 0:
        return [0, 0]
    
    # Convertir a direcciones discretas (SOLO 4 direcciones como antes)
    if abs(dx) > abs(dy):
        # Principalmente horizontal
        if dx > 0:
            return [1, 0]  # Derecha →
        else:
            return [-1, 0]  # Izquierda ←
    else:
        # Principalmente vertical
        if dy > 0:
            return [0, 1]  # Abajo ↓
        else:
            return [0, -1]  # Arriba ↑

def ensure_valid_shooting_direction():
    """Asegura que siempre haya una dirección válida para disparar"""
    global last_direction, current_direction
    
    # Si last_direction es [0,0], usar la dirección del sprite actual
    if last_direction == [0, 0]:
        if current_direction == 'up':
            last_direction = [0, -1]
        elif current_direction == 'down':
            last_direction = [0, 1]
        elif current_direction == 'left':
            last_direction = [-1, 0]
        elif current_direction == 'right':
            last_direction = [1, 0]
        else:
            last_direction = [1, 0]  # Derecha por defecto

def debug_controller_state():
    """Función de debug para verificar el estado del control"""
    if controller_connected and controller:
        try:
            print(f"🎮 DEBUG CONTROL:")
            print(f"   - Nombre: {controller.get_name()}")
            print(f"   - Botones disponibles: {controller.get_numbuttons()}")
            
            # Verificar estado del botón A específicamente
            if controller.get_numbuttons() > 0:
                button_a_state = controller.get_button(0)
                print(f"   - Botón A (0): {'PRESIONADO' if button_a_state else 'liberado'}")
            else:
                print("   - ¡NO HAY BOTONES DETECTADOS!")
                
        except Exception as e:
            print(f"❌ Error en debug del control: {e}")
    else:
        print("🚫 No hay control conectado")

# Intentar inicializar control al inicio
init_controller()

# ========================================
# NIVELES CORREGIDOS - PUERTAS VISIBLES
# ========================================
# CORREGIDO: Asegurar que todas las puertas (2) estén en posiciones accesibles

levels = [
    # NIVEL 1 - ENTRADA AL INFIERNO (PUERTA CORREGIDA)
    {
        'id': 1,
        'name': 'Portal de Entrada',
        'difficulty': 'Principiante',
        'description': 'Las puertas del infierno se abren ante ti',
        'maze': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,0,3,0,1],
            [1,0,1,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,0,1,0,1,1,1,1,0,1,0,1,0,1,1,1,1,1,0,1,1,1,0,1],
            [1,0,0,0,1,3,0,0,0,0,0,0,0,0,0,3,0,1,0,0,0,0,0,1],
            [1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
            [1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,0,1,1,0,0,0,1,1,0,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,1,3,0,0,0,3,1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,1,1,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1], # PUERTA EN (22,13)
        ]
    },

    # NIVEL 2 - CÁMARAS DE TORMENTO (PUERTA CORREGIDA)
    {
        'id': 2,
        'name': 'Cámaras de Tormento',
        'difficulty': 'Iniciado',
        'description': 'Los gritos resuenan en estas cámaras malditas',
        'maze': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,3,0,1],
            [1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,0,1,0,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
            [1,0,1,1,1,1,1,1,0,1,0,1,0,1,0,1,1,1,1,1,0,1,0,1],
            [1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,1],
            [1,1,1,1,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,0,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,3,0,1],
            [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1], # PUERTA EN (22,13)
        ]
    },

    # NIVEL 3 - LABERINTO DE FUEGO (PUERTA CORREGIDA)
    {
        'id': 3,
        'name': 'Laberinto de Fuego',
        'difficulty': 'Guerrero',
        'description': 'Las llamas danzan en cada esquina',
        'maze': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,3,0,1],
            [1,0,1,1,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,1,0,1],
            [1,0,1,0,1,1,1,1,1,0,1,0,1,0,1,1,1,1,1,1,0,1,0,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1,0,1,1,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,0,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,1,0,1,0,1],
            [1,0,1,0,0,0,0,0,0,0,1,3,1,0,0,0,0,0,0,0,0,1,0,1],
            [1,0,1,1,1,1,1,1,1,0,1,0,1,0,1,1,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1], # PUERTA EN (22,13)
        ]
    },

    # NIVEL 4 - FORTALEZA DEMONÍACA (PUERTA CORREGIDA)
    {
        'id': 4,
        'name': 'Fortaleza Demoníaca',
        'difficulty': 'Veterano',
        'description': 'El corazón del mal late en esta fortaleza',
        'maze': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,3,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,3,1],
            [1,0,1,0,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,0,1,1,0,1],
            [1,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,1],
            [1,0,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,0,1,1],
            [1,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
            [1,1,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,1,3,1,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,0,1,1,1,0,1,0,1,0,1,0,1,0,1,1,1,0,1,1,1,1],
            [1,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
            [1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,1,0,1],
            [1,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,1],
            [1,0,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,0,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,3,2,1], # PUERTA EN (22,13)
        ]
    },

    # NIVEL 5 - TRONO DE LUCIFER (PUERTA CORREGIDA)
    {
        'id': 5,
        'name': 'Trono de Lucifer',
        'difficulty': 'Señor Infernal',
        'description': 'El mismísimo trono del príncipe de las tinieblas',
        'maze': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,3,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,3,1],
            [1,0,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
            [1,0,1,0,1,1,1,1,0,1,0,1,0,1,0,1,1,1,1,1,0,1,0,1],
            [1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,1,1,0,1,0,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1],
            [1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,0,1,1,0,1,0,1,1,0,1,0,1,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,1,3,0,0,0,3,1,0,0,0,0,0,0,1,0,1],
            [1,0,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,0,1,0,1],
            [1,0,0,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,1,0,0,0,1],
            [1,1,1,0,1,0,1,1,1,0,1,0,1,0,1,1,1,1,0,1,0,1,1,1],
            [1,0,0,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,1,0,3,2,1], # PUERTA EN (22,13)
        ]
    }
]

# Configuración de la pantalla
TILE_SIZE = 40  # Tamaño de cada celda

# Configuración inicial de dimensiones (serán actualizadas dinámicamente)
initial_maze = levels[0]['maze']
MAZE_WIDTH = len(initial_maze[0])
MAZE_HEIGHT = len(initial_maze)
SCREEN_WIDTH = TILE_SIZE * MAZE_WIDTH
SCREEN_HEIGHT = TILE_SIZE * MAZE_HEIGHT + 100

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🔥 Dimensiones Infernales - Sistema de IA Avanzado")

# Configuración de fuentes
pygame.font.init()
font = pygame.font.SysFont('Arial', 30)
small_font = pygame.font.SysFont('Arial', 20)
emoji_font = pygame.font.SysFont('Segoe UI Emoji', TILE_SIZE)

# Colores del juego - TEMA INFERNAL
COLOR_WALL = (20, 0, 0)          # Rojo muy oscuro para paredes
COLOR_PATH = (80, 40, 40)        # Rojo oscuro para caminos
COLOR_BACKGROUND = (0, 0, 0)     # Negro profundo
COLOR_PLAYER = (255, 255, 0)     # Amarillo brillante para el protagonista
COLOR_EXIT = (255, 100, 0)       # Naranja brillante para salida
COLOR_ENEMY = (255, 0, 0)        # Rojo intenso para enemigos
COLOR_TEXT = (255, 255, 255)     # Blanco para texto
COLOR_AIMBOT = (255, 255, 0)     # Amarillo para aim bot
COLOR_BONUS = (255, 215, 0)      # Dorado para bonus
COLOR_FIRE = (255, 69, 0)        # Rojo fuego para efectos
COLOR_LAVA = (139, 0, 0)         # Rojo lava para elementos especiales

# Game states (SOLO 3 ESTADOS)
STATE_MENU = 'MENU'
STATE_DIFF = 'DIFFICULTY'
STATE_PLAY = 'PLAY'

# Menú principal simplificado (SOLO 3 OPCIONES)
menu_options = ['Nueva Partida', 'Seleccionar Dificultad', 'Salir']
difficulty_options = ['Fácil', 'Medio', 'Difícil']
FPS_levels = {'Fácil': 5, 'Medio': 7, 'Difícil': 9}  # AUMENTADO para más velocidad

# Variables del menú (CONTROLADAS Y LIMITADAS)
menu_idx = 0  # SIEMPRE entre 0-2 (3 opciones máximo)
diff_idx = 1  # Por defecto 'Medio'
game_state = STATE_MENU
FPS = FPS_levels[difficulty_options[diff_idx]]

# Función para resetear menú
def reset_menu():
    global menu_idx
    menu_idx = 0  # Resetear al inicio

# Configuración del protagonista perro (CON SOPORTE PARA SPRITES)
print("🐶 Perro héroe de las dimensiones infernales inicializado")

# Variables para sprites
use_sprites = False
dog_sprites = {}
enemy_sprites = {}  # Sprites de enemigos
poop_sprite = None  # Sprite de caca
cover_image = None  # Portada del juego
wall_sprite = None  # NUEVO: Sprite de pared infernal
current_direction = 'right'

# ========================================
# SISTEMA DE AIM BOT MEJORADO
# ========================================

class AimBot:
    """Sistema de aim bot inteligente para ayudar al jugador"""
    
    def __init__(self, detection_range=6):
        self.detection_range = detection_range
        self.aim_assistance = True
        self.target_enemy = None
        
    def find_nearest_enemy(self, player_pos, enemies):
        """Encuentra el enemigo más cercano dentro del rango"""
        nearest_enemy = None
        min_distance = float('inf')
        
        for enemy in enemies:
            enemy_pos = enemy['pos']
            distance = math.sqrt((player_pos[0] - enemy_pos[0])**2 + 
                               (player_pos[1] - enemy_pos[1])**2)
            
            if distance <= self.detection_range and distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy
                
        return nearest_enemy, min_distance
    
    def calculate_aim_direction(self, player_pos, target_pos):
        """Calcula la dirección óptima para disparar"""
        dx = target_pos[0] - player_pos[0]
        dy = target_pos[1] - player_pos[1]
        
        # Normalizar direcciones para proyectiles
        if abs(dx) > abs(dy):
            return [1 if dx > 0 else -1, 0]
        else:
            return [0, 1 if dy > 0 else -1]
    
    def get_aim_direction(self, player_pos, enemies):
        """Obtiene la dirección de disparo asistido"""
        if not self.aim_assistance:
            return None
            
        nearest_enemy, distance = self.find_nearest_enemy(player_pos, enemies)
        
        if nearest_enemy:
            self.target_enemy = nearest_enemy
            return self.calculate_aim_direction(player_pos, nearest_enemy['pos'])
        
        self.target_enemy = None
        return None
    
    def draw_aim_indicator(self, screen, player_pos, target_pos):
        """Dibuja un indicador visual del aim bot"""
        if target_pos:
            # Línea de mira
            start_pixel = (player_pos[0] * TILE_SIZE + TILE_SIZE//2, 
                          player_pos[1] * TILE_SIZE + TILE_SIZE//2)
            end_pixel = (target_pos[0] * TILE_SIZE + TILE_SIZE//2, 
                        target_pos[1] * TILE_SIZE + TILE_SIZE//2)
            
            pygame.draw.line(screen, COLOR_AIMBOT, start_pixel, end_pixel, 2)
            
            # Círculo alrededor del objetivo
            pygame.draw.circle(screen, COLOR_AIMBOT, end_pixel, TILE_SIZE//2, 2)

# Instancia global del aim bot
aim_bot = AimBot(detection_range=6)

def load_dog_sprite():
    """Función para cargar el sprite del perro si existe"""
    global use_sprites, dog_sprites
    
    sprite_path = 'assets/images/perro.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"✅ ¡Sprite del perro encontrado! Cargando desde: {sprite_path}")
            
            # Cargar el sprite
            dog_spritesheet = pygame.image.load(sprite_path)
            
            # Obtener dimensiones
            sprite_width = dog_spritesheet.get_width()
            sprite_height = dog_spritesheet.get_height()
            
            print(f"📏 Dimensiones del sprite: {sprite_width}x{sprite_height}")
            
            # Escalar al tamaño de celda
            scaled_sprite = pygame.transform.scale(dog_spritesheet, (TILE_SIZE, TILE_SIZE))
            
            # Crear sprites para todas las direcciones
            dog_sprites = {
                'up': [scaled_sprite],
                'right': [scaled_sprite], 
                'down': [scaled_sprite],
                'left': [pygame.transform.flip(scaled_sprite, True, False)]  # Voltear para izquierda
            }
            
            use_sprites = True
            print("🎮 ¡Sprite del perro cargado exitosamente!")
            return True
        else:
            print(f"📁 No se encontró sprite en: {sprite_path}")
            print("💡 Tip: Crea la carpeta 'assets/images/' y pon tu 'perro.png' ahí")
            return False
            
    except Exception as e:
        print(f"❌ Error cargando sprite: {e}")
        return False

def load_enemy_sprites():
    """Función para cargar sprites de criaturas infernales"""
    global enemy_sprites
    
    # Lista de criaturas con sus archivos correspondientes
    enemy_files = {
        '👻': 'fantasma.png',
        '👽': 'alien.png',
        '🧟': 'zombie.png',
        '🦹': 'villano.png',
        '👺': 'demonio.png',
        '🤡': 'payaso.png',
        '👹': 'diablo.png'
    }
    
    sprites_loaded = 0
    
    for emoji, filename in enemy_files.items():
        sprite_path = f'assets/images/{filename}'
        
        try:
            import os
            if os.path.exists(sprite_path):
                print(f"👾 Cargando criatura infernal: {sprite_path}")
                
                # Cargar sprite del enemigo
                enemy_spritesheet = pygame.image.load(sprite_path)
                
                # Escalar al tamaño de celda
                scaled_sprite = pygame.transform.scale(enemy_spritesheet, (TILE_SIZE, TILE_SIZE))
                
                # Guardar sprite (con volteo para izquierda)
                enemy_sprites[emoji] = {
                    'right': scaled_sprite,
                    'left': pygame.transform.flip(scaled_sprite, True, False)
                }
                
                sprites_loaded += 1
                print(f"✅ Sprite de {emoji} cargado!")
                
        except Exception as e:
            print(f"⚠️ Error cargando {sprite_path}: {e}")
    
    if sprites_loaded > 0:
        print(f"🔥 ¡{sprites_loaded} criaturas infernales cargadas!")
    else:
        print("📁 No se encontraron sprites de criaturas infernales")
        print("💡 Tip: Puedes agregar: fantasma.png, alien.png, zombie.png, villano.png, demonio.png, payaso.png, diablo.png en assets/images/")
    
    return sprites_loaded > 0

def load_poop_sprite():
    """Función para cargar el sprite de caca"""
    global poop_sprite
    
    sprite_path = 'assets/images/caca.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"💩 ¡Sprite de caca encontrado! Cargando desde: {sprite_path}")
            
            # Cargar el sprite
            poop_image = pygame.image.load(sprite_path)
            
            # Escalar al tamaño de celda
            poop_sprite = pygame.transform.scale(poop_image, (TILE_SIZE, TILE_SIZE))
            
            print("💩 ¡Sprite de caca cargado exitosamente!")
            return True
        else:
            print(f"📁 No se encontró sprite de caca en: {sprite_path}")
            print("💡 Tip: Agrega 'caca.png' en assets/images/")
            return False
            
    except Exception as e:
        print(f"❌ Error cargando sprite de caca: {e}")
        return False

def load_cover_image():
    """Función para cargar la portada del juego"""
    global cover_image
    
    sprite_path = 'assets/images/portada.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"🖼️ ¡Portada encontrada! Cargando desde: {sprite_path}")
            
            # Cargar la imagen
            cover_raw = pygame.image.load(sprite_path)
            
            # Escalar a un tamaño apropiado para el menú (por ejemplo, 400x300)
            cover_image = pygame.transform.scale(cover_raw, (400, 300))
            
            print("🖼️ ¡Portada cargada exitosamente!")
            return True
        else:
            print(f"📁 No se encontró portada en: {sprite_path}")
            print("💡 Tip: Agrega 'portada.png' en assets/images/")
            return False
            
    except Exception as e:
        print(f"❌ Error cargando portada: {e}")
        return False

def load_wall_sprite():
    """NUEVO: Función para cargar el sprite de pared infernal"""
    global wall_sprite
    
    sprite_path = 'assets/images/bloquerojo.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"🧱 ¡Sprite de pared infernal encontrado! Cargando desde: {sprite_path}")
            
            # Cargar el sprite
            wall_image = pygame.image.load(sprite_path)
            
            # Escalar al tamaño de celda
            wall_sprite = pygame.transform.scale(wall_image, (TILE_SIZE, TILE_SIZE))
            
            print("🧱 ¡Sprite de pared infernal cargado exitosamente!")
            return True
        else:
            print(f"📁 No se encontró sprite de pared en: {sprite_path}")
            print("💡 Tip: Agrega 'bloquerojo.png' en assets/images/")
            return False
            
    except Exception as e:
        print(f"❌ Error cargando sprite de pared: {e}")
        return False

# Intentar cargar sprites al iniciar
load_dog_sprite()
load_enemy_sprites()
load_poop_sprite()
load_cover_image()
load_wall_sprite()  # NUEVO: Cargar sprite de pared

# Función para recargar sprites durante el juego (opcional)
def reload_sprites_if_needed():
    """Recarga sprites si no están cargados pero el archivo existe"""
    global use_sprites
    if not use_sprites:
        load_dog_sprite()
    
    # También recargar sprites de enemigos
    load_enemy_sprites()
    
    # Recargar sprite de caca
    if poop_sprite is None:
        load_poop_sprite()
    
    # Recargar portada
    if cover_image is None:
        load_cover_image()
    
    # NUEVO: Recargar sprite de pared
    if wall_sprite is None:
        load_wall_sprite()

# Símbolos para elementos del juego (simplificados)
GAME_SYMBOLS = {
    0: '  ',  # Camino libre
    1: '██',  # Pared
    2: '🎯',  # Objetivo
    3: '⭐',  # Bonus
}

# Variables del juego simplificadas
player_score = 0

# Variables del juego
player_pos = [1, 1]
player_lives = 3
current_level = 0
maze = levels[current_level]['maze']
projectiles = []
last_direction = [1, 0]

# NUEVO: Sistema de diamantes obligatorios
total_diamonds = 0  # Diamantes totales en el nivel actual
collected_diamonds = 0  # Diamantes recogidos

# NUEVO: Sistema de mensajes temporales
temp_message = ""  # Mensaje temporal a mostrar
temp_message_time = 0  # Tiempo cuando se mostró el mensaje
temp_message_duration = 2.0  # Duración del mensaje en segundos

# ========================================
# CONFIGURACIÓN ALEATORIA DE ENEMIGOS
# ========================================

# Tipos de enemigos infernales disponibles
ALL_ENEMY_TYPES = ['👽', '👻', '🧟', '🦹', '👺', '🤡', '👹']

# Configuración de enemigos por nivel
ENEMIES_PER_LEVEL = {
    0: 3,  # Nivel 1: 3 enemigos
    1: 3,  # Nivel 2: 3 enemigos  
    2: 3,  # Nivel 3: 3 enemigos
    3: 3,  # Nivel 4: 3 enemigos
    4: 3   # Nivel 5: 3 enemigos
}

def find_valid_enemy_positions(maze, count=10):
    """Encuentra posiciones válidas dinámicamente en el laberinto actual"""
    height = len(maze)
    width = len(maze[0])
    valid_positions = []
    
    # Buscar todas las posiciones válidas (no paredes)
    for y in range(1, height - 1):  # Evitar bordes
        for x in range(1, width - 1):  # Evitar bordes
            if maze[y][x] == 0:  # Camino libre
                # Evitar posición inicial del jugador
                if not (x == 1 and y == 1):
                    # Evitar posición de salida
                    if maze[y][x] != 2:
                        valid_positions.append([x, y])
    
    # Mezclar y retornar las primeras 'count' posiciones
    random.shuffle(valid_positions)
    return valid_positions[:count]

def generate_random_enemies(level):
    """Genera enemigos aleatorios para un nivel específico"""
    enemy_count = ENEMIES_PER_LEVEL.get(level, 2)
    
    # Seleccionar tipos aleatorios
    selected_types = random.sample(ALL_ENEMY_TYPES, min(enemy_count, len(ALL_ENEMY_TYPES)))
    
    # Encontrar posiciones válidas
    current_maze = levels[level]['maze']
    valid_positions = find_valid_enemy_positions(current_maze, enemy_count + 5)
    
    # Si no hay posiciones, usar respaldo
    if len(valid_positions) == 0:
        valid_positions = [[2, 2], [3, 3], [4, 4], [5, 5], [6, 6]]
    
    enemies_config = []
    for i, enemy_type in enumerate(selected_types):
        if i < len(valid_positions):
            enemies_config.append({
                'type': enemy_type,
                'pos': valid_positions[i]
            })
    
    return enemies_config

# Enemigos (se generarán dinámicamente)
enemies = []

# Sistema de comportamientos de IA
enemy_behaviors = []

def show_temp_message(message):
    """Muestra un mensaje temporal que no bloquea el juego"""
    global temp_message, temp_message_time
    temp_message = message
    temp_message_time = time.time()
    print(f"📢 Mensaje temporal: {message}")

def draw_temp_message():
    """Dibuja el mensaje temporal si está activo"""
    global temp_message, temp_message_time
    
    if temp_message and time.time() - temp_message_time < temp_message_duration:
        # Calcular transparencia basada en el tiempo restante
        elapsed = time.time() - temp_message_time
        alpha = max(0, 1 - (elapsed / temp_message_duration))
        
        # Crear superficie para el mensaje
        message_surface = pygame.Surface((SCREEN_WIDTH, 100))
        message_surface.fill((0, 0, 0))
        message_surface.set_alpha(int(200 * alpha))
        
        # Dibujar fondo semi-transparente
        screen.blit(message_surface, (0, SCREEN_HEIGHT // 2 - 50))
        
        # Dibujar texto del mensaje
        text_color = (255, int(255 * alpha), int(255 * alpha))
        text = font.render(temp_message, True, text_color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
    elif temp_message and time.time() - temp_message_time >= temp_message_duration:
        # Limpiar mensaje cuando expire
        temp_message = ""

def count_diamonds_in_level(maze):
    """Cuenta los diamantes totales en un nivel"""
    count = 0
    for row in maze:
        for cell in row:
            if cell == 3:  # 3 = diamante
                count += 1
    return count

def get_player_position():
    return player_pos

# Función para inicializar comportamientos de enemigos
def initialize_enemy_behaviors():
    """Inicializa los comportamientos de IA para todos los enemigos"""
    global enemy_behaviors
    enemy_behaviors = []
    
    for enemy in enemies:
        behavior = create_enemy_behavior(
            enemy_data=enemy,
            pathfinder=pathfinder,
            player_pos_getter=get_player_position,
            all_enemies=enemies
        )
        enemy_behaviors.append(behavior)
        
        # DEBUG: Verificar si se crearon fantasmas
        if enemy['type'] == '👻':
            print(f"👻 FANTASMA CREADO: {enemy['pos']} - Puede volverse invisible")

# ========================================
# FUNCIONES BÁSICAS DEL JUEGO
# ========================================

def handle_bonus_tile(x, y):
    """Maneja las bonificaciones - DIAMANTES OBLIGATORIOS"""
    global player_score, maze, collected_diamonds
    
    if maze[y][x] == 3:  # Diamante
        player_score += 100
        collected_diamonds += 1
        maze[y][x] = 0  # Eliminar el diamante del mapa
        print(f"💎 Diamante recogido! {collected_diamonds}/{total_diamonds}")

# Actualizar dimensiones del laberinto según el nivel actual
def update_maze_dimensions():
    global MAZE_WIDTH, MAZE_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, screen
    current_maze = levels[current_level]['maze']
    MAZE_HEIGHT = len(current_maze)
    MAZE_WIDTH = len(current_maze[0])
    SCREEN_WIDTH = TILE_SIZE * MAZE_WIDTH
    SCREEN_HEIGHT = TILE_SIZE * MAZE_HEIGHT + 100
    
    # Actualizar el tamaño de la pantalla
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Inicializar pathfinder A*
pathfinder = AStar(maze)

# Funciones de dibujo actualizadas
def draw_menu():
    # Asegurar que la pantalla tenga el tamaño correcto para el menú
    menu_width = 800
    menu_height = 600
    if SCREEN_WIDTH != menu_width or SCREEN_HEIGHT != menu_height:
        global screen
        screen = pygame.display.set_mode((menu_width, menu_height))
    
    # Fondo infernal degradado
    screen.fill((20, 0, 0))
    
    # Mostrar portada si está disponible
    if cover_image:
        # Centrar la portada en la parte superior
        cover_x = (menu_width - cover_image.get_width()) // 2
        cover_y = 20
        screen.blit(cover_image, (cover_x, cover_y))
        title_y = cover_y + cover_image.get_height() + 20
    else:
        # Título con tema infernal
        title = font.render("🔥 DIMENSIONES INFERNALES 🔥", True, COLOR_FIRE)
        screen.blit(title, (menu_width // 2 - title.get_width() // 2, 50))
        subtitle = small_font.render("- Sistema de IA Demoníaca -", True, COLOR_BONUS)
        screen.blit(subtitle, (menu_width // 2 - subtitle.get_width() // 2, 90))
        title_y = 150
    
    # SOLO dibujar las 3 opciones del menú con estilo infernal
    valid_options = ['🚪 Nueva Partida', '⚙️ Dificultad', '❌ Salir']
    for i, option in enumerate(valid_options):
        if i == menu_idx:
            color = COLOR_FIRE  # Naranja fuego para opción seleccionada
            # Efecto de brillo
            shadow_text = font.render(option, True, (100, 0, 0))
            screen.blit(shadow_text, (menu_width // 2 - shadow_text.get_width() // 2 + 2, title_y + i * 50 + 2))
        else:
            color = (150, 75, 75)  # Rojo oscuro para opciones no seleccionadas
        
        text = font.render(option, True, color)
        screen.blit(text, (menu_width // 2 - text.get_width() // 2, title_y + i * 50))
    
    # Información de IA infernal
    info_lines = [
        "🎮 CONTROL XBOX 360: A=aceptar | B=atrás | Joystick/D-pad=navegar",
        "⌨️ TECLADO: Enter=aceptar | ESC=atrás | Flechas=navegar",
        "👹 CRIATURAS INFERNALES CON IA:",
        "Portal de Entrada: 3 criaturas aleatorias",
        "Cámaras de Tormento: 3 seres del averno", 
        "Laberinto de Fuego: 3 bestias infernales",
        "Fortaleza Demoníaca: 3 guardianes élite",
        "Trono de Lucifer: 3 señores supremos del mal",
        "Enemigos: 👽👻🧟🦹👺🤡👹 (7 tipos disponibles)",
        "👻 Fantasmas pueden volverse INVISIBLES (cooldown 4s)",
        "💎 RECOLECTA TODOS LOS DIAMANTES para abrir portales",
        "🚪 PUERTAS INFERNALES aparecen cuando completes todos los diamantes"
    ]
    
    start_y = title_y + 200
    for i, line in enumerate(info_lines):
        color = COLOR_FIRE if i == 2 else COLOR_BONUS
        font_size = font if i == 2 else small_font
        text = font_size.render(line, True, color)
        screen.blit(text, (50, start_y + i * 25))
    
    # Efectos de partículas infernales (simulados)
    import random
    for _ in range(5):
        x = random.randint(0, menu_width)
        y = random.randint(0, menu_height)
        pygame.draw.circle(screen, (255, 100, 0), (x, y), 2)
    
    pygame.display.flip()

def draw_difficulty_menu():
    # Asegurar tamaño correcto de pantalla
    menu_width = 800
    menu_height = 600
    if SCREEN_WIDTH != menu_width or SCREEN_HEIGHT != menu_height:
        global screen
        screen = pygame.display.set_mode((menu_width, menu_height))
    
    # Fondo infernal
    screen.fill((20, 0, 0))
    
    title = font.render("🔥 Elige tu nivel de tortura:", True, COLOR_FIRE)
    screen.blit(title, (menu_width // 2 - title.get_width() // 2, 100))
    
    # Opciones de dificultad con tema infernal
    infernal_options = ['😈 Alma Perdida', '👹 Demonio', '🔥 Señor del Infierno']
    
    for i, opt in enumerate(infernal_options):
        if i == diff_idx:
            color = COLOR_FIRE
            # Efecto de brillo para opción seleccionada
            shadow_text = font.render(opt, True, (100, 0, 0))
            screen.blit(shadow_text, (menu_width // 2 - shadow_text.get_width() // 2 + 2, 202 + i * 50))
        else:
            color = (150, 75, 75)
        
        txt = font.render(opt, True, color)
        screen.blit(txt, (menu_width // 2 - txt.get_width() // 2, 200 + i * 50))
    
    # Información de dificultad con tema infernal
    fps_info = [
        f"😈 Alma Perdida: {FPS_levels['Fácil']} FPS - Los demonios se mueven lentamente",
        f"👹 Demonio: {FPS_levels['Medio']} FPS - Velocidad infernal equilibrada", 
        f"🔥 Señor del Infierno: {FPS_levels['Difícil']} FPS - Furia demoníaca máxima"
    ]
    
    for i, info in enumerate(fps_info):
        color = COLOR_FIRE if i == diff_idx else (150, 100, 100)
        text = small_font.render(info, True, color)
        screen.blit(text, (menu_width // 2 - text.get_width() // 2, 350 + i * 30))
    
    # Advertencia infernal
    warning = small_font.render("⚠️ Cuanto mayor la dificultad, más rápidos los demonios ⚠️", True, COLOR_BONUS)
    screen.blit(warning, (menu_width // 2 - warning.get_width() // 2, 480))
    
    pygame.display.flip()

def reset_enemies():
    """Resetea enemigos de forma aleatoria según el nivel actual"""
    global enemies, enemy_behaviors, pathfinder, total_diamonds, collected_diamonds
    
    # RESETEAR SISTEMA DE DIAMANTES
    total_diamonds = count_diamonds_in_level(levels[current_level]['maze'])
    collected_diamonds = 0
    print(f"💎 Nivel {current_level + 1}: {total_diamonds} diamantes totales - TODOS REQUERIDOS")
    
    # Asegurar pathfinder
    current_maze = levels[current_level]['maze']
    pathfinder = AStar(current_maze)
    
    # Generar enemigos aleatorios
    enemies_config = generate_random_enemies(current_level)
    
    # Crear enemigos
    enemies = []
    for enemy_config in enemies_config:
        enemy = {
            'pos': enemy_config['pos'].copy(),
            'dir': [0, -1],
            'type': enemy_config['type']
        }
        enemies.append(enemy)
    
    # Respaldo si no hay enemigos
    if len(enemies) == 0:
        enemy = {
            'pos': [2, 2],
            'dir': [0, -1],
            'type': random.choice(ALL_ENEMY_TYPES)
        }
        enemies.append(enemy)
    
    # Inicializar IA
    initialize_enemy_behaviors()
    
    print(f"✅ Nivel {current_level + 1}: {len(enemies)} enemigos cargados")

def reset_game():
    global player_pos, player_lives, current_level, maze, enemies, projectiles, pathfinder
    global player_score, screen, total_diamonds, collected_diamonds, temp_message, temp_message_time
    global last_button_a_state, last_button_b_state, last_space_state
    
    player_pos = [1, 1]
    player_lives = 3
    current_level = 0
    player_score = 0
    
    # NUEVO: Limpiar mensajes temporales y estados de control
    temp_message = ""
    temp_message_time = 0
    last_button_a_state = False
    last_button_b_state = False
    last_space_state = False
    
    # Cargar laberinto del nivel inicial
    maze = levels[current_level]['maze']
    projectiles = []
    
    # Actualizar dimensiones de pantalla
    update_maze_dimensions()
    
    # Inicializar pathfinder ANTES de generar enemigos
    pathfinder = AStar(maze)
    
    # Generar enemigos DESPUÉS de inicializar pathfinder (esto también resetea diamantes)
    reset_enemies()
    
    print(f"🔄 Juego reiniciado - Nivel {current_level + 1}")

def draw_maze():
    """MEJORADO: Dibuja el laberinto con puertas más visibles"""
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            
            if maze[y][x] == 1:  # Paredes infernales
                # NUEVO: Usar sprite de pared si está disponible
                if wall_sprite:
                    screen.blit(wall_sprite, (x * TILE_SIZE, y * TILE_SIZE))
                else:
                    # Usar color sólido como respaldo
                    pygame.draw.rect(screen, COLOR_WALL, rect)
                    # Agregar borde más oscuro para efecto 3D
                    pygame.draw.rect(screen, (10, 0, 0), rect, 2)
            elif maze[y][x] == 2:  # Portal de salida - MEJORADO
                pygame.draw.rect(screen, COLOR_PATH, rect)
                # MEJORADO: Puerta más visible con animación
                pygame.draw.rect(screen, (255, 215, 0), rect, 3)  # Borde dorado
                
                # VERIFICAR si se pueden abrir las puertas
                if collected_diamonds >= total_diamonds:
                    # Puerta abierta - Verde brillante
                    pygame.draw.rect(screen, (0, 255, 0), rect)
                    door_emoji = emoji_font.render('🚪', True, (255, 255, 255))
                    screen.blit(door_emoji, (x * TILE_SIZE + 4, y * TILE_SIZE))
                    
                    # Efecto de brillo
                    import math
                    alpha = int(128 + 127 * math.sin(time.time() * 5))
                    glow_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    glow_surface.fill((0, 255, 0))
                    glow_surface.set_alpha(alpha)
                    screen.blit(glow_surface, (x * TILE_SIZE, y * TILE_SIZE))
                else:
                    # Puerta cerrada - Rojo brillante
                    pygame.draw.rect(screen, (255, 0, 0), rect)
                    door_emoji = emoji_font.render('🔒', True, (255, 255, 255))
                    screen.blit(door_emoji, (x * TILE_SIZE + 4, y * TILE_SIZE))
            elif maze[y][x] == 3:  # Tesoros infernales
                pygame.draw.rect(screen, COLOR_PATH, rect)
                # Efecto dorado brillante
                pygame.draw.rect(screen, COLOR_BONUS, rect, 3)
                bonus_emoji = emoji_font.render('💎', True, (255, 215, 0))
                screen.blit(bonus_emoji, (x * TILE_SIZE + 4, y * TILE_SIZE))
            else:  # Suelo infernal
                pygame.draw.rect(screen, COLOR_PATH, rect)
                # Agregar textura sutil al suelo
                if (x + y) % 4 == 0:
                    pygame.draw.rect(screen, (90, 45, 45), rect, 1)

def draw_player():
    """Dibuja al protagonista perro (sprite si disponible, sino emoji)"""
    x, y = player_pos
    
    # Usar sprite si está cargado, sino emoji de respaldo
    if use_sprites and dog_sprites:
        # Dibujar sprite del perro según la dirección
        screen.blit(dog_sprites[current_direction][0], (x * TILE_SIZE, y * TILE_SIZE))
    else:
        # Usar emoji de perro como respaldo
        player_emoji = emoji_font.render('🐶', True, (255, 255, 0))
        screen.blit(player_emoji, (x * TILE_SIZE + 4, y * TILE_SIZE))

def draw_enemies():
    """Dibuja enemigos (sprite si disponible, sino emoji) - VERIFICA INVISIBILIDAD DE FANTASMAS"""
    for i, enemy in enumerate(enemies):
        x, y = enemy["pos"]
        enemy_type = enemy["type"]
        
        # VERIFICAR SI EL FANTASMA ESTÁ INVISIBLE
        is_invisible = False
        if enemy_type == '👻' and i < len(enemy_behaviors):
            behavior = enemy_behaviors[i]
            if hasattr(behavior, 'is_currently_invisible'):
                is_invisible = behavior.is_currently_invisible()
        
        # NO DIBUJAR SI ESTÁ INVISIBLE
        if is_invisible:
            continue
        
        # Determinar dirección del enemigo (simple: basado en dirección de movimiento)
        enemy_dir = enemy.get("dir", [1, 0])
        sprite_direction = 'left' if enemy_dir[0] < 0 else 'right'
        
        # Usar sprite si está disponible, sino emoji
        if enemy_type in enemy_sprites:
            # Dibujar sprite del enemigo
            screen.blit(enemy_sprites[enemy_type][sprite_direction], (x * TILE_SIZE, y * TILE_SIZE))
        else:
            # Usar emoji como respaldo
            enemy_emoji = emoji_font.render(enemy_type, True, (0, 0, 0))
            screen.blit(enemy_emoji, (x * TILE_SIZE + 4, y * TILE_SIZE))

def draw_aim_bot_indicators():
    """NO DIBUJAR indicadores del aim bot"""
    pass  # Aim bot activo pero sin líneas visuales

def move_enemies():
    global enemy_behaviors, pathfinder
    
    for behavior in enemy_behaviors:
        try:
            behavior.update()
        except Exception as e:
            print(f"Error en comportamiento de enemigo: {e}")
            # Fallback a movimiento simple hacia el jugador
            enemy = behavior.enemy
            player_x, player_y = player_pos
            enemy_x, enemy_y = enemy["pos"]
            
            dx, dy = pathfinder.get_next_move(enemy_x, enemy_y, player_x, player_y)
            new_x = enemy_x + dx
            new_y = enemy_y + dy
            
            if pathfinder.is_valid_position(new_x, new_y):
                enemy["pos"] = [new_x, new_y]

def move_projectiles():
    """MEJORADO: Proyectiles más rápidos y precisos"""
    global enemies, projectiles, player_score
    newp = []
    for p in projectiles:
        # MEJORADO: Proyectiles se mueven más rápido (2 casillas por frame)
        for _ in range(2):  # Mover 2 veces por frame
            p['pos'][0] += p['dir'][0]
            p['pos'][1] += p['dir'][1]
            
            x, y = p['pos']
            
            # Verificar límites
            if not (0 <= x < MAZE_WIDTH and 0 <= y < MAZE_HEIGHT):
                break
                
            # Verificar colisión con paredes
            if maze[y][x] == 1:
                break
                    
            # Verificar colisión con enemigos
            hit = False
            for i, e in enumerate(enemies[:]):
                if e['pos'] == [x, y]:
                    # VERIFICAR SI EL FANTASMA ESTÁ INVISIBLE
                    is_invisible = False
                    if e['type'] == '👻' and i < len(enemy_behaviors):
                        behavior = enemy_behaviors[i]
                        if hasattr(behavior, 'is_currently_invisible'):
                            is_invisible = behavior.is_currently_invisible()
                    
                    # NO PUEDE SER GOLPEADO SI ESTÁ INVISIBLE
                    if not is_invisible:
                        enemies.remove(e)
                        if i < len(enemy_behaviors):
                            enemy_behaviors.pop(i)
                        player_score += 150  # Bonus por eliminar enemigo
                        hit = True
                        break
            
            if hit:
                break
        else:
            # Solo agregar si no salió del bucle con break
            if (0 <= p['pos'][0] < MAZE_WIDTH and 0 <= p['pos'][1] < MAZE_HEIGHT and 
                maze[p['pos'][1]][p['pos'][0]] != 1):
                newp.append(p)
    
    projectiles = newp

def draw_projectiles():
    """Dibuja proyectiles (sprite si disponible, sino emoji)"""
    for p in projectiles:
        x, y = p['pos']
        
        # Usar sprite de caca si está disponible, sino emoji
        if poop_sprite:
            screen.blit(poop_sprite, (x * TILE_SIZE, y * TILE_SIZE))
        else:
            # Usar emoji como respaldo
            poop = emoji_font.render('💩', True, (0, 0, 0))
            screen.blit(poop, (x * TILE_SIZE + 4, y * TILE_SIZE))

def check_enemy_collision():
    global player_score, enemies, enemy_behaviors
    
    for i, e in enumerate(enemies):
        if e['pos'] == player_pos:
            # VERIFICAR SI EL FANTASMA ESTÁ INVISIBLE
            is_invisible = False
            if e['type'] == '👻' and i < len(enemy_behaviors):
                behavior = enemy_behaviors[i]
                if hasattr(behavior, 'is_currently_invisible'):
                    is_invisible = behavior.is_currently_invisible()
            
            # NO PUEDE COLISIONAR SI ESTÁ INVISIBLE
            if not is_invisible:
                return True
    
    return False

def draw_ui():
    """Dibuja la interfaz de usuario temática infernal"""
    ui_y = MAZE_HEIGHT * TILE_SIZE + 10
    
    # Información del nivel con tema infernal
    level_info = f"Dimensión: {current_level + 1} - {levels[current_level]['name']}"
    level_text = small_font.render(level_info, True, COLOR_BONUS)
    screen.blit(level_text, (10, ui_y))
    
    # Puntuación de almas
    score_text = small_font.render(f"Almas Recolectadas: {player_score}", True, COLOR_TEXT)
    screen.blit(score_text, (10, ui_y + 25))
    
    # NUEVO: Estado de diamantes (OBLIGATORIOS)
    diamonds_remaining = total_diamonds - collected_diamonds
    if diamonds_remaining > 0:
        diamond_color = (255, 100, 100)  # Rojo si faltan diamantes
        diamond_status = f"💎 DIAMANTES REQUERIDOS: {collected_diamonds}/{total_diamonds} (faltan {diamonds_remaining}) - 🔒 PUERTA CERRADA"
    else:
        diamond_color = (100, 255, 100)  # Verde si están completos
        diamond_status = f"💎 DIAMANTES COMPLETOS: {collected_diamonds}/{total_diamonds} ✅ - 🚪 PUERTA ABIERTA"
    
    diamond_text = small_font.render(diamond_status, True, diamond_color)
    screen.blit(diamond_text, (10, ui_y + 50))
    
    # Vidas como corazones ardientes
    hearts = '💖' * player_lives
    lives_text = small_font.render(f"Vida: {hearts}", True, COLOR_FIRE)
    screen.blit(lives_text, (200, ui_y))
    
    # Información de criaturas infernales con estado de invisibilidad
    enemy_count = len(enemies)
    enemy_types_current = []
    invisible_count = 0
    
    for i, e in enumerate(enemies):
        enemy_type = e['type']
        # Verificar si está invisible
        if enemy_type == '👻' and i < len(enemy_behaviors):
            behavior = enemy_behaviors[i]
            if hasattr(behavior, 'is_currently_invisible') and behavior.is_currently_invisible():
                invisible_count += 1
                enemy_types_current.append('💨')  # Usar humo para representar invisibilidad
            else:
                enemy_types_current.append(enemy_type)
        else:
            enemy_types_current.append(enemy_type)
    
    enemy_info = f"Demonios: {enemy_count} {''.join(enemy_types_current) if enemy_types_current else ''}"
    if invisible_count > 0:
        enemy_info += f" ({invisible_count} invisible{'s' if invisible_count > 1 else ''})"
    
    enemy_text = small_font.render(enemy_info, True, COLOR_FIRE)
    screen.blit(enemy_text, (200, ui_y + 25))
    
    # Información de aim bot infernal
    aim_status = "🎯 PROYECTIL GUIADO: ON" if aim_bot.aim_assistance else "🎯 PROYECTIL GUIADO: OFF"
    aim_color = COLOR_FIRE if aim_bot.aim_assistance else (100, 100, 100)
    aim_text = small_font.render(aim_status, True, aim_color)
    screen.blit(aim_text, (400, ui_y + 25))
    
    # MEJORADO: Información de proyectiles
    projectile_info = f"💩 Proyectiles: {len(projectiles)}/3 (Velocidad: 2x)"
    projectile_color = COLOR_FIRE if len(projectiles) < 3 else (255, 100, 100)
    projectile_text = small_font.render(projectile_info, True, projectile_color)
    screen.blit(projectile_text, (400, ui_y + 50))
    
    # Información de controles infernales
    control_info = []
    if controller_connected:
        control_info = [
            f"🎮 CONTROL XBOX 360 | {levels[current_level]['difficulty']} | {FPS} FPS",
            f"🕹️ Joystick/D-pad=mover | A=disparar (MEJORADO) | B=salir"
        ]
    else:
        control_info = [
            f"⌨️ SOLO TECLADO | {levels[current_level]['difficulty']} | {FPS} FPS",
            f"🔄 Flechas=mover | ESPACIO=disparar (MEJORADO) | A=guiado | ESC=salir"
        ]
    
    for i, line in enumerate(control_info):
        info_color = COLOR_FIRE if controller_connected else COLOR_TEXT
        info_text = small_font.render(line, True, info_color)
        screen.blit(info_text, (400, ui_y + 70 + i * 20))

def show_message(message):
    # Crear superficie temporal para el mensaje
    temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    temp_surface.fill(COLOR_BACKGROUND)
    
    # Dibujar el mensaje
    text = font.render(message, True, COLOR_TEXT)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    temp_surface.blit(text, text_rect)
    
    # Mostrar en pantalla
    screen.blit(temp_surface, (0, 0))
    pygame.display.flip()
    time.sleep(1.5)

def next_level():
    global current_level, maze, player_pos, enemies, projectiles, game_state, pathfinder, screen
    global total_diamonds, collected_diamonds
    
    current_level += 1
    if current_level < len(levels):
        # Actualizar laberinto
        maze = levels[current_level]['maze']
        update_maze_dimensions()
        
        # IMPORTANTE: Reinicializar pathfinder ANTES de generar enemigos
        pathfinder = AStar(maze)
        
        # Resetear posición del jugador y proyectiles
        player_pos = [1, 1]
        projectiles = []
        
        # Generar enemigos DESPUÉS de inicializar pathfinder (esto también resetea diamantes)
        reset_enemies()
        
        show_message(f"🔥 {levels[current_level]['name']} 🔥")
        show_message(f"💎 Nuevo nivel: {total_diamonds} diamantes requeridos 💎")
        show_message(f"🚪 Encuentra la puerta infernal para continuar 🚪")
    else:
        show_message(f"🏆 ¡Has conquistado todas las dimensiones infernales! 🏆")
        show_message(f"💎 Almas recolectadas: {player_score} 💎")
        reset_game()
        reset_menu()  # ASEGURAR menú limpio
        game_state = STATE_MENU

# Inicialización
clock = pygame.time.Clock()
initialize_enemy_behaviors()

# Loop principal
running = True
while running:
    # NUEVO: Leer inputs del control al inicio del loop
    controller_move = get_controller_movement()
    controller_a_menu = get_controller_button_a_menu()
    controller_b = get_controller_button_b()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # NUEVO: Detectar conexión/desconexión de controles
        elif event.type == pygame.JOYDEVICEADDED:
            print("🎮 Control conectado!")
            init_controller()
        elif event.type == pygame.JOYDEVICEREMOVED:
            print("🚫 Control desconectado!")
            controller_connected = False
        
        if event.type == pygame.KEYDOWN:
            # Manejo ESTRICTO del menú (SOLO 3 opciones válidas)
            if game_state == STATE_MENU:
                # Limitar navegación a SOLO 3 opciones
                if event.key == pygame.K_UP:
                    menu_idx = (menu_idx - 1) % 3  # MÁXIMO 3 opciones
                elif event.key == pygame.K_DOWN:
                    menu_idx = (menu_idx + 1) % 3  # MÁXIMO 3 opciones
                elif event.key == pygame.K_RETURN:
                    # Manejo DIRECTO por índice (sin referencias a strings)
                    if menu_idx == 0:  # Nueva Partida
                        reset_game()
                        update_maze_dimensions()
                        game_state = STATE_PLAY
                    elif menu_idx == 1:  # Seleccionar Dificultad
                        game_state = STATE_DIFF
                    elif menu_idx == 2:  # Salir
                        running = False
            
            elif game_state == STATE_DIFF:
                if event.key == pygame.K_UP:
                    diff_idx = (diff_idx - 1) % len(difficulty_options)
                elif event.key == pygame.K_DOWN:
                    diff_idx = (diff_idx + 1) % len(difficulty_options)
                elif event.key == pygame.K_RETURN:
                    FPS = FPS_levels[difficulty_options[diff_idx]]
                    reset_menu()  # ASEGURAR menú limpio
                    game_state = STATE_MENU
                elif event.key == pygame.K_ESCAPE:
                    reset_menu()  # ASEGURAR menú limpio
                    game_state = STATE_MENU
    
    # NUEVO: Manejar navegación con control en menús
    if game_state == STATE_MENU:
        # Navegación con joystick/D-pad
        if abs(controller_move[1]) > 0.5:  # Movimiento vertical significativo
            if controller_move[1] < 0:  # Arriba
                menu_idx = (menu_idx - 1) % 3
            else:  # Abajo
                menu_idx = (menu_idx + 1) % 3
            time.sleep(0.15)  # Pequeña pausa para evitar navegación muy rápida
        
        # Aceptar con botón A
        if controller_a_menu:
            if menu_idx == 0:  # Nueva Partida
                reset_game()
                update_maze_dimensions()
                game_state = STATE_PLAY
            elif menu_idx == 1:  # Seleccionar Dificultad
                game_state = STATE_DIFF
            elif menu_idx == 2:  # Salir
                running = False
        
        draw_menu()
        
    elif game_state == STATE_DIFF:
        # Navegación con joystick/D-pad
        if abs(controller_move[1]) > 0.5:  # Movimiento vertical significativo
            if controller_move[1] < 0:  # Arriba
                diff_idx = (diff_idx - 1) % len(difficulty_options)
            else:  # Abajo
                diff_idx = (diff_idx + 1) % len(difficulty_options)
            time.sleep(0.15)  # Pequeña pausa para evitar navegación muy rápida
        
        # Aceptar con botón A
        if controller_a_menu:
            FPS = FPS_levels[difficulty_options[diff_idx]]
            reset_menu()  # ASEGURAR menú limpio
            game_state = STATE_MENU
        
        # Retroceder con botón B
        if controller_b:
            reset_menu()  # ASEGURAR menú limpio
            game_state = STATE_MENU
        
        draw_difficulty_menu()
        
    elif game_state == STATE_PLAY:
        # Controles del jugador - TECLADO + CONTROL XBOX 360
        keys = pygame.key.get_pressed()
        new_pos = player_pos.copy()
        
        # NUEVO: Leer input del control Xbox 360
        controller_shoot = get_controller_shoot()  # Ahora usa botón A
        
        # Variables para direcciones
        move_x, move_y = 0, 0
        shoot_direction = None
        
        # TECLADO: Movimiento con flechas
        if keys[pygame.K_UP]:
            move_y = -1
            current_direction = 'up'
        elif keys[pygame.K_DOWN]:
            move_y = 1
            current_direction = 'down'
        elif keys[pygame.K_LEFT]:
            move_x = -1
            current_direction = 'left'
        elif keys[pygame.K_RIGHT]:
            move_x = 1
            current_direction = 'right'
        
        # CONTROL: Movimiento con joystick/D-pad (tiene prioridad sobre teclado)
        if controller_connected and (abs(controller_move[0]) > 0 or abs(controller_move[1]) > 0):
            # Normalizar movimiento del control
            norm_move = normalize_direction(controller_move[0], controller_move[1])
            move_x, move_y = norm_move[0], norm_move[1]
            
            # Actualizar dirección del sprite
            if move_x > 0:
                current_direction = 'right'
            elif move_x < 0:
                current_direction = 'left'
            elif move_y < 0:
                current_direction = 'up'
            elif move_y > 0:
                current_direction = 'down'
        
        # Aplicar movimiento
        if move_x != 0 or move_y != 0:
            new_pos[0] += move_x
            new_pos[1] += move_y
            last_direction = [move_x, move_y]
        
        # Verificar movimiento válido
        if (0 <= new_pos[0] < MAZE_WIDTH and 0 <= new_pos[1] < MAZE_HEIGHT and 
            maze[new_pos[1]][new_pos[0]] != 1):
            
            # Manejar bonificaciones
            handle_bonus_tile(new_pos[0], new_pos[1])
            player_pos = new_pos
        
        # Asegurar dirección válida para disparar
        ensure_valid_shooting_direction()
        
        # MEJORADO: Sistema de disparo más responsivo
        can_shoot = len(projectiles) < 3  # REDUCIDO de 5 a 3 para mejor responsividad
        
        # TECLADO: Disparo con ESPACIO (con debounce mejorado)
        current_space_pressed = keys[pygame.K_SPACE]
        keyboard_shoot = current_space_pressed and not last_space_state
        last_space_state = current_space_pressed
        
        if (controller_shoot or keyboard_shoot) and can_shoot:
            # Determinar dirección de disparo (SOLO 4 direcciones como antes)
            shoot_direction = last_direction.copy()  # Usar última dirección de movimiento
            
            # Obtener dirección de aim bot si está activo
            aim_direction = aim_bot.get_aim_direction(player_pos, enemies)
            
            if aim_direction:
                # Usar aim bot
                projectiles.append({'pos': player_pos.copy(), 'dir': aim_direction})
                print(f"🎯 Proyectil GUIADO creado: {aim_direction}")
            else:
                # Disparo normal (4 direcciones: arriba, abajo, izquierda, derecha)
                projectiles.append({'pos': player_pos.copy(), 'dir': shoot_direction})
                print(f"💥 Proyectil RÁPIDO creado: {shoot_direction}")
            
            print(f"📊 Proyectiles activos: {len(projectiles)}/3")
        elif (controller_shoot or keyboard_shoot) and not can_shoot:
            print("⚠️ Máximo de proyectiles alcanzado (3/3)")
        
        # Toggle aim bot (solo teclado)
        if keys[pygame.K_a]:
            aim_bot.aim_assistance = not aim_bot.aim_assistance
            time.sleep(0.3)  # Evitar toggle múltiple
        
        # Recargar sprites si se presiona R
        if keys[pygame.K_r]:
            print("🔄 Recargando sprites...")
            reload_sprites_if_needed()
            show_message("¡Sprites recargados!")
        
        # Debug del control (presiona D)
        if keys[pygame.K_d]:
            debug_controller_state()
            time.sleep(0.5)  # Evitar spam
        
        # MEJORADO: Verificar llegada a la salida con puertas visibles
        if maze[player_pos[1]][player_pos[0]] == 2:
            if collected_diamonds >= total_diamonds:
                print(f"🚪 ¡Portal abierto! Avanzando al siguiente nivel...")
                next_level()
            else:
                remaining = total_diamonds - collected_diamonds
                show_temp_message(f"🔒 ¡Faltan {remaining} diamantes! La puerta está cerrada")
        
        # Actualizar enemigos y proyectiles
        move_enemies()
        move_projectiles()  # Ahora más rápidos
        
        # Verificar colisiones
        if check_enemy_collision():
            player_lives -= 1
            player_pos = [1, 1]
            reset_enemies()
            projectiles = []
            
            # NUEVO: Limpiar mensaje temporal
            temp_message = ""
            temp_message_time = 0
            last_button_a_state = False
            last_button_b_state = False
            last_space_state = False
            
            if player_lives <= 0:
                show_message(f"💀 Tu alma ha sido devorada 💀")
                show_message(f"🔥 Almas perdidas: {player_score} 🔥")
                reset_game()
                reset_menu()  # ASEGURAR menú limpio
                game_state = STATE_MENU
            else:
                show_message(f"😈 ¡Los demonios te han atrapado! Vida restante: {player_lives} 💖")
        
        # Dibujar todo
        screen.fill(COLOR_BACKGROUND)
        draw_maze()  # Ahora con puertas más visibles
        draw_player()
        draw_enemies()  # Ya no dibuja fantasmas invisibles
        draw_projectiles()
        draw_aim_bot_indicators()
        draw_ui()  # UI mejorada
        draw_temp_message()  # NUEVO: Dibujar mensaje temporal

        # NUEVO: Salir del juego también con botón B del control
        if keys[pygame.K_ESCAPE] or controller_b:
            # NUEVO: Limpiar mensaje temporal y estados de control al salir
            temp_message = ""
            temp_message_time = 0
            last_button_a_state = False
            last_button_b_state = False
            last_space_state = False
            reset_menu()  # ASEGURAR menú limpio
            game_state = STATE_MENU
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()