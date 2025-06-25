import pygame
import sys
import random
import time
from scripts import AStar

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
TILE_SIZE = 40  # Tamaño de cada celda
MAZE_WIDTH = 18  # Número de columnas
MAZE_HEIGHT = 13  # Número de filas
SCREEN_WIDTH = TILE_SIZE * MAZE_WIDTH
SCREEN_HEIGHT = TILE_SIZE * MAZE_HEIGHT

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🐶 Perro Pacman")

# Fuente para textos y emojis
pygame.font.init()
font = pygame.font.SysFont('Arial', 30)
emoji_font = pygame.font.SysFont('Segoe UI Emoji', TILE_SIZE)  # Fuente para emojis

# Colores
COLOR_WALL = (40, 40, 40)
COLOR_PATH = (200, 200, 200)
COLOR_BACKGROUND = (0, 0, 0)
COLOR_PLAYER = (255, 255, 0)
COLOR_EXIT = (0, 255, 0)
COLOR_ENEMY = (255, 0, 0)
COLOR_TEXT = (255, 255, 255)

# Game states
STATE_MENU = 'MENU'
STATE_DIFF = 'DIFFICULTY'  # Nuevo estado para selección de dificultad
STATE_SKIN = 'SKIN'
STATE_PLAY = 'PLAY'

# Menú principal, opciones de dificultad y skins
menu_options = ['Nueva Partida', 'Seleccionar Dificultad', 'Cambiar Skin', 'Salir']  # Añadida opción de dificultad
difficulty_options = ['Fácil', 'Medio', 'Difícil']  # Opciones de dificultad
FPS_levels = {'Fácil': 5, 'Medio': 8, 'Difícil': 12}  # Velocidad del juego según dificultad
skins = ['🐶', '🐱', '🦁']
menu_idx = 0
skin_idx = 0
diff_idx = 1  # Por defecto 'Medio'
current_skin = skins[0]
game_state = STATE_MENU
FPS = FPS_levels[difficulty_options[diff_idx]]  # FPS según dificultad seleccionada

# Cargar y preparar el spritesheet del perro
try:
    # Cargar la imagen del spritesheet
    dog_spritesheet = pygame.image.load('sprites_perro.png')
    # Analizar dimensiones y cortar los frames
    # La imagen tiene 12 sprites (4 columnas x 3 filas)
    sprite_width = dog_spritesheet.get_width() // 4
    sprite_height = dog_spritesheet.get_height() // 3
    
    # Crear un diccionario para almacenar los sprites en cada dirección
    dog_sprites = {
        'up': [],    # Frames mirando hacia arriba
        'right': [], # Frames mirando hacia la derecha
        'down': [],  # Frames mirando hacia abajo
        'left': []   # Frames mirando hacia la izquierda
    }
    
    # Cortar el spritesheet y guardar los frames
    # Para este juego, usamos solo la primera fila (frames 0-3)
    directions = ['down', 'left', 'right', 'up']  # Orden basado en la imagen del spritesheet
    
    for i, direction in enumerate(directions):
        # Recortar el sprite del spritesheet
        frame = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
        frame.blit(dog_spritesheet, (0, 0), (i * sprite_width, 0, sprite_width, sprite_height))
        # Escalar al tamaño de la celda
        scaled_frame = pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE))
        dog_sprites[direction].append(scaled_frame)
    
    # También guardar frames de la segunda fila para animación (opcional)
    for i, direction in enumerate(directions):
        frame = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
        frame.blit(dog_spritesheet, (0, 0), (i * sprite_width, sprite_height, sprite_width, sprite_height))
        scaled_frame = pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE))
        dog_sprites[direction].append(scaled_frame)
    
    # Variable para controlar si usamos spritesheet o emojis
    use_sprites = True
    
except (pygame.error, FileNotFoundError):
    print("No se pudo cargar el spritesheet del perro. Se usarán emojis.")
    use_sprites = False

# Variable para la dirección actual del jugador
current_direction = 'right'  # Dirección inicial

