print("🎮 Sistema de auto-escalado activado - Laberinto grande y visible")
print("🖼️ Ventana optimizada con laberinto de tamaño perfecto")
print("💡 Controles de tamaño:")
print("   - F11: Pantalla completa")
print("   - +/-: Ajustar tamaño del laberinto")
print("🎯 Laberinto optimizado para máxima visibilidad")
print("")

# ========================================
# DIMENSIONES INFERNALES - SISTEMA AVANZADO CON IA Y SPRITES
# ========================================
# Estudiante: Alan Alberto Martinez Ubiera
# Matrícula: 23-EISN-2-062
# Email: aalann34@gmail.com
# Universidad: Universidad O&M
# Materia: Inteligencia Artificial
# Profesor: Yoel Andeyci Pilier Martínez
# Fecha: 5 de Julio, 2025
# ========================================

import pygame
import sys
import random
import time
import math
from scripts import AStar, create_enemy_behavior

# Inicializar Pygame
pygame.init()

# Inicializar sistema de audio
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Inicializar sistema de joysticks/controles
pygame.joystick.init()

# Variable de pantalla completa
fullscreen_mode = False

# Sistema de control Xbox 360
controller = None
controller_connected = False
last_button_a_state = False
last_button_b_state = False
last_space_state = False

def init_controller():
    """Inicializa el control Xbox 360"""
    global controller, controller_connected
    
    joystick_count = pygame.joystick.get_count()
    
    if joystick_count > 0:
        controller = pygame.joystick.Joystick(0)
        controller.init()
        controller_connected = True
        print(f"🎮 Control detectado: {controller.get_name()}")
        print(f"🕹️ Ejes: {controller.get_numaxes()}")
        print(f"🔘 Botones: {controller.get_numbuttons()}")
        
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
        stick_x = controller.get_axis(0)
        stick_y = controller.get_axis(1)
        
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
            return [hat_x, -hat_y]
        else:
            return [stick_x, stick_y]
            
    except Exception as e:
        print(f"Error leyendo control: {e}")
        return [0, 0]

def get_controller_shoot():
    """Detecta si se presiona el botón A para disparar"""
    global last_button_a_state
    
    if not controller_connected:
        return False
    
    try:
        button_a_pressed = controller.get_button(0)
        
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

def get_controller_button_b():
    """Detecta si se presiona el botón B para navegación"""
    global last_button_b_state
    
    if not controller_connected:
        return False
    
    try:
        button_b_pressed = controller.get_button(1)
        
        if button_b_pressed and not last_button_b_state:
            last_button_b_state = True
            return True
        elif not button_b_pressed:
            last_button_b_state = False
            
        return False
    except Exception as e:
        return False

def get_controller_button_a_menu():
    """Detecta si se presiona el botón A para navegación en menús"""
    global last_button_a_state
    
    if not controller_connected:
        return False
    
    try:
        button_a_pressed = controller.get_button(0)
        
        if button_a_pressed and not last_button_a_state:
            last_button_a_state = True
            return True
        elif not button_a_pressed:
            last_button_a_state = False
            
        return False
    except Exception as e:
        return False

def normalize_direction(dx, dy):
    """Normaliza una dirección a 4 direcciones cardinales"""
    if dx == 0 and dy == 0:
        return [0, 0]
    
    if abs(dx) > abs(dy):
        if dx > 0:
            return [1, 0]  # Derecha
        else:
            return [-1, 0]  # Izquierda
    else:
        if dy > 0:
            return [0, 1]  # Abajo
        else:
            return [0, -1]  # Arriba

def ensure_valid_shooting_direction():
    """Asegura que siempre haya una dirección válida para disparar"""
    global last_direction, current_direction
    
    if last_direction == [0, 0] or last_direction is None:
        if current_direction == 'up':
            last_direction = [0, -1]
        elif current_direction == 'down':
            last_direction = [0, 1]
        elif current_direction == 'left':
            last_direction = [-1, 0]
        elif current_direction == 'right':
            last_direction = [1, 0]
        else:
            last_direction = [1, 0]
            current_direction = 'right'
    
    if last_direction[0] == 0 and last_direction[1] == 0:
        last_direction = [1, 0]
        print("🔧 Dirección de disparo corregida: derecha")

# ========================================
# SISTEMA DE AUTO-ESCALADO INTELIGENTE
# ========================================

def detect_screen_resolution():
    """Detecta la resolución de pantalla y calcula dimensiones óptimas"""
    display_info = pygame.display.Info()
    desktop_width = display_info.current_w
    desktop_height = display_info.current_h
    
    print(f"🖥️ Resolución detectada: {desktop_width}x{desktop_height}")
    
    base_width = 1920
    base_height = 1080
    
    scale_factor_w = desktop_width / base_width
    scale_factor_h = desktop_height / base_height
    scale_factor = min(scale_factor_w, scale_factor_h)
    
    scale_factor = max(0.5, min(scale_factor, 2.0))
    
    print(f"📐 Factor de escala calculado: {scale_factor:.2f}")
    
    return scale_factor, desktop_width, desktop_height

def calculate_optimal_dimensions(scale_factor, desktop_width, desktop_height):
    """Calcula dimensiones óptimas para el juego"""
    
    base_tile_size = 50
    tile_size = int(base_tile_size * scale_factor)
    tile_size = max(40, min(tile_size, 80))
    
    if desktop_width >= 1920:
        tile_size = max(tile_size, 55)
    if desktop_width >= 2560:
        tile_size = max(tile_size, 65)
    
    maze_width = 24
    maze_height = 14
    
    min_game_width = maze_width * tile_size
    min_game_height = maze_height * tile_size + 120
    
    max_window_width = int(desktop_width * 0.85)
    max_window_height = int(desktop_height * 0.90)
    
    min_window_width = max(1200, min_game_width)  
    min_window_height = max(800, min_game_height)  
    
    window_width = max(min_window_width, min(max_window_width, min_game_width + 200))
    window_height = max(min_window_height, min(max_window_height, min_game_height + 100))
    
    print(f"🎮 Dimensiones calculadas:")
    print(f"   - Tamaño de celda: {tile_size}px")
    print(f"   - Laberinto: {min_game_width}x{min_game_height - 120}px")
    print(f"   - Ventana: {window_width}x{window_height}")
    
    return tile_size, window_width, window_height, maze_width, maze_height

# Detectar resolución y calcular dimensiones automáticamente
scale_factor, desktop_width, desktop_height = detect_screen_resolution()
TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, MAZE_WIDTH, MAZE_HEIGHT = calculate_optimal_dimensions(
    scale_factor, desktop_width, desktop_height
)

# Configuración de la pantalla
SCREEN_WIDTH = WINDOW_WIDTH
SCREEN_HEIGHT = WINDOW_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🔥 Dimensiones Infernales - Sistema de IA Avanzado")

# Maximizar ventana automáticamente
import os
maximized_successfully = False

