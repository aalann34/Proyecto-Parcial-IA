# 🐶 Perro Héroe - Aventura con IA

**Examen Parcial - Inteligencia Artificial**  
**Estudiante:** Alan Alaberto Martinez Ubiera  
**Matrícula:** 23-EISN-2-62  
**Fecha:** Julio 2025  

## 📋 Descripción del Proyecto

Juego estilo Pac-Man donde un perro héroe debe navegar por laberintos, recoger bonificaciones y evitar enemigos inteligentes. Los enemigos utilizan **algoritmo A*** para perseguir al jugador y **Árboles de Comportamiento** para tomar decisiones estratégicas.

**Características principales:**
- 5 niveles progresivos con dificultad escalable
- IA avanzada implementada desde cero
- Sprites personalizados para personajes
- Sistema de puntuación y vidas
- Soporte para gamepad/joystick
- Efectos de sonido y música

## 🧠 Inteligencia Artificial Implementada

### Algoritmo A* (A-Star)
**Ubicación:** `scripts/astar.py`
- **Propósito:** Navegación óptima de enemigos hacia el jugador
- **Implementación:** Desde cero, sin librerías externas
- **Funcionalidades:**
  - Cálculo de rutas más cortas
  - Evasión de obstáculos
  - Optimización de movimiento

### Árboles de Comportamiento
**Ubicación:** `scripts/behavior_tree.py`, `scripts/enemy_behaviors.py`
- **Propósito:** Decisiones estratégicas de enemigos
- **Implementación:** Sistema completo desde cero
- **Características:**
  - Nodos de condición, acción y composite
  - Comportamientos cooperativos entre enemigos
  - Adaptación al estado del juego
  - Estados: perseguir, patrullar, huir

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Python 3.9 o superior
- Git (para clonar el repositorio)

### Pasos de Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/Proyecto-Parcial-IA.git
cd Proyecto-Parcial-IA
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Ejecutar el juego:**
```bash
python main.py
```

## 🎮 Controles

### Teclado
- **↑↓←→** - Mover al perro héroe
- **Espacio** - Disparar proyectiles
- **R** - Recargar sprites
- **ESC** - Volver al menú

### Gamepad/Joystick
- **Stick analógico/D-pad** - Mover al perro
- **Botón A/X** - Disparar proyectiles
- **Start/Menu** - Pausar/menú

## 📁 Estructura del Proyecto

```
Proyecto-Parcial-IA/
├── main.py                 # Archivo principal del juego
├── scripts/                # Lógica de IA y juego
│   ├── __init__.py        # Módulo de scripts
│   ├── astar.py           # Algoritmo A* implementado desde cero
│   ├── behavior_tree.py   # Sistema de árboles de comportamiento
│   ├── enemy_behaviors.py # Comportamientos específicos de enemigos
│   └── node.py            # Nodos para árboles de comportamiento
├── assets/                # Recursos del juego
│   ├── images/            # Sprites y gráficos
│   │   ├── perro.png      # Sprite del protagonista
│   │   └── fantasma.png   # Sprite del enemigo
│   ├── sounds/            # Efectos de sonido
│   └── music/             # Música de fondo
├── requirements.txt       # Dependencias Python
└── README.md             # Documentación (este archivo)
```

## 🎨 Sistema de Sprites

El juego soporta sprites personalizados:
- **perro.png** - Protagonista perro héroe
- **fantasma.png** - Enemigo fantasma
- **alien.png** - Enemigo alien (opcional)
- **zombie.png** - Enemigo zombie (opcional)

**Fallback:** Si no se encuentran sprites, usa emojis como respaldo.

## 🔊 Audio

- **Efectos de sonido:** Disparos, colisiones, bonificaciones
- **Música de fondo:** Ambiente inmersivo por nivel
- **Formatos soportados:** WAV, OGG, MP3

## 🧪 Tecnologías y Algoritmos

### Librerías Utilizadas
- **Python 3.13**
- **Pygame 2.6.1**

### Algoritmos Implementados Desde Cero
- **A* (A-Star):** Pathfinding y navegación
- **Árboles de Comportamiento:** IA de enemigos
- **Gestión de estados:** Sistema de juego
- **Detección de colisiones:** Física básica

## 📊 Rendimiento

- **FPS:** Configurable (5-12 según dificultad)
- **Optimizaciones:** 
  - Pathfinding eficiente con caching
  - Sprites escalados una sola vez
  - Gestión optimizada de memoria
- **Compatibilidad:** Windows, macOS, Linux

## 🎥 Video Demostrativo

**Formato:** MP4, 720p mínimo, relación 16:9  
**Contenido:** Explicación del código, algoritmos de IA y gameplay  
**Ubicación:** [Enlace al video - será agregado]