# Niveles del juego
levels = [
    # Nivel 1
    [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1],
        [1,0,1,0,0,0,0,1,0,1,0,1,0,0,0,0,0,1],
        [1,0,1,0,1,1,0,1,0,1,0,1,0,1,1,1,0,1],
        [1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],
        [1,0,1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,1],
        [1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ],
    # Nivel 2
    [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1],
        [1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,1,0,1],
        [1,0,1,0,0,0,0,0,0,0,1,0,0,0,0,1,0,1],
        [1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,1,0,1],
        [1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1],
        [1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,0,1,1,1,1,1,1,1,0,1,1,0,1],
        [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,1],
        [1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,0,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ],
    # Nivel 3
    [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,0,1,1,1,1,0,1,1,1,1,0,1],
        [1,0,1,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1],
        [1,0,1,0,1,1,1,1,0,1,0,1,1,1,0,1,0,1],
        [1,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,1],
        [1,1,1,0,1,0,1,1,1,1,1,1,0,1,0,1,1,1],
        [1,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,1],
        [1,0,1,0,1,1,1,1,0,1,1,1,1,1,0,1,0,1],
        [1,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
        [1,0,1,1,1,1,0,1,1,1,1,0,1,1,1,1,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ]
]

# Posición inicial del jugador
player_pos = [1, 1]
player_lives = 3
current_level = 0
maze = levels[current_level]
projectiles = []  # Lista para las popós lanzadas
last_direction = [1, 0]  # Dirección por defecto (derecha)

# Inicializar pathfinder A*
pathfinder = AStar(maze)

# Enemigos (posición y dirección)
# Usaremos diferentes tipos de emoji para los enemigos
enemy_types = ['👻', '👽', '🧟', '🦹', '👺', '🤡']
enemies = [
    {"pos": [1, 10], "dir": [0, -1], "type": enemy_types[0]},
    {"pos": [16, 1], "dir": [-1, 0], "type": enemy_types[1]}
]

# Función para dibujar el menú principal
def draw_menu():
    screen.fill(COLOR_BACKGROUND)
    for i, option in enumerate(menu_options):
        color = (255, 255, 255) if i == menu_idx else (150, 150, 150)
        text = font.render(option, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 150 + i * 50))
    pygame.display.flip()

# Función para dibujar el menú de dificultad
def draw_difficulty_menu():
    screen.fill(COLOR_BACKGROUND)
    title = font.render("Elige dificultad:", True, COLOR_TEXT)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
    
    for i, opt in enumerate(difficulty_options):
        color = (255, 255, 255) if i == diff_idx else (150, 150, 150)
        txt = font.render(opt, True, color)
        screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 200 + i * 50))
    
    pygame.display.flip()

# Función para dibujar el menú de selección de skin
def draw_skin_menu():
    screen.fill(COLOR_BACKGROUND)
    title = font.render("Elige skin:", True, COLOR_TEXT)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
    
    # Modificamos el menú de skins para incluir opción de sprite
    options = skins + ["Sprite"] if use_sprites else skins
    
    # Dibujamos cada skin con un rectángulo indicador
    for i, sk in enumerate(options):
        x = SCREEN_WIDTH // 2 - TILE_SIZE * 2 + i * (TILE_SIZE * 1.5)
        y = 200
        rect = pygame.Rect(x - 5, y - 5, TILE_SIZE + 10, TILE_SIZE + 10)
        pygame.draw.rect(screen,
                      (255, 255, 255) if i == skin_idx else (100, 100, 100),
                      rect, 2)
        
        if i < len(skins):
            screen.blit(emoji_font.render(sk, True, COLOR_TEXT), (x, y))
        else:
            # Para la opción de sprite, mostramos una miniatura del perro
            if use_sprites:
                screen.blit(dog_sprites['right'][0], (x, y))
    
    pygame.display.flip()

