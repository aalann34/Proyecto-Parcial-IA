# ========================================
# PERRO HÉROE - ESTRUCTURA ASSETS (EXAMEN)
# ========================================
# Protagonista: Sprite del perro + sprites de enemigos + sprite de caca + portada
# Estructura: assets/images/, assets/sounds/, assets/music/
# Cumple requisitos del examen parcial de IA
# ========================================

import pygame
import sys
import random
import time
from scripts import AStar, create_enemy_behavior

# Inicializar Pygame
pygame.init()

# ========================================
# NIVELES SIMPLIFICADOS - 5 NIVELES FUNCIONALES
# ========================================
# Solo elementos básicos: 0=camino, 1=pared, 2=salida, 3=bonus

levels = [
    # NIVEL 1 - INTRODUCCIÓN
    {
        'id': 1,
        'name': 'Primer Paso',
        'difficulty': 'Fácil',
        'description': 'El perro héroe comienza su aventura',
        'maze': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,3,0,0,1],
            [1,0,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1],
            [1,0,1,0,0,0,0,1,0,1,0,1,0,0,0,0,0,1,0,1],
            [1,0,1,0,1,1,0,1,0,1,0,1,0,1,1,3,0,1,0,1],
            [1,0,1,0,1,3,0,0,0,0,0,0,0,0,0,1,0,1,0,1],
            [1,0,1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1,0,1],
            [1,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
            [1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,2,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    },

    # NIVEL 2 - CORREGIDO
    {
        'id': 2,
        'name': 'Laberinto Básico',
        'difficulty': 'Intermedio',
        'description': 'El perro explora laberintos más complejos',
        'maze': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,3,0,0,0,0,1,0,0,0,0,0,3,0,0,0,1],
            [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,0,1],
            [1,0,1,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,1],
            [1,0,1,0,1,1,0,1,1,1,0,1,1,1,0,1,0,1,0,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,1,1,0,1,0,1,1,0,1,0,1,1,0,1,0,1,1,1,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,2,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    },

    # NIVEL 3 - SIMPLIFICADO
    {
        'id': 3,
        'name': 'Desafío Medio',
        'difficulty': 'Avanzado',
        'description': 'El perro enfrenta más obstáculos',
        'maze': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1],
            [1,0,1,1,1,1,0,1,1,1,1,0,1,1,1,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,0,1,0,0,0,0,0,3,0,1,0,1],
            [1,0,1,0,1,1,1,1,0,1,0,1,1,1,0,1,0,1,0,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
            [1,1,1,0,1,0,1,1,1,0,1,1,0,1,0,1,1,1,0,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
            [1,0,1,0,1,1,1,1,0,1,1,1,1,1,0,1,0,1,0,1],
            [1,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1,0,1],
            [1,0,1,1,1,1,0,1,1,1,1,0,1,1,1,1,0,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1],
        ]
    },

    # NIVEL 4 - ALIEN, FANTASMA, ZOMBIE, VILLANO
    {
        'id': 4,
        'name': 'Laberinto Avanzado',
        'difficulty': 'Experto',
        'description': 'Aventura desafiante para el perro héroe',
        'maze': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,3,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,3,1],
            [1,0,1,0,1,0,1,1,0,1,0,1,1,0,1,0,1,1,0,1],
            [1,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1,0,1],
            [1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,1,0,1],
            [1,0,0,0,1,0,0,0,1,3,1,0,0,0,1,0,0,0,0,1],
            [1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,1,0,1],
            [1,0,1,0,1,1,1,0,1,0,1,0,1,1,1,0,1,1,0,1],
            [1,0,0,0,1,3,0,0,0,0,0,0,0,3,1,0,0,0,0,1],
            [1,1,1,0,1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    },

    # NIVEL 5 - TODOS LOS ENEMIGOS
    {
        'id': 5,
        'name': 'Desafío Final',
        'difficulty': 'Maestro',
        'description': 'La prueba definitiva del perro héroe',
        'maze': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,3,0,0,1,0,0,0,0,1,1,0,0,0,0,1,0,0,0,1],
            [1,0,1,0,1,0,1,1,0,1,0,1,0,1,1,0,1,0,1,1],
            [1,0,1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1,0],
            [1,0,1,1,1,0,1,0,1,1,1,1,0,1,0,1,1,1,1,0],
            [1,0,0,0,1,0,0,0,1,3,0,1,0,0,0,1,0,0,0,0],
            [1,1,1,0,1,1,1,0,1,1,0,1,0,1,1,1,0,1,1,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0],
            [1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,0],
            [1,0,1,0,0,0,0,0,1,0,1,0,1,0,0,0,0,1,1,0],
            [1,0,1,0,1,1,1,0,1,0,1,0,1,0,1,1,1,0,1,0],
            [1,0,0,0,1,3,0,0,0,0,1,0,0,0,0,3,1,0,0,0],
            [1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,1],
            [1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
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
pygame.display.set_caption("🐶 Perro Héroe - Examen Parcial IA")

# Configuración de fuentes
pygame.font.init()
font = pygame.font.SysFont('Arial', 30)
small_font = pygame.font.SysFont('Arial', 20)
emoji_font = pygame.font.SysFont('Segoe UI Emoji', TILE_SIZE)

# Colores del juego
COLOR_WALL = (40, 40, 40)
COLOR_PATH = (200, 200, 200)
COLOR_BACKGROUND = (0, 0, 0)
COLOR_PLAYER = (255, 255, 0)
COLOR_EXIT = (0, 255, 0)
COLOR_ENEMY = (255, 0, 0)
COLOR_TEXT = (255, 255, 255)

# Game states (SOLO 3 ESTADOS)
STATE_MENU = 'MENU'
STATE_DIFF = 'DIFFICULTY'
STATE_PLAY = 'PLAY'

# Menú principal simplificado (SOLO 3 OPCIONES)
menu_options = ['Nueva Partida', 'Seleccionar Dificultad', 'Salir']
difficulty_options = ['Fácil', 'Medio', 'Difícil']
FPS_levels = {'Fácil': 5, 'Medio': 8, 'Difícil': 12}

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
print("🐶 Perro héroe inicializado con emoji")

# Variables para sprites
use_sprites = False
dog_sprites = {}
enemy_sprites = {}  # Sprites de enemigos
poop_sprite = None  # NUEVO: Sprite de caca
cover_image = None  # NUEVO: Portada del juego
current_direction = 'right'

def load_dog_sprite():
    """Función para cargar el sprite del perro si existe"""
    global use_sprites, dog_sprites
    
    sprite_path = 'assets/images/perro.png'
    
    try:
        import os
        if os.path.exists(sprite_path):
            print(f"✅ ¡Sprite encontrado! Cargando desde: {sprite_path}")
            
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
    """Función para cargar sprites de enemigos"""
    global enemy_sprites
    
    # Lista de enemigos con sus archivos correspondientes
    enemy_files = {
        '👻': 'fantasma.png',
        '👽': 'alien.png',
        '🧟': 'zombie.png',
        '🦹': 'villano.png',
        '👺': 'demonio.png',
        '🤡': 'payaso.png'
    }
    
    sprites_loaded = 0
    
    for emoji, filename in enemy_files.items():
        sprite_path = f'assets/images/{filename}'
        
        try:
            import os
            if os.path.exists(sprite_path):
                print(f"👾 Cargando enemigo: {sprite_path}")
                
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
        print(f"🎭 ¡{sprites_loaded} sprites de enemigos cargados!")
    else:
        print("📁 No se encontraron sprites de enemigos")
        print("💡 Tip: Puedes agregar: fantasma.png, alien.png, zombie.png, etc. en assets/images/")
    
    return sprites_loaded > 0

def load_poop_sprite():
    """NUEVO: Función para cargar el sprite de caca"""
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
    """NUEVO: Función para cargar la portada del juego"""
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

# Intentar cargar sprites al iniciar
load_dog_sprite()
load_enemy_sprites()
load_poop_sprite()  # NUEVO: Cargar sprite de caca
load_cover_image()  # NUEVO: Cargar portada

# Función para recargar sprites durante el juego (opcional)
def reload_sprites_if_needed():
    """Recarga sprites si no están cargados pero el archivo existe"""
    global use_sprites
    if not use_sprites:
        load_dog_sprite()
    
    # También recargar sprites de enemigos
    load_enemy_sprites()
    
    # NUEVO: Recargar sprite de caca
    if poop_sprite is None:
        load_poop_sprite()
    
    # NUEVO: Recargar portada
    if cover_image is None:
        load_cover_image()

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

# ========================================
# FUNCIONES BÁSICAS DEL JUEGO
# ========================================

def handle_bonus_tile(x, y):
    """Maneja solo las bonificaciones"""
    global player_score, maze
    
    if maze[y][x] == 3:  # Bonus
        player_score += 100
        maze[y][x] = 0  # Eliminar el bonus del mapa

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

# ========================================
# CONFIGURACIÓN DE ENEMIGOS POR NIVEL
# ========================================

# Definir qué enemigos aparecen en cada nivel
LEVEL_ENEMIES = {
    0: [],  # Nivel 1 - Sin enemigos
    1: [{'type': '👽', 'pos': [18, 1]}],  # Nivel 2 - Solo Alien
    2: [{'type': '👽', 'pos': [18, 1]}, {'type': '👻', 'pos': [1, 10]}],  # Nivel 3 - Alien + Fantasma
    3: [  # Nivel 4 - Alien, Fantasma, Zombie, Villano
        {'type': '👽', 'pos': [18, 1]},   # Alien (A* inteligente)
        {'type': '👻', 'pos': [1, 10]},   # Fantasma (evade)
        {'type': '🧟', 'pos': [10, 6]},   # Zombie (aleatorio)
        {'type': '🦹', 'pos': [5, 8]}     # Villano (emboscada)
    ],
    4: [  # Nivel 5 - TODOS los enemigos
        {'type': '👽', 'pos': [18, 1]},   # Alien (A* inteligente)
        {'type': '👻', 'pos': [1, 10]},   # Fantasma (evade)
        {'type': '🧟', 'pos': [10, 6]},   # Zombie (aleatorio)
        {'type': '🦹', 'pos': [5, 8]},    # Villano (emboscada)
        {'type': '👺', 'pos': [15, 10]},  # Demonio (teletransporte)
        {'type': '🤡', 'pos': [3, 3]}     # Payaso (trampas + errático)
    ]
}

# Enemigos mejorados
enemy_types = ['👻', '👽', '🧟', '🦹', '👺', '🤡']
enemies = []

# Sistema de comportamientos de IA
enemy_behaviors = []

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

# Funciones de dibujo actualizadas
def draw_menu():
    # Asegurar que la pantalla tenga el tamaño correcto para el menú
    menu_width = 800
    menu_height = 600
    if SCREEN_WIDTH != menu_width or SCREEN_HEIGHT != menu_height:
        global screen
        screen = pygame.display.set_mode((menu_width, menu_height))
    
    screen.fill(COLOR_BACKGROUND)
    
    # NUEVO: Mostrar portada si está disponible
    if cover_image:
        # Centrar la portada en la parte superior
        cover_x = (menu_width - cover_image.get_width()) // 2
        cover_y = 20
        screen.blit(cover_image, (cover_x, cover_y))
        title_y = cover_y + cover_image.get_height() + 20
    else:
        # Si no hay portada, mostrar título normal
        title = font.render("🐶 PERRO HÉROE - AVENTURA PIXELART", True, COLOR_TEXT)
        screen.blit(title, (menu_width // 2 - title.get_width() // 2, 50))
        title_y = 120
    
    # SOLO dibujar las 3 opciones del menú
    valid_options = ['Nueva Partida', 'Seleccionar Dificultad', 'Salir']
    for i, option in enumerate(valid_options):
        color = (255, 255, 255) if i == menu_idx else (150, 150, 150)
        text = font.render(option, True, color)
        screen.blit(text, (menu_width // 2 - text.get_width() // 2, title_y + i * 50))
    
    # Información de IA por nivel
    info_lines = [
        "🧠 SISTEMA DE INTELIGENCIA ARTIFICIAL:",
        "Nivel 1: Sin enemigos - Tutorial",
        "Nivel 2: 👽 Alien (A* inteligente)",
        "Nivel 3: 👽 Alien + 👻 Fantasma (evade)",
        "Nivel 4: 👽👻🧟🦹 (4 enemigos con IA única)",
        "Nivel 5: 👽👻🧟🦹👺🤡 (TODOS - 6 enemigos)"
    ]
    
    start_y = title_y + 200
    for i, line in enumerate(info_lines):
        color = (255, 255, 0) if i == 0 else (200, 200, 200)
        font_size = font if i == 0 else small_font
        text = font_size.render(line, True, color)
        screen.blit(text, (50, start_y + i * 25))
    
    pygame.display.flip()

def draw_difficulty_menu():
    # Asegurar tamaño correcto de pantalla
    menu_width = 800
    menu_height = 600
    if SCREEN_WIDTH != menu_width or SCREEN_HEIGHT != menu_height:
        global screen
        screen = pygame.display.set_mode((menu_width, menu_height))
    
    screen.fill(COLOR_BACKGROUND)
    title = font.render("Elige dificultad:", True, COLOR_TEXT)
    screen.blit(title, (menu_width // 2 - title.get_width() // 2, 100))
    
    for i, opt in enumerate(difficulty_options):
        color = (255, 255, 255) if i == diff_idx else (150, 150, 150)
        txt = font.render(opt, True, color)
        screen.blit(txt, (menu_width // 2 - txt.get_width() // 2, 200 + i * 50))
    
    # Información de dificultad
    fps_info = [
        f"Fácil: {FPS_levels['Fácil']} FPS - Enemigos lentos",
        f"Medio: {FPS_levels['Medio']} FPS - Velocidad normal", 
        f"Difícil: {FPS_levels['Difícil']} FPS - Enemigos rápidos"
    ]
    
    for i, info in enumerate(fps_info):
        color = (255, 255, 0) if i == diff_idx else (150, 150, 150)
        text = small_font.render(info, True, color)
        screen.blit(text, (menu_width // 2 - text.get_width() // 2, 350 + i * 30))
    
    pygame.display.flip()

def reset_enemies():
    """Resetea enemigos según el nivel actual"""
    global enemies, enemy_behaviors
    
    # Obtener configuración de enemigos para el nivel actual
    level_config = LEVEL_ENEMIES.get(current_level, [])
    
    # Crear lista de enemigos con posiciones seguras
    enemies = []
    for enemy_config in level_config:
        enemy = {
            'pos': enemy_config['pos'].copy(),
            'dir': [0, -1],  # Dirección inicial
            'type': enemy_config['type']
        }
        
        # Verificar que la posición sea válida
        x, y = enemy['pos']
        if pathfinder.is_valid_position(x, y):
            enemies.append(enemy)
        else:
            # Si no es válida, usar una posición por defecto
            safe_positions = [[2, 2], [17, 2], [2, 10], [17, 10]]
            for safe_pos in safe_positions:
                if pathfinder.is_valid_position(safe_pos[0], safe_pos[1]):
                    enemy['pos'] = safe_pos
                    enemies.append(enemy)
                    break
    
    # Inicializar comportamientos de IA
    initialize_enemy_behaviors()
    
    print(f"🎮 Nivel {current_level + 1}: {len(enemies)} enemigos cargados")
    for enemy in enemies:
        print(f"   {enemy['type']} en posición {enemy['pos']}")

def reset_game():
    global player_pos, player_lives, current_level, maze, enemies, projectiles, pathfinder
    global player_score, screen
    
    player_pos = [1, 1]
    player_lives = 3
    current_level = 0
    player_score = 0
    
    maze = levels[current_level]['maze']
    projectiles = []
    
    update_maze_dimensions()
    pathfinder = AStar(maze)
    reset_enemies()

def draw_maze():
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            
            if maze[y][x] == 1:  # Pared
                pygame.draw.rect(screen, COLOR_WALL, rect)
            elif maze[y][x] == 2:  # Salida
                pygame.draw.rect(screen, COLOR_PATH, rect)
                door_emoji = emoji_font.render('🚪', True, (0, 0, 0))
                screen.blit(door_emoji, (x * TILE_SIZE + 4, y * TILE_SIZE))
            elif maze[y][x] == 3:  # Bonus
                pygame.draw.rect(screen, COLOR_PATH, rect)
                bonus_emoji = emoji_font.render('⭐', True, (0, 0, 0))
                screen.blit(bonus_emoji, (x * TILE_SIZE + 4, y * TILE_SIZE))
            else:  # Camino libre
                pygame.draw.rect(screen, COLOR_PATH, rect)

def draw_player():
    """Dibuja al protagonista perro (sprite si disponible, sino emoji)"""
    x, y = player_pos
    
    # Usar sprite si está cargado, sino emoji de respaldo
    if use_sprites and dog_sprites:
        # Dibujar sprite del perro según la dirección
        screen.blit(dog_sprites[current_direction][0], (x * TILE_SIZE, y * TILE_SIZE))
    else:
        # Usar emoji de perro como respaldo
        player_emoji = emoji_font.render('🐶', True, (0, 0, 0))
        screen.blit(player_emoji, (x * TILE_SIZE + 4, y * TILE_SIZE))

def draw_enemies():
    """Dibuja enemigos (sprite si disponible, sino emoji)"""
    for enemy in enemies:
        x, y = enemy["pos"]
        enemy_type = enemy["type"]
        
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
    global enemies, projectiles, player_score
    newp = []
    for p in projectiles:
        p['pos'][0] += p['dir'][0]
        p['pos'][1] += p['dir'][1]
        
        x, y = p['pos']
        
        if not (0 <= x < MAZE_WIDTH and 0 <= y < MAZE_HEIGHT):
            continue
            
        if maze[y][x] == 1:
            continue
                
        hit = False
        for i, e in enumerate(enemies[:]):
            if e['pos'] == [x, y]:
                enemies.remove(e)
                if i < len(enemy_behaviors):
                    enemy_behaviors.pop(i)
                player_score += 150  # Bonus por eliminar enemigo
                hit = True
                break
                    
        if not hit:
            newp.append(p)
    
    projectiles = newp

def draw_projectiles():
    """NUEVO: Dibuja proyectiles (sprite si disponible, sino emoji)"""
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
    
    return any(e['pos'] == player_pos for e in enemies)

def draw_ui():
    """Dibuja la interfaz de usuario mejorada"""
    ui_y = MAZE_HEIGHT * TILE_SIZE + 10
    
    # Información del nivel
    level_info = f"Nivel: {current_level + 1} - {levels[current_level]['name']}"
    level_text = small_font.render(level_info, True, COLOR_TEXT)
    screen.blit(level_text, (10, ui_y))
    
    # Puntuación
    score_text = small_font.render(f"Puntuación: {player_score}", True, COLOR_TEXT)
    screen.blit(score_text, (10, ui_y + 25))
    
    # Vidas
    hearts = '❤️' * player_lives
    lives_text = small_font.render(f"Vidas: {hearts}", True, COLOR_TEXT)
    screen.blit(lives_text, (200, ui_y))
    
    # Información de enemigos en el nivel actual
    enemy_count = len(enemies)
    enemy_types_current = [e['type'] for e in enemies]
    enemy_info = f"Enemigos: {enemy_count} {''.join(enemy_types_current) if enemy_types_current else 'Ninguno'}"
    
    enemy_text = small_font.render(enemy_info, True, COLOR_TEXT)
    screen.blit(enemy_text, (200, ui_y + 25))
    
    # Información de sprites y controles
    sprite_info = [
        f"Perro: {'✅' if use_sprites else '❌'} | Enemigos: {len(enemy_sprites)}✅ | Caca: {'✅' if poop_sprite else '❌'}",
        f"Dificultad: {levels[current_level]['difficulty']} | FPS: {FPS}",
        f"(R=recargar sprites | ESPACIO=disparar | ESC=menú)"
    ]
    
    for i, line in enumerate(sprite_info):
        info_text = small_font.render(line, True, COLOR_TEXT)
        screen.blit(info_text, (400, ui_y + i * 20))

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
    
    current_level += 1
    if current_level < len(levels):
        maze = levels[current_level]['maze']
        update_maze_dimensions()
        pathfinder = AStar(maze)
        
        player_pos = [1, 1]
        projectiles = []
        
        reset_enemies()
        show_message(f"¡Nivel {current_level + 1}: {levels[current_level]['name']}!")
    else:
        show_message(f"¡Felicidades! ¡Puntuación final: {player_score}!")
        reset_game()
        reset_menu()  # ASEGURAR menú limpio
        game_state = STATE_MENU

# Inicialización
clock = pygame.time.Clock()
initialize_enemy_behaviors()

# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
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
    
    # Renderizado según el estado del juego (SOLO 3 ESTADOS)
    if game_state == STATE_MENU:
        draw_menu()
    elif game_state == STATE_DIFF:
        draw_difficulty_menu()
    elif game_state == STATE_PLAY:
        # Controles del jugador
        keys = pygame.key.get_pressed()
        new_pos = player_pos.copy()
        
        if keys[pygame.K_UP]:
            new_pos[1] -= 1
            last_direction = [0, -1]
            current_direction = 'up'
        elif keys[pygame.K_DOWN]:
            new_pos[1] += 1
            last_direction = [0, 1]
            current_direction = 'down'
        elif keys[pygame.K_LEFT]:
            new_pos[0] -= 1
            last_direction = [-1, 0]
            current_direction = 'left'
        elif keys[pygame.K_RIGHT]:
            new_pos[0] += 1
            last_direction = [1, 0]
            current_direction = 'right'
        
        # Verificar movimiento válido
        if (0 <= new_pos[0] < MAZE_WIDTH and 0 <= new_pos[1] < MAZE_HEIGHT and 
            maze[new_pos[1]][new_pos[0]] != 1):
            
            # Manejar bonificaciones
            handle_bonus_tile(new_pos[0], new_pos[1])
            player_pos = new_pos
        
        # Lanzar proyectil
        if keys[pygame.K_SPACE] and len(projectiles) < 3:
            projectiles.append({'pos': player_pos.copy(), 'dir': last_direction.copy()})
        
        # Recargar sprites si se presiona R
        if keys[pygame.K_r]:
            print("🔄 Recargando sprites...")
            reload_sprites_if_needed()
            show_message("¡Sprites recargados!")
        
        # Verificar llegada a la salida
        if maze[player_pos[1]][player_pos[0]] == 2:
            next_level()
        
        # Actualizar enemigos y proyectiles
        move_enemies()
        move_projectiles()
        
        # Verificar colisiones
        if check_enemy_collision():
            player_lives -= 1
            player_pos = [1, 1]
            reset_enemies()
            projectiles = []
            
            if player_lives <= 0:
                show_message(f"¡Game Over! Puntuación: {player_score}")
                reset_game()
                reset_menu()  # ASEGURAR menú limpio
                game_state = STATE_MENU
            else:
                show_message(f"¡Te han atrapado! Vidas: {player_lives}")
        
        # Dibujar todo
        screen.fill(COLOR_BACKGROUND)
        draw_maze()
        draw_player()
        draw_enemies()
        draw_projectiles()
        draw_ui()

        if keys[pygame.K_ESCAPE]:
            reset_menu()  # ASEGURAR menú limpio
            game_state = STATE_MENU
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()