try:
    if os.name == 'nt':  # Windows
        import pygame._sdl2
        window = pygame._sdl2.Window.from_display_module()
        window.maximize()
        maximized_successfully = True
        print("🖼️ Ventana maximizada automáticamente")
        SCREEN_WIDTH = screen.get_width()
        SCREEN_HEIGHT = screen.get_height()
        print(f"📐 Nueva resolución: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
except:
    print("⚠️ No se pudo maximizar automáticamente, usando ventana grande")

# Fallback si no se pudo maximizar
if not maximized_successfully:
    fallback_width = min(1400, int(desktop_width * 0.85))
    fallback_height = min(900, int(desktop_height * 0.85))
    screen = pygame.display.set_mode((fallback_width, fallback_height))
    SCREEN_WIDTH = fallback_width
    SCREEN_HEIGHT = fallback_height
    print(f"🖼️ Ventana grande creada: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

def adjust_tile_size(increase=True):
    """Ajusta el tamaño del laberinto dinámicamente"""
    global TILE_SIZE, emoji_font, emoji_font_size
    
    old_size = TILE_SIZE
    
    if increase:
        TILE_SIZE = min(TILE_SIZE + 5, 120)
        action = "aumentado"
    else:
        TILE_SIZE = max(TILE_SIZE - 5, 30)
        action = "reducido"
    
    if TILE_SIZE != old_size:
        emoji_font_size = int(TILE_SIZE * 0.8)
        emoji_font = pygame.font.SysFont('Segoe UI Emoji', emoji_font_size)
        
        print(f"🔧 Tamaño de laberinto {action}: {old_size}px → {TILE_SIZE}px")
        show_temp_message(f"Laberinto {action}: {TILE_SIZE}px")
    else:
        limit = "máximo" if increase else "mínimo"
        print(f"⚠️ Tamaño {limit} alcanzado: {TILE_SIZE}px")
        show_temp_message(f"Tamaño {limit}: {TILE_SIZE}px")

# Configuración de fuentes escaladas automáticamente
pygame.font.init()
base_font_size = max(20, int(26 * scale_factor))
small_font_size = max(16, int(20 * scale_factor))
emoji_font_size = max(18, int(TILE_SIZE * 0.8))

font = pygame.font.SysFont('Arial', base_font_size)
small_font = pygame.font.SysFont('Arial', small_font_size)
emoji_font = pygame.font.SysFont('Segoe UI Emoji', emoji_font_size)

print(f"✅ Configuración de pantalla:")
print(f"   - Resolución de escritorio: {desktop_width}x{desktop_height}")
print(f"   - Tamaño de ventana inicial: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
print(f"   - Factor de escala: {scale_factor:.2f}")
print(f"   - Tamaño de fuente principal: {base_font_size}px")
print(f"   - Tamaño de celda del juego: {TILE_SIZE}px")

def toggle_fullscreen():
    """Función para alternar entre pantalla completa y modo ventana"""
    global fullscreen_mode, screen, SCREEN_WIDTH, SCREEN_HEIGHT, scale_factor
    global font, small_font, emoji_font, base_font_size, small_font_size, emoji_font_size
    
    if fullscreen_mode:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        fullscreen_mode = False
        SCREEN_WIDTH = WINDOW_WIDTH
        SCREEN_HEIGHT = WINDOW_HEIGHT
        print(f"🖼️ Modo ventana: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        fullscreen_mode = True
        SCREEN_WIDTH = screen.get_width()
        SCREEN_HEIGHT = screen.get_height()
        
        scale_factor = min(SCREEN_WIDTH / 1920, SCREEN_HEIGHT / 1080)
        scale_factor = max(0.5, min(scale_factor, 3.0))
        
        base_font_size = max(20, int(30 * scale_factor))
        small_font_size = max(16, int(22 * scale_factor))
        emoji_font_size = max(20, int(TILE_SIZE * 0.9))
        
        font = pygame.font.SysFont('Arial', base_font_size)
        small_font = pygame.font.SysFont('Arial', small_font_size)
        emoji_font = pygame.font.SysFont('Segoe UI Emoji', emoji_font_size)
        
        print(f"🖥️ Pantalla completa: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

# Intentar inicializar control al inicio
init_controller()

# ========================================
# NIVELES DEL JUEGO
# ========================================

levels = [
    # NIVEL 1 - Portal de Entrada
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
            [1,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
            [1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
            [1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,0,1,1,0,0,0,1,1,0,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,1,0,0,3,0,0,1,0,0,0,0,0,0,3,0,1],
            [1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,1,1,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    },

    # NIVEL 2 - Cámaras de Tormento
    {
        'id': 2,
        'name': 'Cámaras de Tormento',
        'difficulty': 'Iniciado',
        'description': 'Los gritos resuenan en estas cámaras malditas',
        'maze': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,3,1],
            [1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,0,1,0,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
            [1,0,1,1,1,1,1,1,0,1,0,1,0,1,0,1,1,1,1,1,0,1,0,1],
            [1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,1],
            [1,1,1,1,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,0,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1,1,1],
            [1,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,3,0,1],
            [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    },

    # NIVEL 3 - Laberinto de Fuego
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
            [1,0,0,0,1,0,0,0,0,0,0,3,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,0,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,1,0,1,0,1],
            [1,0,1,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,1,0,1],
            [1,0,1,1,1,1,1,1,1,0,1,0,1,0,1,1,1,1,1,1,1,1,0,1],
            [1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,1],
            [1,0,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    },

    # NIVEL 4 - Fortaleza Demoníaca
    {
        'id': 4,
        'name': 'Fortaleza Demoníaca',
        'difficulty': 'Veterano',
        'description': 'El corazón del mal late en esta fortaleza',
        'maze': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,3,1],
            [1,0,1,0,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,0,1,1,0,1],
            [1,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,1],
            [1,0,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,0,1,1],
            [1,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
            [1,1,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,1,3,1,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,0,1,1,1,0,1,0,1,0,1,0,1,0,1,1,1,0,1,1,1,1],
            [1,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
            [1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,1,0,1],
            [1,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,3,1],
            [1,3,1,0,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,0,1,1,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    },

    # NIVEL 5 - Trono de Lucifer
    {
        'id': 5,
        'name': 'Trono de Lucifer',
        'difficulty': 'Señor Infernal',
        'description': 'El mismísimo trono del príncipe de las tinieblas',
        'maze': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,3,1],
            [1,0,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
            [1,0,1,0,1,1,1,1,0,1,0,1,0,1,0,1,1,1,1,1,0,1,0,1],
            [1,3,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,1,1,0,1,0,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1],
            [1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,0,1,1,0,1,0,1,1,0,1,0,1,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,1,0,0,3,0,0,1,0,0,0,0,0,0,1,0,1],
            [1,0,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,0,1,0,1],
            [1,0,0,0,1,0,0,0,0,0,1,3,1,0,0,0,0,0,0,1,0,3,0,1],
            [1,1,1,0,1,0,1,1,1,0,1,0,1,0,1,1,1,1,0,1,0,1,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    }
]

# Colores del juego - Tema infernal
COLOR_WALL = (20, 0, 0)
COLOR_PATH = (80, 40, 40)
COLOR_BACKGROUND = (0, 0, 0)
COLOR_PLAYER = (255, 255, 0)
COLOR_EXIT = (255, 100, 0)
COLOR_ENEMY = (255, 0, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_AIMBOT = (255, 255, 0)
COLOR_BONUS = (255, 215, 0)
COLOR_FIRE = (255, 69, 0)
COLOR_LAVA = (139, 0, 0)

# Estados del juego
STATE_MENU = 'MENU'
STATE_DIFF = 'DIFFICULTY'
STATE_PLAY = 'PLAY'

# Opciones de menú
menu_options = ['Nueva Partida', 'Seleccionar Dificultad', 'Salir']
difficulty_options = ['Fácil', 'Medio', 'Difícil']
FPS_levels = {'Fácil': 5, 'Medio': 7, 'Difícil': 9}

# Variables del menú
menu_idx = 0
diff_idx = 1
game_state = STATE_MENU
FPS = FPS_levels[difficulty_options[diff_idx]]

def reset_menu():
    global menu_idx
    menu_idx = 0

# Variables para sprites
use_sprites = False
dog_sprites = {}
enemy_sprites = {}
poop_sprite = None
cover_image = None
wall_sprite = None
heart_sprite = None
diamond_sprite = None
door_sprite = None
humo_sprite = None
fire_sprite = None
current_direction = 'right'

# ========================================
# SISTEMA DE AUDIO
# ========================================

sounds = {}
music_loaded = False
audio_enabled = True
music_paths = {}

def load_sound(filename, sound_name):
    """Carga un sonido específico"""
    global sounds
    sound_path = f'assets/sounds/{filename}'
    
    try:
        import os
        if os.path.exists(sound_path):
            sound = pygame.mixer.Sound(sound_path)
            sounds[sound_name] = sound
            print(f"🔊 Sonido cargado: {filename}")
            return True
        else:
            print(f"🔇 Sonido no encontrado: {sound_path}")
            return False
    except Exception as e:
        print(f"❌ Error cargando sonido {filename}: {e}")
        return False

def load_music(filename, music_name):
    """Carga música de fondo"""
    music_path = f'assets/music/{filename}'
    
    try:
        import os
        if os.path.exists(music_path):
            print(f"🎵 Música encontrada: {filename}")
            return music_path
        else:
            print(f"🔇 Música no encontrada: {music_path}")
            return None
    except Exception as e:
        print(f"❌ Error verificando música {filename}: {e}")
        return None

def play_sound(sound_name, volume=0.7):
    """Reproduce un sonido específico"""
    if audio_enabled and sound_name in sounds:
        try:
            sound = sounds[sound_name]
            sound.set_volume(volume)
            sound.play()
            if sound_name in ['diamante', 'muerte']:
                print(f"🔊 SONIDO: {sound_name}.wav reproducido")
        except Exception as e:
            print(f"❌ Error reproduciendo sonido {sound_name}: {e}")

def play_music(music_path, loop=-1, volume=0.5):
    """Reproduce música de fondo"""
    if audio_enabled and music_path:
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loop)
        except Exception as e:
            print(f"❌ Error reproduciendo música: {e}")

def stop_music():
    """Detiene la música de fondo"""
    try:
        pygame.mixer.music.stop()
    except:
        pass

def load_all_audio():
    """Carga todos los recursos de audio del juego"""
    global music_loaded, music_paths
    
    print("🎵 Cargando recursos de audio...")

    sounds_to_load = [
        ('disparo.wav', 'disparo'),
        ('diamante.wav', 'diamante'),
        ('puerta.wav', 'puerta'),
        ('muerte.wav', 'muerte'),
        ('click.wav', 'click'),
        ('fantasma.wav', 'fantasma'),
        ('teletransporte.wav', 'teletransporte')
    ]

    sounds_loaded = 0
    for filename, sound_name in sounds_to_load:
        if load_sound(filename, sound_name):
            sounds_loaded += 1

    print("🎵 Buscando archivos de música...")

    music_checks = [
        ('menu.mp3', 'menu', 'Música del menú principal'),
        ('juego.mp3', 'game', 'Música durante el gameplay'),
        ('victoria.mp3', 'victory', 'Música de victoria'),
        ('derrota.mp3', 'defeat', 'Música de derrota')
    ]

    music_count = 0
    for filename, key, description in music_checks:
        music_path = load_music(filename, key)
        music_paths[key] = music_path
        if music_path:
            music_count += 1
            print(f"   ✅ {description}: {filename}")
        else:
            print(f"   ❌ {description}: {filename} NO ENCONTRADO")

    if sounds_loaded > 0:
        print(f"🔊 SONIDOS: {sounds_loaded}/{len(sounds_to_load)} cargados")
    else:
        print("⚠️ SONIDOS: No se cargaron efectos de sonido")

    if music_count > 0:
        print(f"🎵 MÚSICA: {music_count}/4 pistas encontradas")
        music_loaded = True

        if music_paths['menu']:
            print("🎵 Iniciando música del menú...")
            play_music(music_paths['menu'], volume=0.3)
    else:
        print("⚠️ MÚSICA: No se encontraron archivos de música")

    return sounds_loaded, music_count

# Cargar audio al inicio
sounds_count, music_count = load_all_audio()

print("")
print("📊 ESTADO DEL AUDIO:")
if music_count == 4:
    print("✅ MÚSICA: Completa - Todas las pistas cargadas")
else:
    print(f"⚠️ MÚSICA: {music_count}/4 pistas cargadas")

if sounds_count > 0:
    print(f"✅ SONIDOS: {sounds_count}/7 efectos cargados")
else:
    print("⚠️ SONIDOS: Pendientes")

# ========================================
# SISTEMA DE AIM BOT
# ========================================

class AimBot:
    """Sistema de aim bot inteligente"""
    
    def __init__(self, detection_range=6):
        self.detection_range = detection_range
        self.aim_assistance = True
        self.target_enemy = None
        
    def find_nearest_enemy(self, player_pos, enemies):
        """Encuentra el enemigo más cercano"""
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
        
        if abs(dx) > abs(dy):
            return [1 if dx > 0 else -1, 0]
        else:
            return [0, 1 if dy > 0 else -1]
    
    def get_aim_direction(self, player_pos, enemies):
        """Obtiene la dirección de disparo asistido"""
        if not self.aim_assistance:
            return None
        
        if not enemies:
            return None
            
        nearest_enemy, distance = self.find_nearest_enemy(player_pos, enemies)
        
        if nearest_enemy and distance <= self.detection_range:
            self.target_enemy = nearest_enemy
            return self.calculate_aim_direction(player_pos, nearest_enemy['pos'])
        
        self.target_enemy = None
        return None

# Instancia global del aim bot
aim_bot = AimBot(detection_range=6)

# ========================================
# SISTEMA DE SPRITES
# ========================================

def load_dog_sprite():
    """Carga el sprite del héroe protagonista"""
    global use_sprites, dog_sprites
    
    sprite_path = 'assets/images/perro.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"✅ Sprite del héroe encontrado: {sprite_path}")
            
            dog_spritesheet = pygame.image.load(sprite_path)
            scaled_sprite = pygame.transform.scale(dog_spritesheet, (TILE_SIZE, TILE_SIZE))
            
            dog_sprites = {
                'up': [scaled_sprite],
                'right': [scaled_sprite], 
                'down': [scaled_sprite],
                'left': [pygame.transform.flip(scaled_sprite, True, False)]
            }
            
            use_sprites = True
            print(f"🎮 Sprite del héroe cargado: {TILE_SIZE}x{TILE_SIZE}")
            return True
        else:
            print(f"📁 No se encontró sprite en: {sprite_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error cargando sprite: {e}")
        return False

def load_enemy_sprites():
    """Carga sprites de enemigos"""
    global enemy_sprites
    
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
                print(f"👾 Cargando criatura: {sprite_path}")
                
                enemy_spritesheet = pygame.image.load(sprite_path)
                scaled_sprite = pygame.transform.scale(enemy_spritesheet, (TILE_SIZE, TILE_SIZE))
                
                enemy_sprites[emoji] = {
                    'right': scaled_sprite,
                    'left': pygame.transform.flip(scaled_sprite, True, False)
                }
                
                sprites_loaded += 1
                
        except Exception as e:
            print(f"⚠️ Error cargando {sprite_path}: {e}")
    
    if sprites_loaded > 0:
        print(f"🔥 {sprites_loaded} criaturas cargadas: {TILE_SIZE}x{TILE_SIZE}")
    
    return sprites_loaded > 0

def load_poop_sprite():
    """Carga el sprite de proyectil"""
    global poop_sprite
    
    sprite_path = 'assets/images/caca.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"💩 Sprite de proyectil encontrado")
            
            poop_image = pygame.image.load(sprite_path)
            poop_sprite = pygame.transform.scale(poop_image, (TILE_SIZE, TILE_SIZE))
            
            print(f"💩 Sprite de proyectil cargado: {TILE_SIZE}x{TILE_SIZE}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error cargando sprite de proyectil: {e}")
        return False

def load_cover_image():
    """Carga la portada del juego"""
    global cover_image
    
    sprite_path = 'assets/images/portada.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"🖼️ Portada encontrada")
            
            cover_raw = pygame.image.load(sprite_path)
            
            cover_width = int(SCREEN_WIDTH * 0.4)
            cover_height = int(cover_width * 0.75)
            
            cover_image = pygame.transform.scale(cover_raw, (cover_width, cover_height))
            
            print(f"🖼️ Portada escalada: {cover_width}x{cover_height}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error cargando portada: {e}")
        return False

def load_wall_sprite():
    """Carga el sprite de pared"""
    global wall_sprite
    
    sprite_path = 'assets/images/bloquerojo.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"🧱 Sprite de pared encontrado")
            
            wall_image = pygame.image.load(sprite_path)
            wall_sprite = pygame.transform.scale(wall_image, (TILE_SIZE, TILE_SIZE))
            
            print(f"🧱 Pared cargada: {TILE_SIZE}x{TILE_SIZE}")
            return True
        else:
            return False
            
    except Exception as e:
        return False

def load_heart_sprite():
    """Carga el sprite de corazón"""
    global heart_sprite
    
    sprite_path = 'assets/images/corazon.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"💖 Sprite de corazón encontrado")
            
            heart_image = pygame.image.load(sprite_path)
            heart_size = max(25, int(TILE_SIZE * 0.8))
            heart_sprite = pygame.transform.scale(heart_image, (heart_size, heart_size))
            
            print(f"💖 Corazón cargado: {heart_size}x{heart_size}")
            return True
        else:
            return False
            
    except Exception as e:
        return False

def load_diamond_sprite():
    """Carga el sprite de diamante"""
    global diamond_sprite
    
    sprite_path = 'assets/images/diamante.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"💎 Sprite de diamante encontrado")
            
            diamond_image = pygame.image.load(sprite_path)
            diamond_sprite = pygame.transform.scale(diamond_image, (TILE_SIZE, TILE_SIZE))
            
            print(f"💎 Diamante cargado: {TILE_SIZE}x{TILE_SIZE}")
            return True
        else:
            return False
            
    except Exception as e:
        return False

def load_door_sprite():
    """Carga el sprite de puerta"""
    global door_sprite
    
    sprite_path = 'assets/images/puerta.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"🚪 Sprite de puerta encontrado")
            
            door_image = pygame.image.load(sprite_path)
            door_sprite = pygame.transform.scale(door_image, (TILE_SIZE, TILE_SIZE))
            
            print(f"🚪 Puerta cargada: {TILE_SIZE}x{TILE_SIZE}")
            return True
        else:
            return False
            
    except Exception as e:
        return False

def load_fire_sprite():
    """Carga el sprite de fuego"""
    global fire_sprite
    
    sprite_path = 'assets/images/fuego.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"🔥 Sprite de fuego encontrado")
            
            fire_image = pygame.image.load(sprite_path)
            fire_sprite = pygame.transform.scale(fire_image, (TILE_SIZE, TILE_SIZE))
            
            print(f"🔥 Fuego cargado: {TILE_SIZE}x{TILE_SIZE}")
            return True
        else:
            return False
            
    except Exception as e:
        return False

def load_humo_sprite():
    """Carga el sprite de humo"""
    global humo_sprite
    
    sprite_path = 'assets/images/humo.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"💨 Sprite de humo encontrado")
            
            humo_image = pygame.image.load(sprite_path)
            humo_sprite = pygame.transform.scale(humo_image, (TILE_SIZE, TILE_SIZE))
            
            print(f"💨 Humo cargado: {TILE_SIZE}x{TILE_SIZE}")
            return True
        else:
            return False
            
    except Exception as e:
        return False

def load_all_sprites():
    """Carga automáticamente todos los sprites"""
    print("")
    print("🎨 CARGANDO SPRITES:")
    
    sprites_loaded = 0
    total_sprites = 10
    
    if load_dog_sprite():
        sprites_loaded += 1
    if load_enemy_sprites():
        sprites_loaded += 1  
    if load_poop_sprite():
        sprites_loaded += 1
    if load_cover_image():
        sprites_loaded += 1
    if load_wall_sprite():
        sprites_loaded += 1
    if load_heart_sprite():
        sprites_loaded += 1
    if load_diamond_sprite():
        sprites_loaded += 1
    if load_door_sprite():
        sprites_loaded += 1
    if load_humo_sprite():
        sprites_loaded += 1
    if load_fire_sprite():
        sprites_loaded += 1
    
    print(f"")
    print(f"🎨 SPRITES CARGADOS: {sprites_loaded}/{total_sprites}")
    if sprites_loaded > 5:
        print("✅ Sprites principales cargados correctamente")
    else:
        print("⚠️ Algunos sprites no se encontraron - El juego usará emojis como respaldo")
    
    return sprites_loaded

# Cargar todos los sprites automáticamente
sprites_loaded_count = load_all_sprites()

def reload_sprites_if_needed():
    """Recarga sprites si es necesario"""
    global use_sprites
    if not use_sprites:
        load_dog_sprite()
    
    load_enemy_sprites()
    
    if poop_sprite is None:
        load_poop_sprite()
    
    if cover_image is None:
        load_cover_image()
    
    if wall_sprite is None:
        load_wall_sprite()
    
    if heart_sprite is None:
        load_heart_sprite()
    
    if diamond_sprite is None:
        load_diamond_sprite()
    
    if door_sprite is None:
        load_door_sprite()
    
    if humo_sprite is None:
        load_humo_sprite()
    
    if fire_sprite is None:
        load_fire_sprite()

# Variables del juego
player_score = 0
player_pos = [1, 1]
player_lives = 3
current_level = 0
maze = levels[current_level]['maze']
projectiles = []
last_direction = [1, 0]

# Sistema de diamantes obligatorios
total_diamonds = 0
collected_diamonds = 0

# Sistema de mensajes temporales
temp_message = ""
temp_message_time = 0
temp_message_duration = 2.0

# ========================================
# CLASE PERSONALIZADA PARA DEMONIO
# ========================================

class DemonRandomTeleport:
    """Comportamiento del demonio con teletransporte aleatorio"""
    
    def __init__(self, enemy_data, pathfinder, player_pos_getter, all_enemies=None):
        self.enemy = enemy_data
        self.pathfinder = pathfinder
        self.get_player_pos = player_pos_getter
        self.all_enemies = all_enemies or []
        
        self.last_teleport_time = 0
        self.teleport_cooldown = 4.0
        self.last_move_time = 0
        self.move_delay = 0.7
        
        print(f"👺 Demonio con teletransporte aleatorio inicializado")
        
    def update(self):
        """Actualiza el comportamiento del demonio"""
        current_time = time.time()
        player_pos = self.get_player_pos()
        enemy_pos = self.enemy["pos"]
        
        distance = math.sqrt((enemy_pos[0] - player_pos[0])**2 + (enemy_pos[1] - player_pos[1])**2)
        
        if self._can_teleport(current_time, distance):
            return self._teleport_randomly()
        elif self._can_move_now(current_time):
            return self._normal_move(player_pos, enemy_pos)
        
        return True
    
    def _can_teleport(self, current_time, distance):
        """Verifica si puede teletransportarse"""
        return current_time - self.last_teleport_time >= self.teleport_cooldown
    
    def _teleport_randomly(self):
        """Se teletransporta a una posición aleatoria"""
        try:
            current_time = time.time()
            self.last_teleport_time = current_time
            
            valid_positions = []
            current_maze = levels[current_level]['maze']
            height = len(current_maze)
            width = len(current_maze[0])
            
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    if current_maze[y][x] == 0:
                        valid_positions.append([x, y])
            
            if valid_positions:
                new_pos = random.choice(valid_positions)
                old_pos = self.enemy["pos"].copy()
                self.enemy["pos"] = new_pos
                self.enemy["dir"] = [0, 0]
                
                print(f"👺 Demonio se teletransportó de {old_pos} a {new_pos}")
                
                play_sound('teletransporte', volume=0.6)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error en teletransporte: {e}")
            return False
    
    def _can_move_now(self, current_time):
        """Controla la velocidad del demonio"""
        return current_time - self.last_move_time >= self.move_delay
    
    def _normal_move(self, player_pos, enemy_pos):
        """Movimiento normal"""
        try:
            self.last_move_time = time.time()
            
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

# ========================================
# CONFIGURACIÓN DE ENEMIGOS
# ========================================

ALL_ENEMY_TYPES = ['👽', '👻', '🧟', '🦹', '👺', '🤡', '👹']

ENEMIES_PER_LEVEL = {
    0: 3,  # Nivel 1: 3 enemigos
    1: 4,  # Nivel 2: 4 enemigos 
    2: 4,  # Nivel 3: 4 enemigos
    3: 5,  # Nivel 4: 5 enemigos
    4: 5   # Nivel 5: 5 enemigos
}

def find_valid_enemy_positions(maze, count=10):
    """Encuentra posiciones válidas para enemigos"""
    height = len(maze)
    width = len(maze[0])
    valid_positions = []
    
    player_safe_zone = []
    for y in range(0, 5):
        for x in range(0, 5):
            player_safe_zone.append([x, y])
    
    for y in range(3, height - 3):
        for x in range(3, width - 3):
            if maze[y][x] == 0:
                if [x, y] not in player_safe_zone:
                    distance_to_player = abs(x - 1) + abs(y - 1)
                    if distance_to_player >= 6:
                        is_near_exit = False
                        for exit_y in range(height):
                            for exit_x in range(width):
                                if maze[exit_y][exit_x] == 2:
                                    distance_to_exit = abs(x - exit_x) + abs(y - exit_y)
                                    if distance_to_exit < 4:
                                        is_near_exit = True
                                        break
                            if is_near_exit:
                                break
                        
                        if not is_near_exit:
                            valid_positions.append([x, y])
    
    print(f"🎯 Posiciones seguras encontradas: {len(valid_positions)}")
    
    import random
    random.shuffle(valid_positions)
    return valid_positions[:count]

def generate_random_enemies(level):
    """Genera enemigos aleatorios para un nivel"""
    enemy_count = ENEMIES_PER_LEVEL.get(level, 2)
    
    selected_types = random.sample(ALL_ENEMY_TYPES, min(enemy_count, len(ALL_ENEMY_TYPES)))
    
    current_maze = levels[level]['maze']
    valid_positions = find_valid_enemy_positions(current_maze, enemy_count + 5)
    
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

# Enemigos y comportamientos
enemies = []
enemy_behaviors = []

def show_temp_message(message):
    """Muestra un mensaje temporal"""
    global temp_message, temp_message_time
    temp_message = message
    temp_message_time = time.time()
    print(f"📢 Mensaje: {message}")

def draw_temp_message():
    """Dibuja mensaje temporal"""
    global temp_message, temp_message_time
    
    if temp_message and time.time() - temp_message_time < temp_message_duration:
        elapsed = time.time() - temp_message_time
        alpha = max(0, 1 - (elapsed / temp_message_duration))
        
        if fullscreen_mode:
            message_width = SCREEN_WIDTH - 80
            message_height = 100
            message_x = 40
            message_y = (SCREEN_HEIGHT // 2) - (message_height // 2)
            
            font_scale = max(1.0, min(2.5, SCREEN_WIDTH / 800))
            message_font_size = int(30 * font_scale)
            message_font = pygame.font.SysFont('Arial', message_font_size)
        else:
            message_width = SCREEN_WIDTH - 40
            message_height = 80
            message_x = 20
            message_y = (MAZE_HEIGHT * TILE_SIZE // 2) - (message_height // 2)
            message_font = font
        
        message_surface = pygame.Surface((message_width, message_height))
        message_surface.fill((0, 0, 0))
        message_surface.set_alpha(int(180 * alpha))
        
        screen.blit(message_surface, (message_x, message_y))
        border_thickness = max(2, int(3 * (SCREEN_WIDTH / 800)))
        pygame.draw.rect(screen, (255, 215, 0), (message_x - border_thickness, message_y - border_thickness, 
                        message_width + border_thickness * 2, message_height + border_thickness * 2), border_thickness)
        
        text_color = (255, int(255 * alpha), int(255 * alpha))
        text = message_font.render(temp_message, True, text_color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, message_y + message_height // 2))
        screen.blit(text, text_rect)
    elif temp_message and time.time() - temp_message_time >= temp_message_duration:
        temp_message = ""

def move_enemies():
    """Mueve enemigos usando IA"""
    global enemy_behaviors, pathfinder
    
    for i, behavior in enumerate(enemy_behaviors):
        try:
            enemy = behavior.enemy
            enemy_type = enemy["type"]
            old_pos = enemy["pos"].copy()
            
            old_invisible_state = False
            if enemy_type == '👻' and hasattr(behavior, 'is_invisible'):
                old_invisible_state = behavior.is_invisible
            
            behavior.update()
            
            if enemy_type == '👺':
                new_pos = enemy["pos"]
                distance_moved = abs(new_pos[0] - old_pos[0]) + abs(new_pos[1] - old_pos[1])
                if distance_moved > 1:
                    play_sound('teletransporte', volume=0.6)
                    print(f"👺 Demonio se teletransportó de {old_pos} a {new_pos}")
            
            if enemy_type == '👻' and hasattr(behavior, 'is_invisible'):
                new_invisible_state = behavior.is_invisible
                if not old_invisible_state and new_invisible_state:
                    play_sound('fantasma', volume=0.5)
                    print(f"👻 Fantasma se volvió INVISIBLE")
                elif old_invisible_state and not new_invisible_state:
                    print(f"👻 Fantasma se volvió VISIBLE")
                    
        except Exception as e:
            print(f"Error en comportamiento de enemigo: {e}")
            enemy = behavior.enemy
            player_x, player_y = player_pos
            enemy_x, enemy_y = enemy["pos"]
            
            dx, dy = pathfinder.get_next_move(enemy_x, enemy_y, player_x, player_y)
            new_x = enemy_x + dx
            new_y = enemy_y + dy
            
            if pathfinder.is_valid_position(new_x, new_y):
                enemy["pos"] = [new_x, new_y]

def move_projectiles():
    """Mueve proyectiles más rápidos"""
    global enemies, projectiles, player_score
    newp = []
    for p in projectiles:
        for _ in range(2):  # Proyectiles rápidos
            p['pos'][0] += p['dir'][0]
            p['pos'][1] += p['dir'][1]
            
            x, y = p['pos']
            
            if not (0 <= x < MAZE_WIDTH and 0 <= y < MAZE_HEIGHT):
                break
                
            if maze[y][x] == 1:
                break
                    
            hit = False
            for i, e in enumerate(enemies[:]):
                if e['pos'] == [x, y]:
                    is_invisible = False
                    if e['type'] == '👻' and i < len(enemy_behaviors):
                        behavior = enemy_behaviors[i]
                        if hasattr(behavior, 'is_currently_invisible'):
                            is_invisible = behavior.is_currently_invisible()
                    
                    if not is_invisible:
                        enemies.remove(e)
                        if i < len(enemy_behaviors):
                            enemy_behaviors.pop(i)
                        player_score += 150
                        
                        hit = True
                        break
            
            if hit:
                break
        else:
            if (0 <= p['pos'][0] < MAZE_WIDTH and 0 <= p['pos'][1] < MAZE_HEIGHT and 
                maze[p['pos'][1]][p['pos'][0]] != 1):
                newp.append(p)
    
    projectiles = newp

def check_enemy_collision():
    """Verifica colisiones entre jugador y enemigos"""
    global player_score, enemies, enemy_behaviors
    
    for i, e in enumerate(enemies):
        if e['pos'] == player_pos:
            is_invisible = False
            if e['type'] == '👻' and i < len(enemy_behaviors):
                behavior = enemy_behaviors[i]
                if hasattr(behavior, 'is_currently_invisible'):
                    is_invisible = behavior.is_currently_invisible()
            
            if not is_invisible:
                print(f"💥 COLISIÓN: Jugador tocado por {e['type']} en {e['pos']}")
                return True
    
    return False

def count_diamonds_in_level(maze):
    """Cuenta los diamantes totales en un nivel"""
    count = 0
    for row in maze:
        for cell in row:
            if cell == 3:
                count += 1
    return count

def get_player_position():
    return player_pos

def initialize_enemy_behaviors():
    """Inicializa los comportamientos de IA para todos los enemigos"""
    global enemy_behaviors
    enemy_behaviors = []
    
    for enemy in enemies:
        enemy_type = enemy.get("type", "👻")
        
        if enemy_type == "👺":
            behavior = DemonRandomTeleport(
                enemy_data=enemy,
                pathfinder=pathfinder,
                player_pos_getter=get_player_position,
                all_enemies=enemies
            )
        else:
            behavior = create_enemy_behavior(
                enemy_data=enemy,
                pathfinder=pathfinder,
                player_pos_getter=get_player_position,
                all_enemies=enemies
            )
        
        enemy_behaviors.append(behavior)
        
        print(f"👾 ENEMIGO CREADO: {enemy['pos']} - {enemy['type']}")
        if enemy_type == "👺":
            print(f"   🔧 Usando teletransporte aleatorio personalizado")

# ========================================
# FUNCIONES DEL JUEGO
# ========================================

def handle_bonus_tile(x, y):
    """Maneja las bonificaciones - diamantes"""
    global player_score, maze, collected_diamonds
    
    if maze[y][x] == 3:
        player_score += 100
        collected_diamonds += 1
        maze[y][x] = 0
        
        play_sound('diamante', volume=0.8)
        
        print(f"💎 Diamante recogido! {collected_diamonds}/{total_diamonds}")

def update_maze_dimensions():
    """Actualiza dimensiones del laberinto"""
    global MAZE_WIDTH, MAZE_HEIGHT
    current_maze = levels[current_level]['maze']
    MAZE_HEIGHT = len(current_maze)
    MAZE_WIDTH = len(current_maze[0])
    print(f"🎮 Nivel actualizado: {MAZE_WIDTH}x{MAZE_HEIGHT}")

def draw_maze():
    """Dibuja el laberinto"""
    maze_pixel_width = MAZE_WIDTH * TILE_SIZE
    maze_pixel_height = MAZE_HEIGHT * TILE_SIZE
    offset_x = (SCREEN_WIDTH - maze_pixel_width) // 2
    offset_y = (SCREEN_HEIGHT - maze_pixel_height - 100) // 2
    
    offset_x = max(0, offset_x)
    offset_y = max(0, offset_y)
    
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            screen_x = x * TILE_SIZE + offset_x
            screen_y = y * TILE_SIZE + offset_y
            rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
            
            if maze[y][x] == 1:  # Paredes
                if wall_sprite:
                    scaled_wall = pygame.transform.scale(wall_sprite, (TILE_SIZE, TILE_SIZE))
                    screen.blit(scaled_wall, (screen_x, screen_y))
                else:
                    pygame.draw.rect(screen, COLOR_WALL, rect)
                    pygame.draw.rect(screen, (10, 0, 0), rect, 2)
            elif maze[y][x] == 2:  # Portal de salida
                pygame.draw.rect(screen, COLOR_PATH, rect)
                
                if collected_diamonds >= 5:
                    # Puerta abierta
                    if door_sprite:
                        scaled_door = pygame.transform.scale(door_sprite, (TILE_SIZE, TILE_SIZE))
                        screen.blit(scaled_door, (screen_x, screen_y))
                        import math
                        alpha = int(64 + 63 * math.sin(time.time() * 5))
                        glow_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
                        glow_surface.fill((0, 255, 0))
                        glow_surface.set_alpha(alpha)
                        screen.blit(glow_surface, (screen_x, screen_y))
                    else:
                        pygame.draw.rect(screen, (0, 255, 0), rect)
                        door_emoji = emoji_font.render('🚪', True, (255, 255, 255))
                        screen.blit(door_emoji, (screen_x + 4, screen_y))
                else:
                    # Puerta cerrada
                    if door_sprite:
                        scaled_door = pygame.transform.scale(door_sprite, (TILE_SIZE, TILE_SIZE))
                        tinted_door = scaled_door.copy()
                        red_overlay = pygame.Surface((TILE_SIZE, TILE_SIZE))
                        red_overlay.fill((255, 0, 0))
                        red_overlay.set_alpha(100)
                        tinted_door.blit(red_overlay, (0, 0))
                        screen.blit(tinted_door, (screen_x, screen_y))
                    else:
                        pygame.draw.rect(screen, (255, 0, 0), rect)
                        door_emoji = emoji_font.render('🔒', True, (255, 255, 255))
                        screen.blit(door_emoji, (screen_x + 4, screen_y))
                        
            elif maze[y][x] == 3:  # Diamantes
                pygame.draw.rect(screen, COLOR_PATH, rect)
                
                if diamond_sprite:
                    scaled_diamond = pygame.transform.scale(diamond_sprite, (TILE_SIZE, TILE_SIZE))
                    screen.blit(scaled_diamond, (screen_x, screen_y))
                    import math
                    alpha = int(64 + 63 * math.sin(time.time() * 3))
                    glow_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    glow_surface.fill((255, 215, 0))
                    glow_surface.set_alpha(alpha)
                    screen.blit(glow_surface, (screen_x, screen_y))
                else:
                    pygame.draw.rect(screen, COLOR_BONUS, rect, 3)
                    bonus_emoji = emoji_font.render('💎', True, (255, 215, 0))
                    screen.blit(bonus_emoji, (screen_x + 4, screen_y))
            else:  # Suelo
                pygame.draw.rect(screen, COLOR_PATH, rect)
                if (x + y) % 4 == 0:
                    pygame.draw.rect(screen, (90, 45, 45), rect, 1)

def draw_player():
    """Dibuja al jugador"""
    x, y = player_pos
    
    maze_pixel_width = MAZE_WIDTH * TILE_SIZE
    maze_pixel_height = MAZE_HEIGHT * TILE_SIZE
    offset_x = (SCREEN_WIDTH - maze_pixel_width) // 2
    offset_y = (SCREEN_HEIGHT - maze_pixel_height - 100) // 2
    offset_x = max(0, offset_x)
    offset_y = max(0, offset_y)
    
    screen_x = x * TILE_SIZE + offset_x
    screen_y = y * TILE_SIZE + offset_y
    
    if use_sprites and dog_sprites:
        scaled_dog = pygame.transform.scale(dog_sprites[current_direction][0], (TILE_SIZE, TILE_SIZE))
        screen.blit(scaled_dog, (screen_x, screen_y))
    else:
        player_emoji = emoji_font.render('🐶', True, (255, 255, 0))
        screen.blit(player_emoji, (screen_x + 4, screen_y))

def draw_enemies():
    """Dibuja enemigos"""
    maze_pixel_width = MAZE_WIDTH * TILE_SIZE
    maze_pixel_height = MAZE_HEIGHT * TILE_SIZE
    offset_x = (SCREEN_WIDTH - maze_pixel_width) // 2
    offset_y = (SCREEN_HEIGHT - maze_pixel_height - 100) // 2
    offset_x = max(0, offset_x)
    offset_y = max(0, offset_y)
    
    for i, enemy in enumerate(enemies):
        x, y = enemy["pos"]
        enemy_type = enemy["type"]
        
        is_invisible = False
        if enemy_type == '👻' and i < len(enemy_behaviors):
            behavior = enemy_behaviors[i]
            if hasattr(behavior, 'is_currently_invisible'):
                is_invisible = behavior.is_currently_invisible()
        
        screen_x = x * TILE_SIZE + offset_x
        screen_y = y * TILE_SIZE + offset_y
        
        if is_invisible:
            if humo_sprite:
                scaled_humo = pygame.transform.scale(humo_sprite, (TILE_SIZE, TILE_SIZE))
                screen.blit(scaled_humo, (screen_x, screen_y))
            else:
                humo_emoji = emoji_font.render('💨', True, (200, 200, 200))
                screen.blit(humo_emoji, (screen_x + 4, screen_y))
        else:
            enemy_dir = enemy.get("dir", [1, 0])
            sprite_direction = 'left' if enemy_dir[0] < 0 else 'right'
            
            if enemy_type in enemy_sprites:
                scaled_enemy = pygame.transform.scale(enemy_sprites[enemy_type][sprite_direction], (TILE_SIZE, TILE_SIZE))
                screen.blit(scaled_enemy, (screen_x, screen_y))
            else:
                enemy_emoji = emoji_font.render(enemy_type, True, (0, 0, 0))
                screen.blit(enemy_emoji, (screen_x + 4, screen_y))

def draw_projectiles():
    """Dibuja proyectiles como proyectiles reales"""
    maze_pixel_width = MAZE_WIDTH * TILE_SIZE
    maze_pixel_height = MAZE_HEIGHT * TILE_SIZE
    offset_x = (SCREEN_WIDTH - maze_pixel_width) // 2
    offset_y = (SCREEN_HEIGHT - maze_pixel_height - 100) // 2
    offset_x = max(0, offset_x)
    offset_y = max(0, offset_y)
    
    for p in projectiles:
        x, y = p['pos']
        screen_x = x * TILE_SIZE + offset_x
        screen_y = y * TILE_SIZE + offset_y
        
        if poop_sprite:
            projectile_size = int(TILE_SIZE * 0.5)
            scaled_poop = pygame.transform.scale(poop_sprite, (projectile_size, projectile_size))
            
            direction = p.get('dir', [1, 0])
            if direction[0] != 0 or direction[1] != 0:
                angle = math.atan2(direction[1], direction[0]) * 180 / math.pi
                rotated_poop = pygame.transform.rotate(scaled_poop, -angle)
            else:
                rotated_poop = scaled_poop
            
            poop_rect = rotated_poop.get_rect()
            centered_x = screen_x + (TILE_SIZE - poop_rect.width) // 2
            centered_y = screen_y + (TILE_SIZE - poop_rect.height) // 2
            
            # Estela de proyectil
            if direction[0] != 0 or direction[1] != 0:
                trail_length = 4
                for i in range(1, trail_length + 1):
                    trail_x = centered_x - (direction[0] * i * 6)
                    trail_y = centered_y - (direction[1] * i * 6)
                    trail_alpha = max(30, 150 - (i * 30))
                    trail_size = max(2, projectile_size - (i * 4))
                    
                    trail_surface = pygame.Surface((trail_size, trail_size))
                    trail_surface.fill((101, 67, 33))
                    trail_surface.set_alpha(trail_alpha)
                    screen.blit(trail_surface, (trail_x, trail_y))
            
            screen.blit(rotated_poop, (centered_x, centered_y))
            
            # Partículas
            import random
            if random.random() < 0.3:
                particle_x = centered_x + random.randint(-5, 5)
                particle_y = centered_y + random.randint(-5, 5)
                particle_size = random.randint(1, 3)
                pygame.draw.circle(screen, (139, 69, 19), (particle_x, particle_y), particle_size)
            
        else:
            center_x = screen_x + TILE_SIZE // 2
            center_y = screen_y + TILE_SIZE // 2
            
            projectile_font_size = max(12, int(TILE_SIZE * 0.4))
            projectile_font = pygame.font.SysFont('Segoe UI Emoji', projectile_font_size)
            
            poop_emoji = projectile_font.render('💩', True, (139, 69, 19))
            emoji_rect = poop_emoji.get_rect(center=(center_x, center_y))
            screen.blit(poop_emoji, emoji_rect)

def draw_ui():
    """UI con sprites de fuego"""
    ui_start_y = SCREEN_HEIGHT - 90
    
    # Información del nivel
    level_info = f"Dimensión: {current_level + 1} - {levels[current_level]['name']}"
    level_text = small_font.render(level_info, True, COLOR_BONUS)
    screen.blit(level_text, (10, ui_start_y))
    
    # Vidas con sprites de corazón
    hearts_x = SCREEN_WIDTH - 150
    hearts_y = ui_start_y
    
    lives_label = small_font.render("Vida:", True, COLOR_FIRE)
    screen.blit(lives_label, (hearts_x - 50, hearts_y + 8))
    
    if heart_sprite:
        large_heart_sprite = pygame.transform.scale(heart_sprite, (35, 35))
        for i in range(player_lives):
            screen.blit(large_heart_sprite, (hearts_x + i * 40, hearts_y))
    elif fire_sprite:
        large_fire_sprite = pygame.transform.scale(fire_sprite, (35, 35))
        for i in range(player_lives):
            screen.blit(large_fire_sprite, (hearts_x + i * 40, hearts_y))
    else:
        for i in range(player_lives):
            pygame.draw.rect(screen, COLOR_FIRE, (hearts_x + i * 40, hearts_y, 30, 30))
    
    section_y = ui_start_y + 30
    
    # Puntuación
    score_text = small_font.render(f"Almas: {player_score}", True, COLOR_TEXT)
    screen.blit(score_text, (10, section_y))
    
    # Estado de diamantes
    diamonds_remaining = 5 - collected_diamonds
    if diamonds_remaining > 0:
        diamond_color = (255, 100, 100)
        diamond_status = f"Gemas: {collected_diamonds}/5 (faltan {diamonds_remaining}) CERRADA"
    else:
        diamond_color = (100, 255, 100)
        diamond_status = f"Gemas: {collected_diamonds}/5 COMPLETADO - PUERTA ABIERTA"
    
    diamond_text = small_font.render(diamond_status, True, diamond_color)
    if fire_sprite:
        fire_size = max(15, int(small_font_size * 0.8))
        scaled_fire = pygame.transform.scale(fire_sprite, (fire_size, fire_size))
        screen.blit(scaled_fire, (190, section_y))
        screen.blit(diamond_text, (210, section_y))
    else:
        screen.blit(diamond_text, (200, section_y))
    
    # Información de enemigos
    enemy_count = len(enemies)
    invisible_count = 0
    
    for i, e in enumerate(enemies):
        enemy_type = e['type']
        if enemy_type == '👻' and i < len(enemy_behaviors):
            behavior = enemy_behaviors[i]
            if hasattr(behavior, 'is_currently_invisible') and behavior.is_currently_invisible():
                invisible_count += 1
    
    enemy_info = f"Demonios: {enemy_count} activos"
    if invisible_count > 0:
        enemy_info += f" ({invisible_count} invisibles)"
    
    enemy_text = small_font.render(enemy_info, True, COLOR_FIRE)
    if fire_sprite:
        fire_size = max(15, int(small_font_size * 0.8))
        scaled_fire = pygame.transform.scale(fire_sprite, (fire_size, fire_size))
        screen.blit(scaled_fire, (590, section_y))
        screen.blit(enemy_text, (610, section_y))
    else:
        screen.blit(enemy_text, (600, section_y))
    
    combat_y = section_y + 25
    
    # Información de proyectiles
    projectile_info = f"Proyectiles: {len(projectiles)}/3"
    projectile_color = COLOR_FIRE if len(projectiles) < 3 else (255, 100, 100)
    projectile_text = small_font.render(projectile_info, True, projectile_color)
    
    if fire_sprite:
        fire_size = max(15, int(small_font_size * 0.8))
        scaled_fire = pygame.transform.scale(fire_sprite, (fire_size, fire_size))
        screen.blit(scaled_fire, (0, combat_y))
        screen.blit(projectile_text, (20, combat_y))
    else:
        screen.blit(projectile_text, (10, combat_y))
    
    # Información de aim bot
    if aim_bot.aim_assistance:
        if aim_bot.target_enemy:
            aim_status = "AIM: ACTIVO"
            aim_color = (0, 255, 0)
        else:
            aim_status = "AIM: ESPERANDO"
            aim_color = COLOR_FIRE
    else:
        aim_status = "AIM: MANUAL"
        aim_color = (100, 100, 100)
    
    aim_text = small_font.render(aim_status, True, aim_color)
    
    if fire_sprite:
        fire_size = max(15, int(small_font_size * 0.8))
        scaled_fire = pygame.transform.scale(fire_sprite, (fire_size, fire_size))
        screen.blit(scaled_fire, (190, combat_y))
        screen.blit(aim_text, (210, combat_y))
    else:
        screen.blit(aim_text, (200, combat_y))
    
    # Información de controles
    if controller_connected:
        control_text = f"Xbox360 | {levels[current_level]['difficulty']} | {FPS}FPS | A=disparar B=salir | +/-=tamaño F11=pantalla"
    else:
        control_text = f"Teclado | {levels[current_level]['difficulty']} | {FPS}FPS | ESPACIO=disparar A=aim +/-=tamaño F11=pantalla"
    
    info_color = COLOR_FIRE if controller_connected else COLOR_TEXT
    info_text_surface = small_font.render(control_text, True, info_color)
    
    if fire_sprite:
        fire_size = max(15, int(small_font_size * 0.8))
        scaled_fire = pygame.transform.scale(fire_sprite, (fire_size, fire_size))
        screen.blit(scaled_fire, (390, combat_y))
        screen.blit(info_text_surface, (410, combat_y))
    else:
        screen.blit(info_text_surface, (400, combat_y))

def draw_menu():
    """Menú principal con sprites de fuego"""
    screen.fill((20, 0, 0))
    
    if cover_image:
        cover_x = (SCREEN_WIDTH - cover_image.get_width()) // 2
        cover_y = 30
        screen.blit(cover_image, (cover_x, cover_y))
        title_y = cover_y + cover_image.get_height() + 30
    else:
        title_text = "DIMENSIONES INFERNALES"
        title = font.render(title_text, True, COLOR_FIRE)
        title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
        
        if fire_sprite:
            fire_size = max(30, int(base_font_size * 1.2))
            scaled_fire = pygame.transform.scale(fire_sprite, (fire_size, fire_size))
            
            screen.blit(scaled_fire, (title_x - fire_size - 10, 40))
            screen.blit(scaled_fire, (title_x + title.get_width() + 10, 40))
        
        screen.blit(title, (title_x, 40))
        subtitle = small_font.render("- Sistema de IA Demoníaca -", True, COLOR_BONUS)
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 80))
        title_y = 130
    
    # Opciones del menú con sprites de fuego
    menu_texts = ['Nueva Partida', 'Dificultad', 'Salir']
    
    for i, option in enumerate(menu_texts):
        option_y = title_y + i * 50
        
        fire_size = max(20, int(base_font_size * 0.8))
        option_text_width = font.size(option)[0]
        fire_x = (SCREEN_WIDTH // 2) - (option_text_width // 2) - fire_size - 10
        fire_y = option_y
        
        if fire_sprite:
            scaled_fire = pygame.transform.scale(fire_sprite, (fire_size, fire_size))
            screen.blit(scaled_fire, (fire_x, fire_y))
        else:
            fire_emoji = small_font.render('🔥', True, COLOR_FIRE)
            screen.blit(fire_emoji, (fire_x, fire_y))
        
        if i == menu_idx:
            color = COLOR_FIRE
            shadow_text = font.render(option, True, (100, 0, 0))
            screen.blit(shadow_text, (SCREEN_WIDTH // 2 - shadow_text.get_width() // 2 + 2, option_y + 2))
            
            indicator_size = fire_size + 5
            indicator_x = fire_x - indicator_size - 5
            if fire_sprite:
                scaled_indicator = pygame.transform.scale(fire_sprite, (indicator_size, indicator_size))
                screen.blit(scaled_indicator, (indicator_x, fire_y - 2))
            else:
                indicator = "► "
                indicator_text = font.render(indicator, True, COLOR_FIRE)
                screen.blit(indicator_text, (indicator_x, option_y))
        else:
            color = (150, 75, 75)
        
        text = font.render(option, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, option_y))
    
    # Información de controles
    controls_y = title_y + 200
    
    control_lines = [
        "CONTROLES:",
        "Xbox 360: A=aceptar | B=atrás | Joystick=navegar",
        "Teclado: Enter=aceptar | ESC=atrás | Flechas=navegar",
        "F11=Pantalla completa | +/- = Ajustar laberinto"
    ]
    
    for i, line in enumerate(control_lines):
        line_y = controls_y + i * 30
        
        if i == 0:
            color = COLOR_FIRE
            font_to_use = font
            
            if fire_sprite:
                fire_size = max(18, int(base_font_size * 0.7))
                scaled_fire = pygame.transform.scale(fire_sprite, (fire_size, fire_size))
                fire_x = (SCREEN_WIDTH // 2) - (font.size(line)[0] // 2) - fire_size - 10
                screen.blit(scaled_fire, (fire_x, line_y))
        else:
            color = COLOR_TEXT
            font_to_use = small_font
            
        text = font_to_use.render(line, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, line_y))
    
    # Información del juego
    info_y = controls_y + 120
    
    game_info = [
        "OBJETIVO: Recolecta los 5 diamantes para abrir las puertas",
        "ENEMIGOS: 7 tipos de criaturas infernales con IA única",
        "DISPARO: Siempre puedes disparar (ESPACIO/A) - Presiona A para aim bot",
        "Sprites personalizados para mejor experiencia visual"
    ]
    
    for i, info in enumerate(game_info):
        line_y = info_y + i * 25
        
        if i == 0:
            color = COLOR_BONUS
        else:
            color = (200, 150, 100)
        
        if fire_sprite:
            fire_size = max(15, int(small_font_size * 0.8))
            scaled_fire = pygame.transform.scale(fire_sprite, (fire_size, fire_size))
            text_width = small_font.size(info)[0]
            fire_x = (SCREEN_WIDTH - text_width) // 2 - fire_size - 8
            screen.blit(scaled_fire, (fire_x, line_y))
        
        text = small_font.render(info, True, color)
        text_x = (SCREEN_WIDTH - text.get_width()) // 2
        screen.blit(text, (text_x, line_y))
    
    # Efectos visuales sutiles
    import random
    for _ in range(3):
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 50)
        alpha = random.randint(50, 150)
        
        particle_surface = pygame.Surface((4, 4))
        particle_surface.fill((255, 100, 0))
        particle_surface.set_alpha(alpha)
        screen.blit(particle_surface, (x, y))
    
    pygame.display.flip()

def draw_difficulty_menu():
    """Menú de dificultad con sprites de fuego"""
    screen.fill((20, 0, 0))
    
    title_text = "Elige tu nivel de tortura:"
    title = font.render(title_text, True, COLOR_FIRE)
    title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
    
    if fire_sprite:
        fire_size = max(25, int(base_font_size * 0.9))
        scaled_fire = pygame.transform.scale(fire_sprite, (fire_size, fire_size))
        fire_x = title_x - fire_size - 10
        screen.blit(scaled_fire, (fire_x, 80))
    
    screen.blit(title, (title_x, 80))
    
    difficulty_texts = ['Alma Perdida (Fácil)', 'Demonio (Medio)', 'Señor del Infierno (Difícil)']
    
    for i, opt in enumerate(difficulty_texts):
        option_y = 180 + i * 60
        
        fire_size = max(20, int(base_font_size * 0.8))
        option_text_width = font.size(opt)[0]
        fire_x = (SCREEN_WIDTH // 2) - (option_text_width // 2) - fire_size - 10
        fire_y = option_y
        
        if fire_sprite:
            scaled_fire = pygame.transform.scale(fire_sprite, (fire_size, fire_size))
            screen.blit(scaled_fire, (fire_x, fire_y))
        else:
            fire_emoji = small_font.render('🔥', True, COLOR_FIRE)
            screen.blit(fire_emoji, (fire_x, fire_y))
        
        if i == diff_idx:
            color = COLOR_FIRE
            shadow_text = font.render(opt, True, (100, 0, 0))
            screen.blit(shadow_text, (SCREEN_WIDTH // 2 - shadow_text.get_width() // 2 + 2, option_y + 2))
            
            indicator_size = fire_size + 5
            indicator_x = fire_x - indicator_size - 5
            if fire_sprite:
                scaled_indicator = pygame.transform.scale(fire_sprite, (indicator_size, indicator_size))
                screen.blit(scaled_indicator, (indicator_x, fire_y - 2))
            else:
                indicator = "► "
                indicator_text = font.render(indicator, True, COLOR_FIRE)
                screen.blit(indicator_text, (indicator_x, option_y))
        else:
            color = (150, 75, 75)
        
        txt = font.render(opt, True, color)
        screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, option_y))
    
    speed_y = 400
    
    speed_info = [
        f"VELOCIDADES:",
        f"Alma Perdida: {FPS_levels['Fácil']} FPS - Demonios lentos",
        f"Demonio: {FPS_levels['Medio']} FPS - Velocidad equilibrada", 
        f"Señor del Infierno: {FPS_levels['Difícil']} FPS - Máxima furia"
    ]
    
    for i, info in enumerate(speed_info):
        line_y = speed_y + i * 30
        
        if i == 0:
            color = COLOR_FIRE
            font_to_use = font
            
            if fire_sprite:
                fire_size = max(18, int(base_font_size * 0.7))
                scaled_fire = pygame.transform.scale(fire_sprite, (fire_size, fire_size))
                fire_x = (SCREEN_WIDTH // 2) - (font.size(info)[0] // 2) - fire_size - 10
                screen.blit(scaled_fire, (fire_x, line_y))
                
        elif i == diff_idx + 1:
            color = COLOR_FIRE
            font_to_use = small_font
            
            if fire_sprite:
                fire_size = max(15, int(small_font_size * 0.8))
                scaled_fire = pygame.transform.scale(fire_sprite, (fire_size, fire_size))
                text_width = small_font.size(info)[0]
                fire_x = (SCREEN_WIDTH - text_width) // 2 - fire_size - 8
                screen.blit(scaled_fire, (fire_x, line_y))
        else:
            color = (150, 100, 100)
            font_to_use = small_font
            
        text = font_to_use.render(info, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, line_y))
    
    instructions_y = speed_y + 150
    
    back_text = small_font.render("Enter=aceptar | ESC/B=volver | Flechas=navegar", True, COLOR_BONUS)
    screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, instructions_y))
    
    pygame.display.flip()

def reset_game(show_welcome_messages=True):
    global player_pos, player_lives, current_level, maze, enemies, projectiles, pathfinder
    global player_score, screen, total_diamonds, collected_diamonds, temp_message, temp_message_time
    global last_button_a_state, last_button_b_state, last_space_state
    
    player_pos = [1, 1]
    player_lives = 3
    current_level = 0
    player_score = 0
    
    temp_message = ""
    temp_message_time = 0
    last_button_a_state = False
    last_button_b_state = False
    last_space_state = False
    
    import copy
    maze = copy.deepcopy(levels[current_level]['maze'])
    projectiles = []
    
    update_maze_dimensions()
    
    pathfinder = AStar(maze)
    
    reset_enemies()
    
    print(f"🔄 Juego reiniciado - Nivel {current_level + 1}")
    print(f"💎 Diamantes en nivel: {total_diamonds}")
    
    if show_welcome_messages:
        show_message(f"Bienvenido a las Dimensiones Infernales!")
        show_message(f"Nivel {current_level + 1}: {levels[current_level]['name']}")
        show_message(f"Objetivo: Recolecta los 5 diamantes para abrir la puerta")
        show_message(f"Cuidado con los {len(enemies)} demonios que te persiguen!")

def reset_enemies():
    """Resetea enemigos de forma aleatoria según el nivel actual"""
    global enemies, enemy_behaviors, pathfinder, total_diamonds, collected_diamonds, maze
    
    import copy
    maze = copy.deepcopy(levels[current_level]['maze'])
    
    total_diamonds = count_diamonds_in_level(maze)
    collected_diamonds = 0
    
    if total_diamonds != 5:
        print(f"⚠️ ERROR: Nivel {current_level + 1} tiene {total_diamonds} diamantes, debería tener 5")
        total_diamonds = 5
    
    print(f"💎 Nivel {current_level + 1}: {total_diamonds} diamantes requeridos")
    
    pathfinder = AStar(maze)
    
    enemies_config = generate_random_enemies(current_level)
    
    enemies = []
    for enemy_config in enemies_config:
        enemy = {
            'pos': enemy_config['pos'].copy(),
            'dir': [0, -1],
            'type': enemy_config['type']
        }
        enemies.append(enemy)
    
    if len(enemies) == 0:
        enemy = {
            'pos': [2, 2],
            'dir': [0, -1],
            'type': random.choice(ALL_ENEMY_TYPES)
        }
        enemies.append(enemy)
    
    initialize_enemy_behaviors()
    
    print(f"✅ Nivel {current_level + 1}: {len(enemies)} enemigos cargados")

def show_message(message):
    """Función de mensaje con limpieza automática de emojis"""
    clean_message = message
    clean_message = clean_message.replace("🔥", "")
    clean_message = clean_message.replace("💎", "diamantes")
    clean_message = clean_message.replace("🚪", "puerta")
    clean_message = clean_message.replace("🎯", "")
    clean_message = clean_message.replace("👹", "demonios")
    clean_message = clean_message.replace("💀", "")
    clean_message = clean_message.replace("🏆", "")
    clean_message = clean_message.replace("😈", "")
    clean_message = clean_message.replace("💖", "")
    clean_message = clean_message.replace("⚠️", "")
    clean_message = clean_message.replace("✅", "COMPLETADO")
    clean_message = clean_message.replace("❌", "")
    clean_message = clean_message.replace("🤡", "payaso")
    clean_message = clean_message.replace("🧟", "zombie")
    clean_message = clean_message.replace("👻", "fantasma")
    clean_message = clean_message.replace("👽", "alien")
    clean_message = clean_message.replace("🦹", "villano")
    clean_message = clean_message.replace("👺", "demonio")
    
    temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    temp_surface.fill(COLOR_BACKGROUND)
    
    text = font.render(clean_message, True, COLOR_TEXT)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    temp_surface.blit(text, text_rect)
    
    screen.blit(temp_surface, (0, 0))
    pygame.display.flip()
    time.sleep(1.5)

def next_level():
    global current_level, maze, player_pos, enemies, projectiles, game_state, pathfinder, screen
    global total_diamonds, collected_diamonds
    
    current_level += 1
    if current_level < len(levels):
        import copy
        maze = copy.deepcopy(levels[current_level]['maze'])
        update_maze_dimensions()
        
        pathfinder = AStar(maze)
        
        player_pos = [1, 1]
        projectiles = []
        
        reset_enemies()
        
        show_message(f"Nivel {current_level + 1}: {levels[current_level]['name']}")
        show_message(f"Recolecta los 5 diamantes para continuar!")
        show_message(f"Encuentra la puerta infernal cuando tengas todos los diamantes")
    else:
        if music_paths and music_paths['victory']:
            stop_music()
            play_music(music_paths['victory'], loop=0, volume=0.7)
        
        show_message(f"Has conquistado todas las dimensiones infernales!")
        show_message(f"Almas recolectadas: {player_score}")
        reset_game(show_welcome_messages=False)
        reset_menu()
        game_state = STATE_MENU
        
        if music_paths and music_paths['menu']:
            play_music(music_paths['menu'], volume=0.3)

# Inicialización
print("")
print("🎮 INICIALIZANDO COMPONENTES FINALES:")

sprites_loaded_count = load_all_sprites()

print("📊 RESUMEN FINAL:")
print(f"   ✅ Sprites: {sprites_loaded_count}/10 cargados")
print(f"   ✅ Audio: {sounds_count}/7 sonidos + {music_count}/4 músicas")
print(f"   ✅ IA: A* + Árboles de Comportamiento implementados")
print(f"   ✅ Controles: Xbox 360 + Teclado soportados")
print(f"   ✅ Niveles: 5 dimensiones infernales con 5 diamantes cada una")

pathfinder = AStar(levels[current_level]['maze'])

clock = pygame.time.Clock()
if 'enemies' in globals() and enemies:
    initialize_enemy_behaviors()

reset_enemies()

# Loop principal
running = True
while running:
    controller_move = get_controller_movement()
    controller_a_menu = get_controller_button_a_menu()
    controller_b = get_controller_button_b()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.JOYDEVICEADDED:
            print("🎮 Control conectado!")
            init_controller()
        elif event.type == pygame.JOYDEVICEREMOVED:
            print("🚫 Control desconectado!")
            controller_connected = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                toggle_fullscreen()
            elif event.key == pygame.K_F4 and fullscreen_mode:
                toggle_fullscreen()
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                adjust_tile_size(increase=True)
            elif event.key == pygame.K_MINUS:
                adjust_tile_size(increase=False)
            
            if game_state == STATE_MENU:
                if event.key == pygame.K_UP:
                    menu_idx = (menu_idx - 1) % 3
                elif event.key == pygame.K_DOWN:
                    menu_idx = (menu_idx + 1) % 3
                elif event.key == pygame.K_RETURN:
                    play_sound('click', volume=0.5)
                    
                    if menu_idx == 0:  # Nueva Partida
                        reset_game(show_welcome_messages=True)
                        update_maze_dimensions()
                        
                        if music_paths and music_paths['game']:
                            stop_music()
                            play_music(music_paths['game'], volume=0.4)
                        
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
                    play_sound('click', volume=0.5)
                    
                    FPS = FPS_levels[difficulty_options[diff_idx]]
                    reset_menu()
                    game_state = STATE_MENU
                elif event.key == pygame.K_ESCAPE:
                    play_sound('click', volume=0.5)
                    
                    reset_menu()
                    game_state = STATE_MENU
    
    # Manejar navegación con control en menús
    if game_state == STATE_MENU:
        if abs(controller_move[1]) > 0.5:
            if controller_move[1] < 0:
                menu_idx = (menu_idx - 1) % 3
            else:
                menu_idx = (menu_idx + 1) % 3
            time.sleep(0.15)
        
        if controller_a_menu:
            play_sound('click', volume=0.5)
            
            if menu_idx == 0:  # Nueva Partida
                reset_game(show_welcome_messages=True)
                update_maze_dimensions()
                
                if music_paths and music_paths['game']:
                    stop_music()
                    play_music(music_paths['game'], volume=0.4)
                
                game_state = STATE_PLAY
            elif menu_idx == 1:  # Seleccionar Dificultad
                game_state = STATE_DIFF
            elif menu_idx == 2:  # Salir
                running = False
        
        draw_menu()
        
    elif game_state == STATE_DIFF:
        if abs(controller_move[1]) > 0.5:
            if controller_move[1] < 0:
                diff_idx = (diff_idx - 1) % len(difficulty_options)
            else:
                diff_idx = (diff_idx + 1) % len(difficulty_options)
            time.sleep(0.15)
        
        if controller_a_menu:
            play_sound('click', volume=0.5)
            
            FPS = FPS_levels[difficulty_options[diff_idx]]
            reset_menu()
            game_state = STATE_MENU
        
        if controller_b:
            play_sound('click', volume=0.5)
            
            reset_menu()
            game_state = STATE_MENU
        
        draw_difficulty_menu()
        
    elif game_state == STATE_PLAY:
        # Controles del jugador
        keys = pygame.key.get_pressed()
        new_pos = player_pos.copy()
        
        controller_shoot = get_controller_shoot()
        
        move_x, move_y = 0, 0
        
        # Movimiento con flechas
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
        
        # Movimiento con control (prioridad)
        if controller_connected and (abs(controller_move[0]) > 0 or abs(controller_move[1]) > 0):
            norm_move = normalize_direction(controller_move[0], controller_move[1])
            move_x, move_y = norm_move[0], norm_move[1]
            
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
            
            old_pos = player_pos.copy()
            player_pos = new_pos
            
            if old_pos != player_pos:
                handle_bonus_tile(new_pos[0], new_pos[1])
        
        ensure_valid_shooting_direction()
        
        can_shoot = len(projectiles) < 3
        
        # Disparo con ESPACIO
        current_space_pressed = keys[pygame.K_SPACE]
        keyboard_shoot = current_space_pressed and not last_space_state
        last_space_state = current_space_pressed
        
        if (controller_shoot or keyboard_shoot) and can_shoot:
            aim_direction = None
            if aim_bot.aim_assistance:
                aim_direction = aim_bot.get_aim_direction(player_pos, enemies)
            
            if aim_direction:
                final_direction = aim_direction
                disparo_tipo = "GUIADO"
            else:
                final_direction = last_direction.copy()
                
                if final_direction == [0, 0] or final_direction is None:
                    if current_direction == 'up':
                        final_direction = [0, -1]
                    elif current_direction == 'down':
                        final_direction = [0, 1]
                    elif current_direction == 'left':
                        final_direction = [-1, 0]
                    elif current_direction == 'right':
                        final_direction = [1, 0]
                    else:
                        final_direction = [1, 0]
                
                disparo_tipo = "MANUAL"
            
            projectiles.append({'pos': player_pos.copy(), 'dir': final_direction})
            
            play_sound('disparo', volume=0.6)
            
            print(f"PROYECTIL {disparo_tipo} creado: {final_direction}")
            print(f"Proyectiles activos: {len(projectiles)}/3")
            
        elif (controller_shoot or keyboard_shoot) and not can_shoot:
            print("⚠️ Máximo de proyectiles alcanzado (3/3)")
        
        # Toggle aim bot
        if keys[pygame.K_a]:
            aim_bot.aim_assistance = not aim_bot.aim_assistance
            status = "ACTIVADO" if aim_bot.aim_assistance else "DESACTIVADO"
            print(f"🎯 Aim bot {status}")
            show_temp_message(f"Aim bot {status}")
            time.sleep(0.3)
        
        # Recargar sprites
        if keys[pygame.K_r]:
            print("🔄 Recargando sprites...")
            reload_sprites_if_needed()
            show_message("¡Sprites recargados!")
        
        # Verificar llegada a la salida
        if maze[player_pos[1]][player_pos[0]] == 2:
            if collected_diamonds >= 5:
                print(f"🚪 Portal abierto! Avanzando al siguiente nivel...")
                
                play_sound('puerta', volume=0.8)
                
                next_level()
            else:
                remaining = 5 - collected_diamonds
                show_temp_message(f"Faltan {remaining} diamantes! La puerta está cerrada")
        
        # Actualizar enemigos y proyectiles
        move_enemies()
        move_projectiles()
        
        # Verificar colisiones
        if check_enemy_collision():
            player_lives -= 1
            player_pos = [1, 1]
            reset_enemies()
            projectiles = []
            
            play_sound('muerte', volume=0.8)
            
            temp_message = ""
            temp_message_time = 0
            last_button_a_state = False
            last_button_b_state = False
            last_space_state = False
            
            if player_lives <= 0:
                if music_paths and music_paths['defeat']:
                    stop_music()
                    play_music(music_paths['defeat'], loop=0, volume=0.6)
                
                show_message(f"Tu alma ha sido devorada")
                show_message(f"Almas perdidas: {player_score}")
                reset_game(show_welcome_messages=False)
                reset_menu()
                game_state = STATE_MENU
                
                if music_paths and music_paths['menu']:
                    play_music(music_paths['menu'], volume=0.3)
            else:
                show_message(f"Los demonios te han tocado! Vida restante: {player_lives}")
        
        # Dibujar todo
        screen.fill(COLOR_BACKGROUND)
        draw_maze()
        draw_player()
        draw_enemies()
        draw_projectiles()
        draw_ui()
        draw_temp_message()

        # Salir del juego
        if keys[pygame.K_ESCAPE] or controller_b:
            temp_message = ""
            temp_message_time = 0
            last_button_a_state = False
            last_button_b_state = False
            last_space_state = False
            reset_menu()
            
            if music_paths and music_paths['menu']:
                stop_music()
                play_music(music_paths['menu'], volume=0.3)
            
            game_state = STATE_MENU
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()