## 🏆 Características del Examen Implementadas

- ✅ **Algoritmo A*** implementado desde cero
- ✅ **Árboles de Comportamiento** implementados desde cero
- ✅ **Sprites personalizados** para personajes
- ✅ **Sonidos y música** integrados
- ✅ **Soporte para gamepad** obligatorio
- ✅ **Menú completo** (iniciar, reiniciar, configurar)
- ✅ **Sistema de puntuación** y progresión
- ✅ **Comentarios detallados** en código
- ✅ **Historial completo** en Git

## 📝 Notas de Desarrollo

- **Desarrollo:** 100% implementado desde cero
- **IA:** Sin librerías externas para algoritmos
- **Git:** Historial completo de commits
- **Comentarios:** Código completamente documentado
- **Rendimiento:** Optimizado para evaluación

## 📄 Licencia

Proyecto académico - Examen Parcial de Inteligencia Artificial  
**Universidad:**  Universidad o&m
**Materia:** Inteligencia Artificial  
**Profesor:** Yoel Andeyci Pilier Martínez # 🐶 Perro Héroe - Aventura con IA

**Examen Parcial - Inteligencia Artificial**  
**Estudiante:** Alan Alberto Martinez Ubiera  
**Matrícula:** 23-EISN-2-062
**Fecha:** Julio 2025  

## 📋 Descripción

Juego estilo Pac-Man donde un perro héroe debe navegar por laberintos, recoger bonificaciones y evitar enemigos inteligentes. Los enemigos utilizan **algoritmo A*** para perseguir al jugador y **Árboles de Comportamiento** para tomar decisiones estratégicas.

## 🎮 Características

- **5 Niveles progresivos** con dificultad escalable
- **IA Avanzada:**
  - Algoritmo A* implementado desde cero
  - Árboles de Comportamiento para enemigos
- **Sprites personalizados** para perro y enemigos
- **Sistema de puntuación** y vidas
- **Menú interactivo** con opciones de dificultad

## 🧠 Inteligencia Artificial

### Algoritmo A*
Implementado en `scripts/astar.py` para:
- Navegación óptima de enemigos
- Cálculo de rutas más cortas
- Evasión de obstáculos

### Árboles de Comportamiento
Implementados en `scripts/behavior_tree.py` para:
- Decisiones estratégicas de enemigos
- Comportamientos cooperativos
- Adaptación al estado del juego

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Python 3.9 o superior
- Git

### Pasos de Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/Proyecto-Parcial-IA.git
cd Proyecto-Parcial-IA
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Ejecutar el juego:**
```bash
python main.py
```

## 🎯 Controles

- **↑↓←→** - Mover al perro héroe
- **Espacio** - Disparar proyectiles
- **R** - Recargar sprites
- **ESC** - Volver al menú

## 📁 Estructura del Proyecto

```
Proyecto-Parcial-IA/
├── main.py                 # Archivo principal del juego
├── scripts/                # Lógica de IA y juego
│   ├── astar.py           # Algoritmo A* desde cero
│   ├── behavior_tree.py   # Árboles de Comportamiento
│   ├── enemy_behaviors.py # Comportamientos de enemigos
│   └── node.py            # Nodos para árboles
├── resources/             # Recursos del juego
│   └── imagenes/          # Sprites
│       ├── perro.png      # Sprite del protagonista
│       └── fantasma.png   # Sprite del enemigo
├── requirements.txt       # Dependencias Python
└── README.md             # Este archivo
```

## 🎨 Sprites

El juego soporta sprites personalizados:
- `perro.png` - Protagonista perro héroe
- `fantasma.png` - Enemigo fantasma
- `alien.png` - Enemigo alien (opcional)
- `zombie.png` - Enemigo zombie (opcional)

Si no se encuentran sprites, usa emojis como respaldo.

## 🧪 Tecnologías Utilizadas

- **Python 3.13**
- **Pygame 2.6.1**
- **Algoritmos implementados desde cero:**
  - A* (A-Star)
  - Árboles de Comportamiento
  - Pathfinding
  - Gestión de estados

## 📊 Rendimiento

- **FPS:** Configurable (5-12 según dificultad)
- **Optimizaciones:** Pathfinding eficiente, sprites escalados
- **Memoria:** Gestión optimizada de recursos

## 🎥 Video Demostrativo

[Enlace al video explicativo - Formato MP4, 720p mínimo, relación 16:9]

## 📝 Notas de Desarrollo

- Código implementado completamente desde cero
- Sin librerías externas para IA
- Historial completo en Git
- Comentarios detallados en código

## 📄 Licencia

Proyecto académico - Examen Parcial IA