# Función para reposicionar enemigos a sus posiciones iniciales
def reset_enemies():
    global enemies, current_level
    enemies = [
        {"pos": [1, 10], "dir": [0, -1], "type": enemy_types[0]},
        {"pos": [16, 1], "dir": [-1, 0], "type": enemy_types[1]}
    ]
    # Si hay enemigos adicionales por nivel, también los reposicionamos
    if current_level > 0:
        idx = min(current_level + 2, len(enemy_types) - 1)
        enemies.append({"pos": [MAZE_WIDTH // 2, MAZE_HEIGHT // 2], "dir": [1, 0], "type": enemy_types[idx]})

# Función para reiniciar el juego
def reset_game():
    global player_pos, player_lives, current_level, maze, enemies, projectiles, pathfinder
    player_pos = [1, 1]
    player_lives = 3
    current_level = 0
    maze = levels[current_level]
    projectiles = []
    
    # Actualizar el pathfinder con el nuevo laberinto
    pathfinder = AStar(maze)
    
    # Restablecer enemigos
    reset_enemies()

# Función para dibujar el laberinto
def draw_maze():
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if maze[y][x] == 1:
                pygame.draw.rect(screen, COLOR_WALL, rect)
            elif maze[y][x] == 2:
                pygame.draw.rect(screen, COLOR_PATH, rect)
                # Dibujar la puerta de salida como emoji
                door_emoji = emoji_font.render('🚪', True, (0, 0, 0))
                screen.blit(door_emoji, (x * TILE_SIZE + 4, y * TILE_SIZE))
            else:
                pygame.draw.rect(screen, COLOR_PATH, rect)

# Función para dibujar al jugador con la skin actual
def draw_player():
    x, y = player_pos
    
    # Usar sprites o emojis según la selección
    if skin_idx >= len(skins) and use_sprites:
        # Usar el sprite del perro según la dirección
        screen.blit(dog_sprites[current_direction][0], (x * TILE_SIZE, y * TILE_SIZE))
    else:
        # Usar el emoji seleccionado
        player_emoji = emoji_font.render(current_skin, True, (0, 0, 0))
        screen.blit(player_emoji, (x * TILE_SIZE + 4, y * TILE_SIZE))

# Función para dibujar enemigos
def draw_enemies():
    for enemy in enemies:
        x, y = enemy["pos"]
        enemy_emoji = emoji_font.render(enemy["type"], True, (0, 0, 0))
        screen.blit(enemy_emoji, (x * TILE_SIZE + 4, y * TILE_SIZE))

# Función para mover a los enemigos usando A*
def move_enemies():
    """
    Mueve a los enemigos usando el algoritmo A* para perseguir al jugador
    """
    global pathfinder
    
    for enemy in enemies:
        x, y = enemy["pos"]
        player_x, player_y = player_pos
        
        # Calcular distancia al jugador
        distance_to_player = abs(player_x - x) + abs(player_y - y)
        
        # Diferentes comportamientos según el tipo de enemigo
        if enemy["type"] == '👻':  # Fantasma - siempre persigue con A*
            dx, dy = pathfinder.get_next_move(x, y, player_x, player_y)
            
        elif enemy["type"] == '👽':  # Alien - persigue solo si está cerca
            if distance_to_player <= 5:
                dx, dy = pathfinder.get_next_move(x, y, player_x, player_y)
            else:
                # Movimiento aleatorio cuando está lejos
                dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0), (0, 0)])
                
        elif enemy["type"] == '🧟':  # Zombie - lento pero persistente
            if distance_to_player <= 8:  # Mayor rango de detección
                # Usa A* pero se mueve más lento (50% de probabilidad de moverse)
                if random.random() < 0.5:
                    dx, dy = pathfinder.get_next_move(x, y, player_x, player_y)
                else:
                    dx, dy = (0, 0)  # Se queda quieto
            else:
                dx, dy = (0, 0)
                
        else:  # Otros enemigos - comportamiento mixto
            if distance_to_player <= 3:
                dx, dy = pathfinder.get_next_move(x, y, player_x, player_y)
            else:
                # Patrullaje aleatorio
                possible_moves = []
                for test_dx, test_dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x = x + test_dx
                    new_y = y + test_dy
                    if pathfinder.is_valid_position(new_x, new_y):
                        possible_moves.append((test_dx, test_dy))
                
                if possible_moves:
                    dx, dy = random.choice(possible_moves)
                else:
                    dx, dy = (0, 0)
        
        # Aplicar el movimiento calculado
        new_x = x + dx
        new_y = y + dy
        
        # Verificar que el movimiento sea válido antes de aplicarlo
        if pathfinder.is_valid_position(new_x, new_y):
            enemy["pos"] = [new_x, new_y]

# Función para mover los proyectiles
def move_projectiles():
    global enemies, projectiles
    newp = []
    for p in projectiles:
        # Mover el proyectil
        p['pos'][0] += p['dir'][0]
        p['pos'][1] += p['dir'][1]
        
        x, y = p['pos']
        
        # Verificar si está dentro del laberinto
        if not (0 <= x < MAZE_WIDTH and 0 <= y < MAZE_HEIGHT):
            continue
            
        # Verificar colisión con paredes
        if maze[y][x] == 1:
            continue  # El proyectil desaparece al chocar con una pared
                
        # Verificar colisión con enemigos
        hit = False
        for e in enemies[:]:  # Hacer una copia para poder eliminar durante la iteración
            if e['pos'] == [x, y]:
                enemies.remove(e)
                hit = True
                break
                    
        if not hit:
            newp.append(p)
    
    projectiles = newp

# Función para dibujar los proyectiles
def draw_projectiles():
    for p in projectiles:
        x, y = p['pos']
        poop = emoji_font.render('💩', True, (0, 0, 0))
        screen.blit(poop, (x * TILE_SIZE + 4, y * TILE_SIZE))

# Función para detectar colisiones con enemigos
def check_enemy_collision():
    return any(e['pos'] == player_pos for e in enemies)

# Función para dibujar vidas
def draw_lives():
    hearts = '❤️' * player_lives
    lives_text = font.render(f"Vidas: {hearts}", True, COLOR_TEXT)
    screen.blit(lives_text, (10, 10))

# Función para mostrar mensajes en pantalla
def show_message(message):
    text = font.render(message, True, COLOR_TEXT)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    time.sleep(1.5)

