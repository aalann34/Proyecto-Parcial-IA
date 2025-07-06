print("🎮 Sistema de auto-escalado activado - Laberinto grande y visible")
print("🖼️ Ventana optimizada con laberinto de tamaño perfecto")
print("💡 Controles de tamaño:")
print("   - F11: Pantalla completa")
print("   - +/-: Ajustar tamaño del laberinto")
print("🎯 Laberinto optimizado para máxima visibilidad")
print("")

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
from scripts import AStar, create_enemy_behavior

# Inicializar Pygame
pygame.init()

# NUEVO: Inicializar sistema de audio
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# NUEVO: Inicializar sistema de joysticks/controles
pygame.joystick.init()

# NUEVO: Variable de pantalla completa
fullscreen_mode = False

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
    """CORREGIDO: Asegura que siempre haya una dirección válida para disparar"""
    global last_direction, current_direction
    
    # Si last_direction es [0,0] o inválida, usar la dirección del sprite actual
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
            # Por defecto: disparar hacia la derecha
            last_direction = [1, 0]
            current_direction = 'right'
    
    # NUEVO: Verificar que la dirección sea válida (no [0,0])
    if last_direction[0] == 0 and last_direction[1] == 0:
        last_direction = [1, 0]  # Forzar dirección derecha por defecto
        print("🔧 Dirección de disparo corregida: derecha")

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

# ========================================
# SISTEMA DE AUTO-ESCALADO INTELIGENTE
# ========================================

def detect_screen_resolution():
    """Detecta la resolución de pantalla y calcula dimensiones óptimas"""
    # Obtener información de la pantalla
    display_info = pygame.display.Info()
    desktop_width = display_info.current_w
    desktop_height = display_info.current_h
    
    print(f"🖥️ Resolución detectada: {desktop_width}x{desktop_height}")
    
    # Calcular factor de escala basado en resolución común (1920x1080)
    base_width = 1920
    base_height = 1080
    
    scale_factor_w = desktop_width / base_width
    scale_factor_h = desktop_height / base_height
    scale_factor = min(scale_factor_w, scale_factor_h)  # Usar el menor para mantener proporción
    
    # Asegurar que el factor de escala esté en un rango razonable
    scale_factor = max(0.5, min(scale_factor, 2.0))  # Entre 50% y 200%
    
    print(f"📐 Factor de escala calculado: {scale_factor:.2f}")
    
    return scale_factor, desktop_width, desktop_height

def calculate_optimal_dimensions(scale_factor, desktop_width, desktop_height):
    """Calcula dimensiones óptimas para el juego - LABERINTO MÁS GRANDE Y VISIBLE"""
    
    # CORREGIDO: Laberinto más grande para mejor visibilidad
    base_tile_size = 50  # AUMENTADO de 35 a 50 para mejor visibilidad
    tile_size = int(base_tile_size * scale_factor)
    tile_size = max(40, min(tile_size, 80))  # Rango: 40-80 píxeles (más grande)
    
    # NUEVO: Tamaños más grandes para mejor visibilidad
    if desktop_width >= 1920:
        tile_size = max(tile_size, 55)  # Mínimo 55px en pantallas grandes
    if desktop_width >= 2560:
        tile_size = max(tile_size, 65)  # Mínimo 65px en pantallas 2K+
    
    # Dimensiones del laberinto
    maze_width = 24
    maze_height = 14
    
    # Calcular tamaño mínimo necesario para el laberinto
    min_game_width = maze_width * tile_size
    min_game_height = maze_height * tile_size + 120  # +120 para UI
    
    # AJUSTADO: Ventana moderada pero laberinto grande
    max_window_width = int(desktop_width * 0.85)  # 85% de la pantalla
    max_window_height = int(desktop_height * 0.90)  # 90% de la pantalla
    
    # AJUSTADO: Tamaño mínimo para acomodar laberinto grande
    min_window_width = max(1200, min_game_width)  
    min_window_height = max(800, min_game_height)  
    
    # Determinar tamaño final de ventana
    window_width = max(min_window_width, min(max_window_width, min_game_width + 200))
    window_height = max(min_window_height, min(max_window_height, min_game_height + 100))
    
    print(f"🎮 Dimensiones calculadas (LABERINTO GRANDE Y VISIBLE):")
    print(f"   - Tamaño de celda: {tile_size}px (AUMENTADO para mejor visibilidad)")
    print(f"   - Laberinto: {min_game_width}x{min_game_height - 120}px")
    print(f"   - Ventana: {window_width}x{window_height}")
    print(f"   - Resolución detectada: {desktop_width}x{desktop_height}")
    
    return tile_size, window_width, window_height, maze_width, maze_height

# Detectar resolución y calcular dimensiones automáticamente
scale_factor, desktop_width, desktop_height = detect_screen_resolution()
TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, MAZE_WIDTH, MAZE_HEIGHT = calculate_optimal_dimensions(
    scale_factor, desktop_width, desktop_height
)

# Configuración de la pantalla con auto-escalado
SCREEN_WIDTH = WINDOW_WIDTH
SCREEN_HEIGHT = WINDOW_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🔥 Dimensiones Infernales - Sistema de IA Avanzado")

# NUEVO: Maximizar ventana automáticamente al iniciar
import os
maximized_successfully = False

