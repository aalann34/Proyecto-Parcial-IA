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

# ========================================
# NIVELES SIMPLIFICADOS - 5 NIVELES FUNCIONALES
# ========================================
# Solo elementos básicos: 0=camino, 1=pared, 2=salida, 3=bonus

levels = [
    # NIVEL 1 - ENTRADA AL INFIERNO
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

    # NIVEL 2 - CÁMARAS DE TORMENTO
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
            [1,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    },

    # NIVEL 3 - LABERINTO DE FUEGO (CORREGIDO - diamantes accesibles)
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
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    },

    # NIVEL 4 - FORTALEZA DEMONÍACA (CORREGIDO - diamantes accesibles)
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
            [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
    },

    # NIVEL 5 - TRONO DE LUCIFER
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
            [1,0,0,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,1,0,0,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
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
FPS_levels = {'Fácil': 4, 'Medio': 6, 'Difícil': 8}  # Reducido para mejor jugabilidad

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
player_web_slowdown = 0  # NUEVO: Contador de ralentización por telarañas

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

# ========================================
# SISTEMA GLOBAL DE TELARAÑAS SIMPLIFICADO Y FUNCIONAL
# ========================================
ghost_webs = []  # Lista global de todas las telarañas activas

def update_ghost_webs():
    """VERSIÓN SIMPLIFICADA: Actualiza las telarañas globales de todos los fantasmas"""
    global ghost_webs
    current_time = time.time()
    
    # PASO 1: Limpiar telarañas viejas
    old_count = len(ghost_webs)
    ghost_webs = [web for web in ghost_webs 
                 if current_time - web['time'] < web['duration']]
    
    if len(ghost_webs) != old_count:
        print(f"🕸️ Limpiando telarañas viejas: {old_count} -> {len(ghost_webs)}")
    
    # PASO 2: Recopilar telarañas de todos los fantasmas
    if not enemy_behaviors:
        return
    
    for i, behavior in enumerate(enemy_behaviors):
        try:
            # VERIFICAR SI ES UN FANTASMA
            if hasattr(behavior, 'get_active_webs') and behavior.enemy.get('type') == '👻':
                webs_from_ghost = behavior.get_active_webs()
                
                for web in webs_from_ghost:
                    # EVITAR DUPLICADOS (comparar posición y tiempo)
                    web_exists = False
                    for existing_web in ghost_webs:
                        if (existing_web['pos'] == web['pos'] and 
                            abs(existing_web['time'] - web['time']) < 0.5):
                            web_exists = True
                            break
                    
                    if not web_exists:
                        ghost_webs.append(web)
                        print(f"🕸️ NUEVA TELARAÑA AGREGADA: {web['pos']} - Total global: {len(ghost_webs)}")
                        
        except Exception as e:
            print(f"❌ Error procesando fantasma {i}: {e}")
            continue

def draw_ghost_webs():
    """VERSIÓN SIMPLIFICADA: Dibuja todas las telarañas activas"""
    if not ghost_webs:
        return
        
    current_time = time.time()
    
    for web in ghost_webs:
        try:
            x, y = web['pos']
            age = current_time - web['time']
            
            # Efecto de desvanecimiento
            alpha = max(0, 1 - (age / web['duration']))
            
            if alpha > 0:
                # FONDO GRIS OSCURO
                web_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                gray_color = int(60 * alpha)
                pygame.draw.rect(screen, (gray_color, gray_color, gray_color), web_rect)
                
                # EMOJI DE TELARAÑA
                web_emoji = emoji_font.render('🕸️', True, (200, 200, 200))
                screen.blit(web_emoji, (x * TILE_SIZE + 4, y * TILE_SIZE))
                
        except Exception as e:
            print(f"❌ Error dibujando telaraña: {e}")
            continue

def check_web_collision():
    """VERSIÓN SIMPLIFICADA: Verifica si el jugador está en una telaraña"""
    if not ghost_webs:
        return False
        
    player_x, player_y = player_pos
    
    for web in ghost_webs:
        try:
            web_x, web_y = web['pos']
            if player_x == web_x and player_y == web_y:
                return True
        except:
            continue
            
    return False

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
            print(f"🕸️ FANTASMA CREADO: {enemy['pos']} - Puede crear telarañas")

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
        "👹 CRIATURAS INFERNALES CON IA:",
        "Portal de Entrada: 3 criaturas aleatorias",
        "Cámaras de Tormento: 3 seres del averno", 
        "Laberinto de Fuego: 3 bestias infernales",
        "Fortaleza Demoníaca: 3 guardianes élite",
        "Trono de Lucifer: 3 señores supremos del mal",
        "Enemigos: 👽👻🧟🦹👺🤡👹 (7 tipos disponibles)",
        "👻 Fantasmas dejan telarañas temporales 🕸️",
        "🧱 Paredes infernales con bloquerojo.png"
    ]
    
    start_y = title_y + 200
    for i, line in enumerate(info_lines):
        color = COLOR_FIRE if i == 0 else COLOR_BONUS
        font_size = font if i == 0 else small_font
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
    global enemies, enemy_behaviors, pathfinder, ghost_webs
    
    # LIMPIAR TELARAÑAS AL RESETEAR ENEMIGOS
    ghost_webs = []
    print("🕸️ Telarañas limpiadas al resetear enemigos")
    
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
    global player_score, screen, ghost_webs, player_web_slowdown
    
    player_pos = [1, 1]
    player_lives = 3
    current_level = 0
    player_score = 0
    player_web_slowdown = 0  # NUEVO: Resetear ralentización
    ghost_webs = []  # NUEVO: Limpiar telarañas
    
    # Cargar laberinto del nivel inicial
    maze = levels[current_level]['maze']
    projectiles = []
    
    # Actualizar dimensiones de pantalla
    update_maze_dimensions()
    
    # Inicializar pathfinder ANTES de generar enemigos
    pathfinder = AStar(maze)
    
    # Generar enemigos DESPUÉS de inicializar pathfinder
    reset_enemies()
    
    print(f"🔄 Juego reiniciado - Nivel {current_level + 1}")