# Función para configurar el siguiente nivel
def next_level():
    global current_level, maze, player_pos, enemies, projectiles, game_state, pathfinder
    current_level += 1
    if current_level < len(levels):
        maze = levels[current_level]
        
        # Actualizar el pathfinder con el nuevo laberinto
        pathfinder = AStar(maze)
        
        player_pos = [1, 1]
        projectiles = []  # Limpiar proyectiles al cambiar de nivel
        reset_enemies()  # Usar la función para reposicionar enemigos
        show_message(f"¡Nivel {current_level + 1}!")
    else:
        show_message("¡Felicidades! ¡Has completado el juego!")
        reset_game()
        game_state = STATE_MENU

# Clock para controlar la velocidad del juego
clock = pygame.time.Clock()

# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            # Manejo de teclas según el estado del juego
            if game_state == STATE_MENU:
                if event.key == pygame.K_UP:
                    menu_idx = (menu_idx - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    menu_idx = (menu_idx + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    choice = menu_options[menu_idx]
                    if choice == 'Nueva Partida':
                        reset_game()
                        game_state = STATE_PLAY
                    elif choice == 'Seleccionar Dificultad':
                        game_state = STATE_DIFF
                    elif choice == 'Cambiar Skin':
                        game_state = STATE_SKIN
                    else:  # Salir
                        running = False
            
            elif game_state == STATE_DIFF:
                if event.key == pygame.K_UP:
                    diff_idx = (diff_idx - 1) % len(difficulty_options)
                elif event.key == pygame.K_DOWN:
                    diff_idx = (diff_idx + 1) % len(difficulty_options)
                elif event.key == pygame.K_RETURN:
                    FPS = FPS_levels[difficulty_options[diff_idx]]
                    game_state = STATE_MENU
                elif event.key == pygame.K_ESCAPE:
                    game_state = STATE_MENU
            
            elif game_state == STATE_SKIN:
                available_options = len(skins) + (1 if use_sprites else 0)
                if event.key == pygame.K_LEFT:
                    skin_idx = (skin_idx - 1) % available_options
                elif event.key == pygame.K_RIGHT:
                    skin_idx = (skin_idx + 1) % available_options
                elif event.key == pygame.K_RETURN:
                    # Si la selección está dentro del rango de skins disponibles
                    if skin_idx < len(skins):
                        current_skin = skins[skin_idx]
                    # Si no, estamos en la opción "Sprite"
                    game_state = STATE_MENU
                elif event.key == pygame.K_ESCAPE:
                    game_state = STATE_MENU
    
    # Actualizar y renderizar según el estado del juego
    if game_state == STATE_MENU:
        draw_menu()
    
    elif game_state == STATE_DIFF:
        draw_difficulty_menu()
    
    elif game_state == STATE_SKIN:
        draw_skin_menu()
    
    elif game_state == STATE_PLAY:
        # Manejo de teclas para mover al jugador
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
        
        # Verificar si el movimiento es válido (no hay pared)
        if 0 <= new_pos[0] < MAZE_WIDTH and 0 <= new_pos[1] < MAZE_HEIGHT and maze[new_pos[1]][new_pos[0]] != 1:
            player_pos = new_pos
        
        # Lanzar popó con la barra espaciadora
        if keys[pygame.K_SPACE] and len(projectiles) < 3:  # Limitar a 3 proyectiles a la vez
            # Crear un nuevo proyectil
            projectiles.append({'pos': player_pos.copy(), 'dir': last_direction.copy()})
        
        # Verificar si el jugador llegó a la salida
        if maze[player_pos[1]][player_pos[0]] == 2:
            next_level()
        
        # Mover enemigos y proyectiles
        move_enemies()
        move_projectiles()
        
        # Verificar colisión con enemigos
        if check_enemy_collision():
            player_lives -= 1
            player_pos = [1, 1]  # Volver a la posición inicial
            reset_enemies()  # ¡NUEVO! Reposicionar enemigos también
            projectiles = []  # ¡NUEVO! Limpiar proyectiles tambié
            
            if player_lives <= 0:
                show_message("¡Game Over!")
                reset_game()
                game_state = STATE_MENU
            else:
                show_message(f"¡Te han atrapado! Vidas restantes: {player_lives}")
        
        # Dibujar todo
        screen.fill(COLOR_BACKGROUND)
        draw_maze()
        draw_player()
        draw_enemies()
        draw_projectiles()
        draw_lives()

        # Tecla de escape para volver al menú
        if keys[pygame.K_ESCAPE]:
            game_state = STATE_MENU
    
    # Actualizar pantalla
    pygame.display.flip()
    
    # Controlar la velocidad del juego
    clock.tick(FPS)

# Cerrar Pygame
pygame.quit()
sys.exit()