try:
    if os.name == 'nt':  # Windows
        import pygame._sdl2
        window = pygame._sdl2.Window.from_display_module()
        window.maximize()
        maximized_successfully = True
        print("🖼️ Ventana maximizada automáticamente")
        # Actualizar dimensiones después de maximizar
        SCREEN_WIDTH = screen.get_width()
        SCREEN_HEIGHT = screen.get_height()
        print(f"📐 Nueva resolución: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
except:
    print("⚠️ No se pudo maximizar automáticamente, usando ventana grande")

# Fallback: Si no se pudo maximizar, usar una ventana más grande
if not maximized_successfully:
    # Crear una ventana apropiada para el laberinto grande
    fallback_width = min(1400, int(desktop_width * 0.85))  # Aumentado para acomodar laberinto
    fallback_height = min(900, int(desktop_height * 0.85))  # Aumentado para acomodar laberinto
    screen = pygame.display.set_mode((fallback_width, fallback_height))
    SCREEN_WIDTH = fallback_width
    SCREEN_HEIGHT = fallback_height
    print(f"🖼️ Ventana grande creada: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print("💡 Usa F11 para pantalla completa o +/- para ajustar el laberinto")

def adjust_tile_size(increase=True):
    """Función para ajustar el tamaño del laberinto dinámicamente"""
    global TILE_SIZE, emoji_font, emoji_font_size
    
    old_size = TILE_SIZE
    
    if increase:
        TILE_SIZE = min(TILE_SIZE + 5, 120)  # Máximo 120px (aumentado)
        action = "aumentado"
    else:
        TILE_SIZE = max(TILE_SIZE - 5, 30)   # Mínimo 30px (aumentado)
        action = "reducido"
    
    if TILE_SIZE != old_size:
        # Actualizar fuente de emojis para que coincida
        emoji_font_size = int(TILE_SIZE * 0.8)
        emoji_font = pygame.font.SysFont('Segoe UI Emoji', emoji_font_size)
        
        print(f"🔧 Tamaño de laberinto {action}: {old_size}px → {TILE_SIZE}px")
        show_temp_message(f"Laberinto {action}: {TILE_SIZE}px")
    else:
        limit = "máximo" if increase else "mínimo"
        print(f"⚠️ Tamaño {limit} alcanzado: {TILE_SIZE}px")
        show_temp_message(f"Tamaño {limit}: {TILE_SIZE}px")

# FUNCIÓN F12 ELIMINADA - SOLO USAR F11 PARA PANTALLA COMPLETA

# Configuración de fuentes escaladas automáticamente - ADAPTADAS AL LABERINTO GRANDE
pygame.font.init()
# AJUSTADO: Fuentes adaptadas al laberinto más grande
base_font_size = max(20, int(26 * scale_factor))  # Aumentado de 24 a 26
small_font_size = max(16, int(20 * scale_factor))  # Aumentado de 18 a 20
emoji_font_size = max(18, int(TILE_SIZE * 0.8))   # Adaptado al nuevo TILE_SIZE

font = pygame.font.SysFont('Arial', base_font_size)
small_font = pygame.font.SysFont('Arial', small_font_size)
emoji_font = pygame.font.SysFont('Segoe UI Emoji', emoji_font_size)

print(f"✅ Configuración de pantalla con laberinto grande:")
print(f"   - Resolución de escritorio: {desktop_width}x{desktop_height}")
print(f"   - Tamaño de ventana inicial: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
print(f"   - Factor de escala: {scale_factor:.2f}")
print(f"   - Tamaño de fuente principal: {base_font_size}px")
print(f"   - Tamaño de fuente pequeña: {small_font_size}px")
print(f"   - Tamaño de celda del juego: {TILE_SIZE}px (GRANDE Y VISIBLE)")
print(f"   - Tamaño total del laberinto: {MAZE_WIDTH * TILE_SIZE}x{MAZE_HEIGHT * TILE_SIZE}px")

def toggle_fullscreen():
    """ACTUALIZADO: Función para alternar entre pantalla completa y modo ventana con auto-escalado"""
    global fullscreen_mode, screen, SCREEN_WIDTH, SCREEN_HEIGHT, scale_factor
    global font, small_font, emoji_font, base_font_size, small_font_size, emoji_font_size
    
    if fullscreen_mode:
        # Cambiar a modo ventana (usar dimensiones calculadas automáticamente)
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        fullscreen_mode = False
        SCREEN_WIDTH = WINDOW_WIDTH
        SCREEN_HEIGHT = WINDOW_HEIGHT
        print(f"🖼️ Modo ventana: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    else:
        # Cambiar a pantalla completa
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        fullscreen_mode = True
        SCREEN_WIDTH = screen.get_width()
        SCREEN_HEIGHT = screen.get_height()
        
        # Recalcular factor de escala para pantalla completa
        scale_factor = min(SCREEN_WIDTH / 1920, SCREEN_HEIGHT / 1080)
        scale_factor = max(0.5, min(scale_factor, 3.0))
        
        # Actualizar fuentes para pantalla completa
        base_font_size = max(20, int(30 * scale_factor))
        small_font_size = max(16, int(22 * scale_factor))
        emoji_font_size = max(20, int(TILE_SIZE * 0.9))
        
        font = pygame.font.SysFont('Arial', base_font_size)
        small_font = pygame.font.SysFont('Arial', small_font_size)
        emoji_font = pygame.font.SysFont('Segoe UI Emoji', emoji_font_size)
        
        print(f"🖥️ Pantalla completa: {SCREEN_WIDTH}x{SCREEN_HEIGHT} (escala: {scale_factor:.2f})")

# Intentar inicializar control al inicio
init_controller()

# ========================================
# NIVELES CORREGIDOS - PAREDES Y PUERTAS FIJAS
# ========================================

levels = [
    # NIVEL 1 - ENTRADA AL INFIERNO (COMPLETAMENTE CORREGIDO)
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
            [1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,1,1,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    },

    # NIVEL 2 - CÁMARAS DE TORMENTO (CORREGIDO)
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
            [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    },

    # NIVEL 3 - LABERINTO DE FUEGO (CORREGIDO)
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
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    },

    # NIVEL 4 - FORTALEZA DEMONÍACA (CORREGIDO)
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
            [1,0,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    },

    # NIVEL 5 - TRONO DE LUCIFER (CORREGIDO)
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
            [1,1,1,0,1,0,1,1,1,0,1,0,1,0,1,1,1,1,0,1,0,1,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    }
]

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
# NUEVOS SPRITES
heart_sprite = None  # NUEVO: Sprite de corazón
diamond_sprite = None  # NUEVO: Sprite de diamante
door_sprite = None  # NUEVO: Sprite de puerta
humo_sprite = None  # NUEVO: Sprite de humo para fantasmas invisibles
current_direction = 'right'

# ========================================
# SISTEMA DE AUDIO MEJORADO (INTEGRADO CHATGPT SOLUTION)
# ========================================

# Variables para sonidos
sounds = {}
music_loaded = False
audio_enabled = True
music_paths = {}  # NUEVO: Variable global para rutas de música

def load_sound(filename, sound_name):
    """Carga un sonido específico con manejo de errores"""
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
    """Carga música de fondo con manejo de errores"""
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
    """CORREGIDO: Reproduce un sonido específico con debug"""
    if audio_enabled and sound_name in sounds:
        try:
            sound = sounds[sound_name]
            sound.set_volume(volume)
            sound.play()
            # DEBUG: Solo mostrar sonidos importantes
            if sound_name in ['golpe', 'diamante', 'muerte']:
                print(f"🔊 SONIDO: {sound_name}.wav reproducido (vol: {volume:.1f})")
        except Exception as e:
            print(f"❌ Error reproduciendo sonido {sound_name}: {e}")
    elif sound_name not in sounds and audio_enabled:
        print(f"⚠️ Sonido '{sound_name}' no encontrado en assets/sounds/")

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

    # CORREGIDO: Usar nombres exactos de archivos que tienes
    sounds_to_load = [
        ('disparo.wav', 'disparo'),      # Cambié 'shoot' por 'disparo'
        ('golpe.wav', 'golpe'),          # Cambié 'hit' por 'golpe'
        ('diamante.wav', 'diamante'),    # Cambié 'diamond' por 'diamante'
        ('puerta.wav', 'puerta'),        # Cambié 'door' por 'puerta'
        ('muerte.wav', 'muerte'),        # Cambié 'death' por 'muerte'
        ('click.wav', 'click'),          # Mantuvo igual
        ('fantasma.wav', 'fantasma'),    # Cambié 'ghost' por 'fantasma'
        ('teletransporte.wav', 'teletransporte')  # Cambié 'teleport' por 'teletransporte'
    ]

    sounds_loaded = 0
    for filename, sound_name in sounds_to_load:
        if load_sound(filename, sound_name):
            sounds_loaded += 1

    # Verificar música disponible - MEJORADO
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

        # Reproducir música del menú automáticamente
        if music_paths['menu']:
            print("🎵 Iniciando música del menú...")
            play_music(music_paths['menu'], volume=0.3)
    else:
        print("⚠️ MÚSICA: No se encontraron archivos de música")
        print("📁 Asegúrate de que los archivos estén en: assets/music/")
        print("📋 Nombres requeridos: menu.mp3, juego.mp3, victoria.mp3, derrota.mp3")

    return sounds_loaded, music_count

# ✅ CARGAR AUDIO AL INICIO (¡IMPORTANTE hacerlo antes de usar music_count!)
sounds_count, music_count = load_all_audio()

# ✅ MOSTRAR ESTADO DEL AUDIO DESPUÉS DE CARGAR
print("")
print("📊 ESTADO DEL AUDIO:")
if music_count == 4:
    print("✅ MÚSICA: Completa - Todas las pistas cargadas")
else:
    print(f"⚠️ MÚSICA: {music_count}/4 pistas cargadas")

if sounds_count > 0:
    print(f"✅ SONIDOS: {sounds_count}/8 efectos cargados")
    if sounds_count < 8:
        print("    📋 Ver MUSICA_Y_SONIDOS_PENDIENTES.md para completar sonidos")
else:
    print("⚠️ SONIDOS: Pendientes - Ver MUSICA_Y_SONIDOS_PENDIENTES.md")

if music_count == 4 and sounds_count == 8:
    print("🎉 ¡AUDIO COMPLETO! Tu proyecto está 100% listo para el examen")
elif music_count == 4:
    print("🎵 Música completa - Solo faltan los efectos de sonido")
else:
    print("🔊 Agrega los archivos de audio faltantes para completar el proyecto")

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
        """CORREGIDO: Obtiene la dirección de disparo asistido solo si hay enemigos cerca"""
        if not self.aim_assistance:
            return None
        
        # Si no hay enemigos, no hay dirección de aim
        if not enemies:
            return None
            
        nearest_enemy, distance = self.find_nearest_enemy(player_pos, enemies)
        
        if nearest_enemy and distance <= self.detection_range:
            self.target_enemy = nearest_enemy
            return self.calculate_aim_direction(player_pos, nearest_enemy['pos'])
        
        # No hay enemigos en rango
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

# ========================================
# SISTEMA DE SPRITES MEJORADO Y CORREGIDO
# ========================================

def load_dog_sprite():
    """CORREGIDO: Función para cargar el sprite del perro con escalado automático"""
    global use_sprites, dog_sprites
    
    sprite_path = 'assets/images/perro.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"✅ ¡Sprite del perro encontrado! Cargando desde: {sprite_path}")
            
            # Cargar el sprite
            dog_spritesheet = pygame.image.load(sprite_path)
            
            # Escalar automáticamente al tamaño de celda calculado
            scaled_sprite = pygame.transform.scale(dog_spritesheet, (TILE_SIZE, TILE_SIZE))
            
            # Crear sprites para todas las direcciones
            dog_sprites = {
                'up': [scaled_sprite],
                'right': [scaled_sprite], 
                'down': [scaled_sprite],
                'left': [pygame.transform.flip(scaled_sprite, True, False)]
            }
            
            use_sprites = True
            print(f"🎮 ¡Sprite del perro cargado! Tamaño: {TILE_SIZE}x{TILE_SIZE}")
            return True
        else:
            print(f"📁 No se encontró sprite en: {sprite_path}")
            print("💡 Tip: Crea la carpeta 'assets/images/' y pon tu 'perro.png' ahí")
            return False
            
    except Exception as e:
        print(f"❌ Error cargando sprite: {e}")
        return False

def load_enemy_sprites():
    """CORREGIDO: Función para cargar sprites de criaturas infernales con escalado automático"""
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
                
                # Escalar automáticamente al tamaño de celda
                scaled_sprite = pygame.transform.scale(enemy_spritesheet, (TILE_SIZE, TILE_SIZE))
                
                enemy_sprites[emoji] = {
                    'right': scaled_sprite,
                    'left': pygame.transform.flip(scaled_sprite, True, False)
                }
                
                sprites_loaded += 1
                
        except Exception as e:
            print(f"⚠️ Error cargando {sprite_path}: {e}")
    
    if sprites_loaded > 0:
        print(f"🔥 ¡{sprites_loaded} criaturas cargadas! Tamaño: {TILE_SIZE}x{TILE_SIZE}")
    
    return sprites_loaded > 0

def load_poop_sprite():
    """CORREGIDO: Función para cargar el sprite de caca con escalado automático"""
    global poop_sprite
    
    sprite_path = 'assets/images/caca.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"💩 ¡Sprite de caca encontrado!")
            
            poop_image = pygame.image.load(sprite_path)
            poop_sprite = pygame.transform.scale(poop_image, (TILE_SIZE, TILE_SIZE))
            
            print(f"💩 ¡Sprite de caca cargado! Tamaño: {TILE_SIZE}x{TILE_SIZE}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error cargando sprite de caca: {e}")
        return False

def load_cover_image():
    """CORREGIDO: Función para cargar la portada del juego con escalado automático"""
    global cover_image
    
    sprite_path = 'assets/images/portada.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"🖼️ ¡Portada encontrada!")
            
            cover_raw = pygame.image.load(sprite_path)
            
            # Escalar portada proporcionalmente a la ventana
            cover_width = int(SCREEN_WIDTH * 0.4)  # 40% del ancho de pantalla
            cover_height = int(cover_width * 0.75)  # Mantener proporción 4:3
            
            cover_image = pygame.transform.scale(cover_raw, (cover_width, cover_height))
            
            print(f"🖼️ ¡Portada escalada! Tamaño: {cover_width}x{cover_height}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error cargando portada: {e}")
        return False

def load_wall_sprite():
    """CORREGIDO: Función para cargar el sprite de pared infernal con escalado automático"""
    global wall_sprite
    
    sprite_path = 'assets/images/bloquerojo.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"🧱 ¡Sprite de pared encontrado!")
            
            wall_image = pygame.image.load(sprite_path)
            wall_sprite = pygame.transform.scale(wall_image, (TILE_SIZE, TILE_SIZE))
            
            print(f"🧱 ¡Pared cargada! Tamaño: {TILE_SIZE}x{TILE_SIZE}")
            return True
        else:
            return False
            
    except Exception as e:
        return False

def load_heart_sprite():
    """CORREGIDO: Función para cargar el sprite de corazón con escalado automático"""
    global heart_sprite
    
    sprite_path = 'assets/images/corazon.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"💖 ¡Sprite de corazón encontrado!")
            
            heart_image = pygame.image.load(sprite_path)
            
            # Tamaño de corazón escalado automáticamente
            heart_size = max(25, int(TILE_SIZE * 0.8))
            heart_sprite = pygame.transform.scale(heart_image, (heart_size, heart_size))
            
            print(f"💖 ¡Corazón cargado! Tamaño: {heart_size}x{heart_size}")
            return True
        else:
            return False
            
    except Exception as e:
        return False

def load_diamond_sprite():
    """CORREGIDO: Función para cargar el sprite de diamante con escalado automático"""
    global diamond_sprite
    
    sprite_path = 'assets/images/diamante.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"💎 ¡Sprite de diamante encontrado!")
            
            diamond_image = pygame.image.load(sprite_path)
            diamond_sprite = pygame.transform.scale(diamond_image, (TILE_SIZE, TILE_SIZE))
            
            print(f"💎 ¡Diamante cargado! Tamaño: {TILE_SIZE}x{TILE_SIZE}")
            return True
        else:
            return False
            
    except Exception as e:
        return False

def load_door_sprite():
    """CORREGIDO: Función para cargar el sprite de puerta con escalado automático"""
    global door_sprite
    
    sprite_path = 'assets/images/puerta.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"🚪 ¡Sprite de puerta encontrado!")
            
            door_image = pygame.image.load(sprite_path)
            door_sprite = pygame.transform.scale(door_image, (TILE_SIZE, TILE_SIZE))
            
            print(f"🚪 ¡Puerta cargada! Tamaño: {TILE_SIZE}x{TILE_SIZE}")
            return True
        else:
            return False
            
    except Exception as e:
        return False

def load_humo_sprite():
    """NUEVO: Función para cargar el sprite de humo con escalado automático"""
    global humo_sprite
    
    sprite_path = 'assets/images/humo.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"💨 ¡Sprite de humo encontrado!")
            
            humo_image = pygame.image.load(sprite_path)
            humo_sprite = pygame.transform.scale(humo_image, (TILE_SIZE, TILE_SIZE))
            
            print(f"💨 ¡Humo cargado! Tamaño: {TILE_SIZE}x{TILE_SIZE}")
            return True
        else:
            return False
            
    except Exception as e:
        return False

# ✅ CARGAR SPRITES AL INICIO AUTOMÁTICAMENTE
def load_all_sprites():
    """NUEVO: Carga automáticamente todos los sprites al inicio"""
    print("")
    print("🎨 CARGANDO SPRITES:")
    
    sprites_loaded = 0
    total_sprites = 8  # Actualizado: ahora son 8 sprites
    
    # Cargar cada sprite
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
    if load_humo_sprite():  # NUEVO: Cargar sprite de humo
        sprites_loaded += 1
    
    print(f"")
    print(f"🎨 SPRITES CARGADOS: {sprites_loaded}/{total_sprites + 1}")
    if sprites_loaded > 5:
        print("✅ ¡Sprites principales cargados correctamente!")
    else:
        print("⚠️ Algunos sprites no se encontraron - El juego usará emojis como respaldo")
    
    return sprites_loaded

# ✅ CARGAR TODOS LOS SPRITES AUTOMÁTICAMENTE
sprites_loaded_count = load_all_sprites()

def reload_sprites_if_needed():
    """CORREGIDO: Recarga sprites si no están cargados pero el archivo existe"""
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
    
    # NUEVOS: Recargar sprites adicionales
    if heart_sprite is None:
        load_heart_sprite()
    
    if diamond_sprite is None:
        load_diamond_sprite()
    
    if door_sprite is None:
        load_door_sprite()
    
    # NUEVO: Recargar sprite de humo
    if humo_sprite is None:
        load_humo_sprite()

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
last_direction = [1, 0]  # CORREGIDO: Inicializar con dirección válida (derecha)

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
    """CORREGIDO: Encuentra posiciones válidas con zona de seguridad alrededor del jugador"""
    height = len(maze)
    width = len(maze[0])
    valid_positions = []
    
    # ZONA DE SEGURIDAD: 3x3 alrededor del jugador inicial [1,1]
    player_safe_zone = [
        [0, 0], [1, 0], [2, 0],
        [0, 1], [1, 1], [2, 1], 
        [0, 2], [1, 2], [2, 2]
    ]
    
    # Buscar todas las posiciones válidas (no paredes)
    for y in range(2, height - 2):  # AUMENTADO: Evitar más bordes
        for x in range(2, width - 2):  # AUMENTADO: Evitar más bordes
            if maze[y][x] == 0:  # Camino libre
                # NUEVO: Verificar que no esté en la zona de seguridad del jugador
                if [x, y] not in player_safe_zone:
                    # NUEVO: Verificar que no esté cerca de la salida
                    is_near_exit = False
                    for exit_y in range(height):
                        for exit_x in range(width):
                            if maze[exit_y][exit_x] == 2:  # Salida encontrada
                                distance_to_exit = abs(x - exit_x) + abs(y - exit_y)
                                if distance_to_exit < 3:  # Zona de seguridad de la salida
                                    is_near_exit = True
                                    break
                        if is_near_exit:
                            break
                    
                    if not is_near_exit:
                        valid_positions.append([x, y])
    
    print(f"🎯 Posiciones seguras encontradas: {len(valid_positions)}")
    
    # Mezclar y retornar las primeras 'count' posiciones
    import random
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
    """CORREGIDO: Muestra un mensaje temporal que no bloquea el juego"""
    global temp_message, temp_message_time
    temp_message = message
    temp_message_time = time.time()
    print(f"📢 Mensaje: {message}")

def draw_temp_message():
    """ACTUALIZADO: Dibujar mensaje temporal centrado en cualquier resolución"""
    global temp_message, temp_message_time
    
    if temp_message and time.time() - temp_message_time < temp_message_duration:
        # Calcular transparencia basada en el tiempo restante
        elapsed = time.time() - temp_message_time
        alpha = max(0, 1 - (elapsed / temp_message_duration))
        
        # NUEVO: Adaptable a pantalla completa
        if fullscreen_mode:
            # En pantalla completa, centrar en toda la pantalla
            message_width = SCREEN_WIDTH - 80
            message_height = 100
            message_x = 40
            message_y = (SCREEN_HEIGHT // 2) - (message_height // 2)
            
            # Fuente escalada
            font_scale = max(1.0, min(2.5, SCREEN_WIDTH / 800))
            message_font_size = int(30 * font_scale)
            message_font = pygame.font.SysFont('Arial', message_font_size)
        else:
            # Modo ventana normal
            message_width = SCREEN_WIDTH - 40
            message_height = 80
            message_x = 20
            message_y = (MAZE_HEIGHT * TILE_SIZE // 2) - (message_height // 2)
            message_font = font
        
        # Fondo semi-transparente con borde
        message_surface = pygame.Surface((message_width, message_height))
        message_surface.fill((0, 0, 0))
        message_surface.set_alpha(int(180 * alpha))
        
        # Dibujar fondo con borde dorado
        screen.blit(message_surface, (message_x, message_y))
        border_thickness = max(2, int(3 * (SCREEN_WIDTH / 800)))
        pygame.draw.rect(screen, (255, 215, 0), (message_x - border_thickness, message_y - border_thickness, 
                        message_width + border_thickness * 2, message_height + border_thickness * 2), border_thickness)
        
        # Dibujar texto del mensaje centrado
        text_color = (255, int(255 * alpha), int(255 * alpha))
        text = message_font.render(temp_message, True, text_color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, message_y + message_height // 2))
        screen.blit(text, text_rect)
    elif temp_message and time.time() - temp_message_time >= temp_message_duration:
        # Limpiar mensaje cuando expire
        temp_message = ""

def move_enemies():
    """Mueve enemigos usando IA - SIN SONIDOS INCORRECTOS"""
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
    
    # NOTA: Esta función NO debe reproducir sonidos
    # Los sonidos solo se reproducen cuando:
    # - El jugador dispara (disparo.wav)
    # - El jugador golpea enemigo (golpe.wav)  
    # - El jugador recoge diamante (diamante.wav)
    # - El jugador es golpeado (muerte.wav)
    # - El jugador abre puerta (puerta.wav)

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
                    # Verificar si el enemigo está invisible
                    is_invisible = False
                    if e['type'] == '👻' and i < len(enemy_behaviors):
                        behavior = enemy_behaviors[i]
                        if hasattr(behavior, 'is_currently_invisible'):
                            is_invisible = behavior.is_currently_invisible()
                    
                    # No puede ser golpeado si está invisible
                    if not is_invisible:
                        enemies.remove(e)
                        if i < len(enemy_behaviors):
                            enemy_behaviors.pop(i)
                        player_score += 150  # Bonus por eliminar enemigo
                        
                        # CORREGIDO: Solo reproducir sonido cuando EL JUGADOR golpea a un enemigo
                        play_sound('golpe', volume=0.9)
                        
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

def check_enemy_collision():
    """CORREGIDO: Verifica colisiones SOLO entre jugador y enemigos"""
    global player_score, enemies, enemy_behaviors
    
    # Solo verificar si EL JUGADOR está en la misma posición que un enemigo
    for i, e in enumerate(enemies):
        if e['pos'] == player_pos:  # SOLO verificar posición del jugador
            # Verificar si el enemigo está invisible
            is_invisible = False
            if e['type'] == '👻' and i < len(enemy_behaviors):
                behavior = enemy_behaviors[i]
                if hasattr(behavior, 'is_currently_invisible'):
                    is_invisible = behavior.is_currently_invisible()
            
            # No puede colisionar si está invisible
            if not is_invisible:
                print(f"💥 COLISIÓN: Jugador golpeado por {e['type']} en {e['pos']}")
                return True
    
    return False

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
        
        # DEBUG: Verificar enemigos creados
        print(f"👾 ENEMIGO CREADO: {enemy['pos']} - {enemy['type']}")

def debug_enemy_spawn_positions(maze):
    """NUEVO: Función de debug para verificar posiciones de spawn"""
    print("🔍 DEBUG: Verificando posiciones de spawn de enemigos...")
    
    valid_positions = find_valid_enemy_positions(maze, 20)
    
    print(f"📍 Posiciones válidas encontradas: {len(valid_positions)}")
    print(f"🎯 Primeras 10 posiciones: {valid_positions[:10]}")
    
    # Verificar distancia mínima al jugador
    player_start = [1, 1]
    min_distance = float('inf')
    closest_pos = None
    
    for pos in valid_positions:
        distance = abs(pos[0] - player_start[0]) + abs(pos[1] - player_start[1])
        if distance < min_distance:
            min_distance = distance
            closest_pos = pos
    
    print(f"📏 Posición más cercana al jugador: {closest_pos} (distancia: {min_distance})")
    print(f"✅ Zona de seguridad: {'OK' if min_distance >= 3 else 'PROBLEMA'}")

# ========================================
# FUNCIONES BÁSICAS DEL JUEGO
# ========================================

def handle_bonus_tile(x, y):
    """CORREGIDO: Maneja las bonificaciones - SOLO DIAMANTES"""
    global player_score, maze, collected_diamonds
    
    if maze[y][x] == 3:  # Solo si hay un diamante en esa posición
        player_score += 100
        collected_diamonds += 1
        maze[y][x] = 0  # Eliminar el diamante del mapa
        
        # CORREGIDO: Solo reproducir sonido de diamante
        play_sound('diamante', volume=0.8)
        
        print(f"💎 Diamante recogido en [{x},{y}]! {collected_diamonds}/{total_diamonds}")
        
    # NOTA: Esta función NO debe reproducir sonido de golpe
    # Solo debe sonar 'diamante.wav' cuando se recoge un diamante

# Actualizar dimensiones del laberinto según el nivel actual
def update_maze_dimensions():
    """Actualiza dimensiones - Solo para compatibilidad"""
    global MAZE_WIDTH, MAZE_HEIGHT
    current_maze = levels[current_level]['maze']
    MAZE_HEIGHT = len(current_maze)
    MAZE_WIDTH = len(current_maze[0])
    print(f"🎮 Nivel actualizado: {MAZE_WIDTH}x{MAZE_HEIGHT}")

def draw_maze():
    """Dibuja el laberinto centrado en ventana extendida"""
    # Calcular offset para centrar en ventana extendida
    maze_pixel_width = MAZE_WIDTH * TILE_SIZE
    maze_pixel_height = MAZE_HEIGHT * TILE_SIZE
    offset_x = (SCREEN_WIDTH - maze_pixel_width) // 2
    offset_y = (SCREEN_HEIGHT - maze_pixel_height - 100) // 2
    
    # Asegurar que el laberinto esté visible
    offset_x = max(0, offset_x)
    offset_y = max(0, offset_y)
    
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            screen_x = x * TILE_SIZE + offset_x
            screen_y = y * TILE_SIZE + offset_y
            rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
            
            if maze[y][x] == 1:  # Paredes infernales
                if wall_sprite:
                    scaled_wall = pygame.transform.scale(wall_sprite, (TILE_SIZE, TILE_SIZE))
                    screen.blit(scaled_wall, (screen_x, screen_y))
                else:
                    pygame.draw.rect(screen, COLOR_WALL, rect)
                    pygame.draw.rect(screen, (10, 0, 0), rect, 2)
            elif maze[y][x] == 2:  # Portal de salida
                pygame.draw.rect(screen, COLOR_PATH, rect)
                
                if collected_diamonds >= total_diamonds:
                    # Puerta abierta
                    if door_sprite:
                        scaled_door = pygame.transform.scale(door_sprite, (TILE_SIZE, TILE_SIZE))
                        screen.blit(scaled_door, (screen_x, screen_y))
                        # Efecto de brillo verde
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
                        
            elif maze[y][x] == 3:  # Tesoros infernales
                pygame.draw.rect(screen, COLOR_PATH, rect)
                
                if diamond_sprite:
                    scaled_diamond = pygame.transform.scale(diamond_sprite, (TILE_SIZE, TILE_SIZE))
                    screen.blit(scaled_diamond, (screen_x, screen_y))
                    # Efecto de brillo dorado
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
            else:  # Suelo infernal
                pygame.draw.rect(screen, COLOR_PATH, rect)
                if (x + y) % 4 == 0:
                    pygame.draw.rect(screen, (90, 45, 45), rect, 1)

def draw_player():
    """Dibuja al jugador centrado en ventana extendida"""
    x, y = player_pos
    
    # Calcular offset igual que en draw_maze
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
    """Dibuja enemigos centrados en ventana extendida"""
    # Calcular offset igual que en draw_maze
    maze_pixel_width = MAZE_WIDTH * TILE_SIZE
    maze_pixel_height = MAZE_HEIGHT * TILE_SIZE
    offset_x = (SCREEN_WIDTH - maze_pixel_width) // 2
    offset_y = (SCREEN_HEIGHT - maze_pixel_height - 100) // 2
    offset_x = max(0, offset_x)
    offset_y = max(0, offset_y)
    
    for i, enemy in enumerate(enemies):
        x, y = enemy["pos"]
        enemy_type = enemy["type"]
        
        # Verificar invisibilidad
        is_invisible = False
        if enemy_type == '👻' and i < len(enemy_behaviors):
            behavior = enemy_behaviors[i]
            if hasattr(behavior, 'is_currently_invisible'):
                is_invisible = behavior.is_currently_invisible()
        
        screen_x = x * TILE_SIZE + offset_x
        screen_y = y * TILE_SIZE + offset_y
        
        if is_invisible:
            # NUEVO: Mostrar sprite de humo si está disponible
            if humo_sprite:
                scaled_humo = pygame.transform.scale(humo_sprite, (TILE_SIZE, TILE_SIZE))
                screen.blit(scaled_humo, (screen_x, screen_y))
            else:
                # Fallback: emoji de humo
                humo_emoji = emoji_font.render('💨', True, (200, 200, 200))
                screen.blit(humo_emoji, (screen_x + 4, screen_y))
        else:
            # Mostrar enemigo normal
            enemy_dir = enemy.get("dir", [1, 0])
            sprite_direction = 'left' if enemy_dir[0] < 0 else 'right'
            
            if enemy_type in enemy_sprites:
                scaled_enemy = pygame.transform.scale(enemy_sprites[enemy_type][sprite_direction], (TILE_SIZE, TILE_SIZE))
                screen.blit(scaled_enemy, (screen_x, screen_y))
            else:
                enemy_emoji = emoji_font.render(enemy_type, True, (0, 0, 0))
                screen.blit(enemy_emoji, (screen_x + 4, screen_y))

def draw_projectiles():
    """Dibuja proyectiles centrados en ventana extendida"""
    # Calcular offset igual que en draw_maze
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
            scaled_poop = pygame.transform.scale(poop_sprite, (TILE_SIZE, TILE_SIZE))
            screen.blit(scaled_poop, (screen_x, screen_y))
        else:
            poop = emoji_font.render('💩', True, (0, 0, 0))
            screen.blit(poop, (screen_x + 4, screen_y))

def draw_ui():
    """UI en ventana extendida"""
    # UI en la parte inferior de la ventana extendida
    ui_start_y = SCREEN_HEIGHT - 90
    
    # ========================================
    # SECCIÓN SUPERIOR: INFORMACIÓN BÁSICA
    # ========================================
    
    # Información del nivel (esquina superior izquierda)
    level_info = f"Dimensión: {current_level + 1} - {levels[current_level]['name']}"
    level_text = small_font.render(level_info, True, COLOR_BONUS)
    screen.blit(level_text, (10, ui_start_y))
    
    # ========================================
    # SECCIÓN CORAZONES: MÁS GRANDES Y PROMINENTES
    # ========================================
    
    # Corazones más grandes en la esquina superior derecha
    hearts_x = SCREEN_WIDTH - 150
    hearts_y = ui_start_y
    
    # Texto "Vida:" 
    lives_label = small_font.render("Vida:", True, COLOR_FIRE)
    screen.blit(lives_label, (hearts_x - 50, hearts_y + 8))
    
    if heart_sprite:
        # Usar sprites de corazón MÁS GRANDES (35x35)
        large_heart_sprite = pygame.transform.scale(heart_sprite, (35, 35))
        for i in range(player_lives):
            screen.blit(large_heart_sprite, (hearts_x + i * 40, hearts_y))
    else:
        # Respaldo con emojis más grandes
        large_emoji_font = pygame.font.SysFont('Segoe UI Emoji', 35)
        for i in range(player_lives):
            heart_emoji = large_emoji_font.render('💖', True, COLOR_FIRE)
            screen.blit(heart_emoji, (hearts_x + i * 40, hearts_y))
    
    # ========================================
    # SECCIÓN MEDIA: ESTADÍSTICAS PRINCIPALES
    # ========================================
    
    section_y = ui_start_y + 30  # Más espacio después de los corazones
    
    # Puntuación de almas (izquierda)
    score_text = small_font.render(f"Almas: {player_score}", True, COLOR_TEXT)
    screen.blit(score_text, (10, section_y))
    
    # Estado de diamantes (centro)
    diamonds_remaining = total_diamonds - collected_diamonds
    if diamonds_remaining > 0:
        diamond_color = (255, 100, 100)  # Rojo si faltan diamantes
        diamond_status = f"💎 {collected_diamonds}/{total_diamonds} (faltan {diamonds_remaining}) 🔒"
    else:
        diamond_color = (100, 255, 100)  # Verde si están completos
        diamond_status = f"💎 {collected_diamonds}/{total_diamonds} ✅ 🚪 ABIERTA"
    
    diamond_text = small_font.render(diamond_status, True, diamond_color)
    screen.blit(diamond_text, (200, section_y))
    
    # Información de enemigos
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
        enemy_info += f" ({invisible_count} 💨)"
    
    enemy_text = small_font.render(enemy_info, True, COLOR_FIRE)
    screen.blit(enemy_text, (600, section_y))
    
    # ========================================
    # SECCIÓN INFERIOR: INFORMACIÓN DE COMBATE
    # ========================================
    
    combat_y = section_y + 25
    
    # Información de proyectiles (centro)
    projectile_info = f"💩 Proyectiles: {len(projectiles)}/3"
    projectile_color = COLOR_FIRE if len(projectiles) < 3 else (255, 100, 100)
    projectile_text = small_font.render(projectile_info, True, projectile_color)
    screen.blit(projectile_text, (10, combat_y))
    
    # Información de aim bot (derecha)
    if aim_bot.aim_assistance:
        if aim_bot.target_enemy:
            aim_status = "🎯 ACTIVO"
            aim_color = (0, 255, 0)  # Verde cuando está apuntando
        else:
            aim_status = "🎯 ESPERANDO"
            aim_color = COLOR_FIRE  # Naranja cuando está esperando enemigos
    else:
        aim_status = "🎯 MANUAL"
        aim_color = (100, 100, 100)  # Gris cuando está desactivado
    
    aim_text = small_font.render(aim_status, True, aim_color)
    screen.blit(aim_text, (200, combat_y))
    
    # ========================================
    # SECCIÓN CONTROLES: INFORMACIÓN COMPACTA
    # ========================================
    
    # Información de controles más compacta
    if controller_connected:
        control_text = f"🎮 Xbox360 | {levels[current_level]['difficulty']} | {FPS}FPS | A=disparar(siempre) B=salir | +/-=tamaño F11=pantalla"
    else:
        control_text = f"⌨️ Teclado | {levels[current_level]['difficulty']} | {FPS}FPS | ESPACIO=disparar(siempre) A=aim +/-=tamaño F11=pantalla"
    
    info_color = COLOR_FIRE if controller_connected else COLOR_TEXT
    info_text_surface = small_font.render(control_text, True, info_color)
    screen.blit(info_text_surface, (400, combat_y))

def draw_menu():
    """Menú principal con ventana extendida"""
    # Fondo infernal degradado
    screen.fill((20, 0, 0))
    
    # Mostrar portada si está disponible
    if cover_image:
        # Centrar la portada en la parte superior
        cover_x = (SCREEN_WIDTH - cover_image.get_width()) // 2
        cover_y = 30
        screen.blit(cover_image, (cover_x, cover_y))
        title_y = cover_y + cover_image.get_height() + 30
    else:
        # Título con tema infernal
        title = font.render("🔥 DIMENSIONES INFERNALES 🔥", True, COLOR_FIRE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))
        subtitle = small_font.render("- Sistema de IA Demoníaca -", True, COLOR_BONUS)
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 80))
        title_y = 130
    
    # ========================================
    # SECCIÓN OPCIONES DEL MENÚ
    # ========================================
    
    # SOLO dibujar las 3 opciones del menú con estilo infernal
    valid_options = ['🚪 Nueva Partida', '⚙️ Dificultad', '❌ Salir']
    for i, option in enumerate(valid_options):
        option_y = title_y + i * 50
        
        if i == menu_idx:
            color = COLOR_FIRE  # Naranja fuego para opción seleccionada
            # Efecto de brillo para opción seleccionada
            shadow_text = font.render(option, True, (100, 0, 0))
            screen.blit(shadow_text, (SCREEN_WIDTH // 2 - shadow_text.get_width() // 2 + 2, option_y + 2))
            
            # Indicador de selección
            indicator = "► "
            indicator_text = font.render(indicator, True, COLOR_FIRE)
            screen.blit(indicator_text, (SCREEN_WIDTH // 2 - font.size(option)[0] // 2 - 40, option_y))
        else:
            color = (150, 75, 75)  # Rojo oscuro para opciones no seleccionadas
        
        text = font.render(option, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, option_y))
    
    # ========================================
    # SECCIÓN INFORMACIÓN DE CONTROLES (SIMPLIFICADA)
    # ========================================
    
    controls_y = title_y + 200  # Más espacio después de las opciones
    
    # Información de controles más simple y clara
    control_lines = [
        "🎮 CONTROLES:",
        "Xbox 360: A=aceptar | B=atrás | Joystick=navegar",
        "Teclado: Enter=aceptar | ESC=atrás | Flechas=navegar",
        "F11=Pantalla completa | +/- = Ajustar laberinto"
    ]
    
    for i, line in enumerate(control_lines):
        color = COLOR_FIRE if i == 0 else COLOR_TEXT
        font_to_use = small_font if i > 0 else font
        text = font_to_use.render(line, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, controls_y + i * 30))
    
    # ========================================
    # SECCIÓN INFORMACIÓN DEL JUEGO (COMPACTA)
    # ========================================
    
    info_y = controls_y + 120
    
    # Información más compacta del juego
    game_info = [
        "🎯 OBJETIVO: Recolecta TODOS los diamantes 💎 para abrir las puertas 🚪",
        "👹 ENEMIGOS: 7 tipos de criaturas infernales con IA única",
        "💩 DISPARO: Siempre puedes disparar (ESPACIO/A) - Presiona A para aim bot",
        "🎮 Sprites personalizados para mejor experiencia visual"
    ]
    
    for i, info in enumerate(game_info):
        color = COLOR_BONUS if i == 0 else (200, 150, 100)
        text = small_font.render(info, True, color)
        # Centrar cada línea
        text_x = (SCREEN_WIDTH - text.get_width()) // 2
        screen.blit(text, (text_x, info_y + i * 25))
    
    # ========================================
    # EFECTOS VISUALES SUTILES
    # ========================================
    
    # Efectos de partículas infernales más sutiles
    import random
    for _ in range(3):  # Menos partículas para no distraer
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 50)
        alpha = random.randint(50, 150)
        
        # Crear superficie con transparencia
        particle_surface = pygame.Surface((4, 4))
        particle_surface.fill((255, 100, 0))
        particle_surface.set_alpha(alpha)
        screen.blit(particle_surface, (x, y))
    
    pygame.display.flip()

def draw_difficulty_menu():
    """Menú de dificultad"""
    # Fondo infernal
    screen.fill((20, 0, 0))
    
    # ========================================
    # TÍTULO
    # ========================================
    
    title = font.render("🔥 Elige tu nivel de tortura:", True, COLOR_FIRE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
    
    # ========================================
    # OPCIONES DE DIFICULTAD
    # ========================================
    
    # Opciones de dificultad con tema infernal
    infernal_options = ['😈 Alma Perdida (Fácil)', '👹 Demonio (Medio)', '🔥 Señor del Infierno (Difícil)']
    
    for i, opt in enumerate(infernal_options):
        option_y = 180 + i * 60
        
        if i == diff_idx:
            color = COLOR_FIRE
            # Efecto de brillo para opción seleccionada
            shadow_text = font.render(opt, True, (100, 0, 0))
            screen.blit(shadow_text, (SCREEN_WIDTH // 2 - shadow_text.get_width() // 2 + 2, option_y + 2))
            
            # Indicador de selección
            indicator = "► "
            indicator_text = font.render(indicator, True, COLOR_FIRE)
            screen.blit(indicator_text, (SCREEN_WIDTH // 2 - font.size(opt)[0] // 2 - 40, option_y))
        else:
            color = (150, 75, 75)
        
        txt = font.render(opt, True, color)
        screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, option_y))
    
    # ========================================
    # INFORMACIÓN DE VELOCIDAD
    # ========================================
    
    speed_y = 400
    
    # Información de velocidad más clara
    speed_info = [
        f"⚡ VELOCIDADES:",
        f"😈 Alma Perdida: {FPS_levels['Fácil']} FPS - Demonios lentos",
        f"👹 Demonio: {FPS_levels['Medio']} FPS - Velocidad equilibrada", 
        f"🔥 Señor del Infierno: {FPS_levels['Difícil']} FPS - Máxima furia"
    ]
    
    for i, info in enumerate(speed_info):
        if i == 0:
            color = COLOR_FIRE
            font_to_use = font
        elif i == diff_idx + 1:
            color = COLOR_FIRE  # Resaltar la opción seleccionada
            font_to_use = small_font
        else:
            color = (150, 100, 100)
            font_to_use = small_font
            
        text = font_to_use.render(info, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, speed_y + i * 30))
    
    # ========================================
    # INSTRUCCIONES
    # ========================================
    
    instructions_y = speed_y + 150
    
    # Instrucciones de navegación
    back_text = small_font.render("Enter=aceptar | ESC/B=volver | Flechas=navegar", True, COLOR_BONUS)
    screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, instructions_y))
    
    pygame.display.flip()

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
    
    # CORREGIDO: Recargar laberinto ORIGINAL del nivel inicial (con diamantes)
    import copy
    maze = copy.deepcopy(levels[current_level]['maze'])  # Copia profunda para no modificar el original
    projectiles = []
    
    # Actualizar dimensiones de pantalla
    update_maze_dimensions()
    
    # Inicializar pathfinder ANTES de generar enemigos
    pathfinder = AStar(maze)
    
    # Generar enemigos DESPUÉS de inicializar pathfinder (esto también resetea diamantes)
    reset_enemies()
    
    print(f"🔄 Juego reiniciado - Nivel {current_level + 1}")
    print(f"💎 Diamantes en nivel: {total_diamonds} (LABERINTO ORIGINAL RECARGADO)")

def reset_enemies():
    """Resetea enemigos de forma aleatoria según el nivel actual"""
    global enemies, enemy_behaviors, pathfinder, total_diamonds, collected_diamonds, maze
    
    # CORREGIDO: Recargar laberinto original antes de contar diamantes
    import copy
    maze = copy.deepcopy(levels[current_level]['maze'])  # Asegurar laberinto fresco
    
    # RESETEAR SISTEMA DE DIAMANTES
    total_diamonds = count_diamonds_in_level(maze)
    collected_diamonds = 0
    print(f"💎 Nivel {current_level + 1}: {total_diamonds} diamantes totales - TODOS REQUERIDOS")
    
    # Asegurar pathfinder con laberinto fresco
    pathfinder = AStar(maze)
    
    # NUEVO: Debug de posiciones antes de generar enemigos
    debug_enemy_spawn_positions(maze)
    
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
        # CORREGIDO: Recargar laberinto ORIGINAL del nuevo nivel
        import copy
        maze = copy.deepcopy(levels[current_level]['maze'])  # Copia profunda
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
        # NUEVO: Música de victoria al completar todos los niveles
        if music_paths and music_paths['victory']:
            stop_music()
            play_music(music_paths['victory'], loop=0, volume=0.7)
        
        show_message(f"🏆 ¡Has conquistado todas las dimensiones infernales! 🏆")
        show_message(f"💎 Almas recolectadas: {player_score} 💎")
        reset_game()
        reset_menu()  # ASEGURAR menú limpio
        game_state = STATE_MENU
        
        # NUEVO: Volver a música del menú después de victoria
        if music_paths and music_paths['menu']:
            play_music(music_paths['menu'], volume=0.3)

# Inicialización
print("")
print("🎮 INICIALIZANDO COMPONENTES FINALES:")

# ✅ CARGAR SPRITES AUTOMÁTICAMENTE AL INICIO
print("🎨 Cargando sprites automáticamente...")

# ✅ CARGAR TODOS LOS SPRITES AL INICIO
sprites_loaded_count = load_all_sprites()

print("🔧 PROBLEMAS CORREGIDOS:")
print("   ✅ Bug de diamantes: Ahora reaparecen en nueva partida")
print("   ✅ Tamaño del laberinto: Aumentado para mejor visibilidad")
print("   ✅ Sprites: Carga automática al inicio del juego")
print("   ✅ Audio: Integrada solución de ChatGPT")

# ✅ INICIALIZAR PATHFINDER
pathfinder = AStar(levels[current_level]['maze'])

clock = pygame.time.Clock()
if 'enemies' in globals() and enemies:
    initialize_enemy_behaviors()

# ✅ GENERAR ENEMIGOS INICIALES
reset_enemies()

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
            # Control de pantalla completa (funciona en todos los estados)
            if event.key == pygame.K_F11:
                toggle_fullscreen()
            elif event.key == pygame.K_F4 and fullscreen_mode:
                # F4 para salir de pantalla completa
                toggle_fullscreen()
            # Controles para ajustar tamaño del laberinto
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                adjust_tile_size(increase=True)  # + para agrandar
            elif event.key == pygame.K_MINUS:
                adjust_tile_size(increase=False)  # - para encoger
            
            # Manejo ESTRICTO del menú (SOLO 3 opciones válidas)
            if game_state == STATE_MENU:
                # Limitar navegación a SOLO 3 opciones
                if event.key == pygame.K_UP:
                    menu_idx = (menu_idx - 1) % 3  # MÁXIMO 3 opciones
                elif event.key == pygame.K_DOWN:
                    menu_idx = (menu_idx + 1) % 3  # MÁXIMO 3 opciones
                elif event.key == pygame.K_RETURN:
                    # NUEVO: Sonido de click en menú
                    play_sound('click', volume=0.5)
                    
                    # Manejo DIRECTO por índice (sin referencias a strings)
                    if menu_idx == 0:  # Nueva Partida
                        reset_game()
                        update_maze_dimensions()
                        
                        # NUEVO: Cambiar a música de juego
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
                    # NUEVO: Sonido de click
                    play_sound('click', volume=0.5)
                    
                    FPS = FPS_levels[difficulty_options[diff_idx]]
                    reset_menu()  # ASEGURAR menú limpio
                    game_state = STATE_MENU
                elif event.key == pygame.K_ESCAPE:
                    # NUEVO: Sonido de click
                    play_sound('click', volume=0.5)
                    
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
            # NUEVO: Sonido de click con control
            play_sound('click', volume=0.5)
            
            if menu_idx == 0:  # Nueva Partida
                reset_game()
                update_maze_dimensions()
                
                # NUEVO: Cambiar a música de juego
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
        # Navegación con joystick/D-pad
        if abs(controller_move[1]) > 0.5:  # Movimiento vertical significativo
            if controller_move[1] < 0:  # Arriba
                diff_idx = (diff_idx - 1) % len(difficulty_options)
            else:  # Abajo
                diff_idx = (diff_idx + 1) % len(difficulty_options)
            time.sleep(0.15)  # Pequeña pausa para evitar navegación muy rápida
        
        # Aceptar con botón A
        if controller_a_menu:
            # NUEVO: Sonido de click
            play_sound('click', volume=0.5)
            
            FPS = FPS_levels[difficulty_options[diff_idx]]
            reset_menu()  # ASEGURAR menú limpio
            game_state = STATE_MENU
        
        # Retroceder con botón B
        if controller_b:
            # NUEVO: Sonido de click
            play_sound('click', volume=0.5)
            
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
            
            # CORREGIDO: Solo manejar bonificaciones si realmente nos movemos
            old_pos = player_pos.copy()
            player_pos = new_pos
            
            # Solo verificar bonificaciones si cambió de posición
            if old_pos != player_pos:
                handle_bonus_tile(new_pos[0], new_pos[1])
            
        # Si el movimiento no es válido, mantener posición anterior (sin sonidos)
        
        # Asegurar dirección válida para disparar
        ensure_valid_shooting_direction()
        
        # MEJORADO: Sistema de disparo más responsivo
        can_shoot = len(projectiles) < 3  # REDUCIDO de 5 a 3 para mejor responsividad
        
        # TECLADO: Disparo con ESPACIO (con debounce mejorado)
        current_space_pressed = keys[pygame.K_SPACE]
        keyboard_shoot = current_space_pressed and not last_space_state
        last_space_state = current_space_pressed
        
        if (controller_shoot or keyboard_shoot) and can_shoot:
            # CORREGIDO: SIEMPRE disparar, con o sin enemigos
            
            # 1. Obtener dirección de aim bot si está activo Y hay enemigos
            aim_direction = None
            if aim_bot.aim_assistance:
                aim_direction = aim_bot.get_aim_direction(player_pos, enemies)
            
            # 2. Determinar dirección final de disparo
            if aim_direction:
                # Usar aim bot si encontró enemigo
                final_direction = aim_direction
                disparo_tipo = "GUIADO"
            else:
                # Disparo manual - usar última dirección de movimiento
                final_direction = last_direction.copy()
                
                # NUEVO: Si la dirección es inválida, usar dirección actual del sprite
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
                        final_direction = [1, 0]  # Derecha por defecto
                
                disparo_tipo = "MANUAL"
            
            # 3. SIEMPRE crear el proyectil
            projectiles.append({'pos': player_pos.copy(), 'dir': final_direction})
            
            # 4. Reproducir sonido de disparo
            play_sound('disparo', volume=0.6)
            
            # 5. Debug mejorado
            print(f"💥 Proyectil {disparo_tipo} creado: {final_direction}")
            print(f"📊 Proyectiles activos: {len(projectiles)}/3")
            
        elif (controller_shoot or keyboard_shoot) and not can_shoot:
            print("⚠️ Máximo de proyectiles alcanzado (3/3)")
        
        # Toggle aim bot (solo teclado) - MEJORADO
        if keys[pygame.K_a]:
            aim_bot.aim_assistance = not aim_bot.aim_assistance
            status = "ACTIVADO" if aim_bot.aim_assistance else "DESACTIVADO"
            print(f"🎯 Aim bot {status}")
            show_temp_message(f"Aim bot {status}")
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
                
                # NUEVO: Reproducir sonido de puerta
                play_sound('puerta', volume=0.8)
                
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
            
            # CORREGIDO: Reproducir sonido solo cuando el JUGADOR es golpeado
            play_sound('muerte', volume=0.8)
            
            # NUEVO: Limpiar mensaje temporal
            temp_message = ""
            temp_message_time = 0
            last_button_a_state = False
            last_button_b_state = False
            last_space_state = False
            
            if player_lives <= 0:
                # NUEVO: Música de derrota
                if music_paths and music_paths['defeat']:
                    stop_music()
                    play_music(music_paths['defeat'], loop=0, volume=0.6)
                
                show_message(f"💀 Tu alma ha sido devorada 💀")
                show_message(f"🔥 Almas perdidas: {player_score} 🔥")
                reset_game()
                reset_menu()  # ASEGURAR menú limpio
                game_state = STATE_MENU
                
                # NUEVO: Volver a música del menú
                if music_paths and music_paths['menu']:
                    play_music(music_paths['menu'], volume=0.3)
            else:
                show_message(f"😈 ¡Los demonios te han atrapado! Vida restante: {player_lives} 💖")
        
        # Dibujar todo
        screen.fill(COLOR_BACKGROUND)
        draw_maze()  # Ahora con sprites personalizados
        draw_player()
        draw_enemies()  # Ya no dibuja fantasmas invisibles
        draw_projectiles()
        draw_ui()  # UI mejorada con sprites
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
            
            # NUEVO: Volver a música del menú
            if music_paths and music_paths['menu']:
                stop_music()
                play_music(music_paths['menu'], volume=0.3)
            
            game_state = STATE_MENU
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()