def draw_maze():
    """MODIFICADO: Dibuja el laberinto con sprites de pared infernal si están disponibles"""
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
            elif maze[y][x] == 2:  # Portal de salida
                pygame.draw.rect(screen, COLOR_PATH, rect)
                # Efecto de portal con gradiente
                pygame.draw.rect(screen, COLOR_EXIT, rect)
                door_emoji = emoji_font.render('🚪', True, (255, 215, 0))  # Puerta dorada
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
    
    return any(e['pos'] == player_pos for e in enemies)

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
    
    # Vidas como corazones ardientes
    hearts = '💖' * player_lives
    lives_text = small_font.render(f"Vida: {hearts}", True, COLOR_FIRE)
    screen.blit(lives_text, (200, ui_y))
    
    # Información de criaturas infernales
    enemy_count = len(enemies)
    enemy_types_current = [e['type'] for e in enemies]
    enemy_info = f"Demonios: {enemy_count} {''.join(enemy_types_current) if enemy_types_current else ''}"
    
    enemy_text = small_font.render(enemy_info, True, COLOR_FIRE)
    screen.blit(enemy_text, (200, ui_y + 25))
    
    # NUEVO: Estado de telarañas con debug
    web_count = len(ghost_webs)
    in_web = check_web_collision()
    
    if in_web:
        web_status = f"🕸️ ATRAPADO EN TELARAÑA - MOVIMIENTO LENTO (Total: {web_count})"
        web_color = (255, 100, 100)  # Rojo de advertencia
        web_text = small_font.render(web_status, True, web_color)
        screen.blit(web_text, (200, ui_y + 50))
        ui_y_offset = 25
    elif web_count > 0:
        web_status = f"🕸️ Telarañas activas: {web_count}"
        web_color = (200, 200, 200)  # Gris informativo
        web_text = small_font.render(web_status, True, web_color)
        screen.blit(web_text, (200, ui_y + 50))
        ui_y_offset = 25
    else:
        ui_y_offset = 0
    
    # Información de aim bot infernal
    aim_status = "🎯 PROYECTIL GUIADO: ON" if aim_bot.aim_assistance else "🎯 PROYECTIL GUIADO: OFF"
    aim_color = COLOR_FIRE if aim_bot.aim_assistance else (100, 100, 100)
    aim_text = small_font.render(aim_status, True, aim_color)
    screen.blit(aim_text, (200, ui_y + 50 + ui_y_offset))
    
    # Información de controles infernales
    sprite_info = [
        f"Tortura: {levels[current_level]['difficulty']} | Velocidad: {FPS} FPS",
        f"(R=recargar | ESPACIO=lanzar proyectil | A=guiado | ESC=salir)"
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
    global ghost_webs, player_web_slowdown
    
    current_level += 1
    if current_level < len(levels):
        # Limpiar telarañas del nivel anterior
        ghost_webs = []
        player_web_slowdown = 0
        print("🕸️ Telarañas limpiadas al cambiar de nivel")
        
        # Actualizar laberinto
        maze = levels[current_level]['maze']
        update_maze_dimensions()
        
        # IMPORTANTE: Reinicializar pathfinder ANTES de generar enemigos
        pathfinder = AStar(maze)
        
        # Resetear posición del jugador y proyectiles
        player_pos = [1, 1]
        projectiles = []
        
        # Generar enemigos DESPUÉS de inicializar pathfinder
        reset_enemies()
        
        show_message(f"🔥 {levels[current_level]['name']} 🔥")
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
        
        # VERIFICAR SI ESTÁ EN TELARAÑA (movimiento más lento)
        in_web = check_web_collision()
        
        # Sistema de ralentización por telarañas
        move_allowed = True
        if in_web:
            player_web_slowdown += 1
            # Solo se puede mover cada 3 frames cuando está en telaraña
            if player_web_slowdown % 3 != 0:
                move_allowed = False
        else:
            player_web_slowdown = 0
        
        if move_allowed:
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
        if (move_allowed and 
            0 <= new_pos[0] < MAZE_WIDTH and 0 <= new_pos[1] < MAZE_HEIGHT and 
            maze[new_pos[1]][new_pos[0]] != 1):
            
            # Manejar bonificaciones
            handle_bonus_tile(new_pos[0], new_pos[1])
            player_pos = new_pos
        
        # Sistema de disparo con aim bot
        if keys[pygame.K_SPACE] and len(projectiles) < 5:  # Aumentado límite de proyectiles
            # Obtener dirección de aim bot
            aim_direction = aim_bot.get_aim_direction(player_pos, enemies)
            
            if aim_direction:
                # Usar aim bot
                projectiles.append({'pos': player_pos.copy(), 'dir': aim_direction})
            else:
                # Disparo normal
                projectiles.append({'pos': player_pos.copy(), 'dir': last_direction.copy()})
        
        # Toggle aim bot
        if keys[pygame.K_a]:
            aim_bot.aim_assistance = not aim_bot.aim_assistance
            time.sleep(0.3)  # Evitar toggle múltiple
        
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
        
        # ACTUALIZAR TELARAÑAS DE FANTASMAS (SIMPLIFICADO)
        update_ghost_webs()
        
        # Verificar colisiones
        if check_enemy_collision():
            player_lives -= 1
            player_pos = [1, 1]
            reset_enemies()
            projectiles = []
            ghost_webs = []  # LIMPIAR telarañas al morir
            player_web_slowdown = 0  # Resetear ralentización
            
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
        draw_maze()
        draw_ghost_webs()  # DIBUJAR TELARAÑAS SIMPLIFICADO
        draw_player()
        draw_enemies()
        draw_projectiles()
        draw_aim_bot_indicators()
        draw_ui()

        if keys[pygame.K_ESCAPE]:
            reset_menu()  # ASEGURAR menú limpio
            game_state = STATE_MENU
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()