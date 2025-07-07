# 🔥 Dimensiones Infernales - Sistema de IA Avanzado

**Examen Parcial - Inteligencia Artificial**  
**Estudiante:** Alan Alberto Martinez Ubiera  
**Matrícula:** 23-EISN-2-062  
**Email:** aalann34@gmail.com  
**Universidad:** Universidad O&M  
**Materia:** Inteligencia Artificial  
**Profesor:** Yoel Andeyci Pilier Martínez  
**Fecha:** 5 de Julio, 2025  

## 📋 Descripción del Proyecto

Juego de acción estilo laberinto donde un **héroe valiente** debe navegar por **dimensiones infernales**, recolectar **diamantes mágicos** y enfrentar **criaturas demoníacas** con inteligencia artificial avanzada. Los enemigos utilizan **algoritmo A*** para perseguir al jugador y **Árboles de Comportamiento** para tomar decisiones estratégicas.

**🎯 OBJETIVO:** Recolecta los 5 diamantes 💎 para abrir las puertas infernales 🚪 y avanzar al siguiente nivel.

## 🚀 Características Principales

### 🎮 **Experiencia de Juego**
- ✅ **5 niveles progresivos** con temática infernal única
- ✅ **Sistema de diamantes obligatorios** - debes recoger TODOS para avanzar
- ✅ **Puertas dinámicas** - se abren solo cuando recoges todos los diamantes
- ✅ **3 dificultades** - Alma Perdida (5 FPS), Demonio (7 FPS), Señor del Infierno (9 FPS)
- ✅ **Sistema de vidas** con indicadores visuales personalizados
- ✅ **Puntuación avanzada** con bonus por eliminar enemigos (150 puntos cada uno)

### 🖥️ **Sistema de Auto-Escalado Inteligente**
- ✅ **Detección automática** de resolución de pantalla
- ✅ **Escalado inteligente** de elementos del juego según el monitor
- ✅ **Laberinto grande y visible** optimizado para cualquier pantalla
- ✅ **Fuentes adaptativas** que se ajustan automáticamente
- ✅ **Pantalla completa** con F11 y auto-maximizado al inicio
- ✅ **Ajuste dinámico** del tamaño con +/- en tiempo real

### 🎯 **Sistema de Combate Avanzado**
- ✅ **Disparo ilimitado** - SIEMPRE puedes disparar, sin restricciones
- ✅ **Aim bot inteligente** - guiado automático hacia enemigos cercanos (rango de 6 casillas)
- ✅ **Proyectiles rápidos** - se mueven a velocidad 2x para mayor responsividad
- ✅ **Límite de 3 proyectiles** simultáneos para equilibrar el gameplay
- ✅ **Indicador visual** del estado del aim bot (ACTIVO/ESPERANDO/MANUAL)
- ✅ **Proyectiles realistas** con efectos de rotación, estela y partículas

### 👾 **Criaturas Infernales con IA Única**
- ✅ **7 tipos de enemigos** con comportamientos completamente únicos
- ✅ **Habilidades especiales** específicas para cada tipo de criatura
- ✅ **Spawn inteligente** en posiciones seguras (zona 5x5 alrededor del jugador protegida)
- ✅ **IA cooperativa** - algunos enemigos coordinan estrategias
- ✅ **Comportamientos dinámicos** que se adaptan al estado del juego

## 🧠 Inteligencia Artificial Implementada

### 🎯 **Algoritmo A* (A-Star)**
**Ubicación:** `scripts/astar.py`
- **Implementación:** 100% desde cero, sin librerías externas
- **Características:**
  - Cálculo de rutas más cortas en tiempo real
  - Evasión inteligente de obstáculos
  - Optimización de movimiento para todos los tipos de enemigos
  - Pathfinding eficiente con sistema de heurística Manhattan
  - Soporte para mapas dinámicos con validación de posiciones

### 🌳 **Árboles de Comportamiento**
**Ubicación:** `scripts/behavior_tree.py`, `scripts/enemy_behaviors.py`
- **Implementación:** Sistema completo desde cero
- **Funcionalidades:**
  - **Nodos de Condición** - Evaluación de estados del juego
  - **Nodos de Acción** - Movimientos y decisiones estratégicas
  - **Nodos Composite** - Secuencias y selectores complejos (Sequence, Selector)
  - **Nodos Decoradores** - Inverter, Timer para comportamientos avanzados
  - **Blackboard System** - Memoria compartida entre nodos

### 👹 **Comportamientos Específicos por Enemigo:**

#### 👽 **Alien - Perseguidor Inteligente**
- Usa A* para persecución eficiente
- Velocidad controlada (delay 0.3s)
- Pathfinding óptimo hacia el jugador

#### 👻 **Fantasma - Maestro de la Invisibilidad**
- **Sistema de invisibilidad temporal** (2.5s invisible, 4s cooldown)
- Teletransporte aleatorio cuando se vuelve invisible
- Huye del jugador cuando está visible y cerca
- Efectos de sonido especiales para invisibilidad

#### 🧟 **Zombie - Horda Implacable**
- **Persecución lenta pero constante** (delay 0.8s)
- **Sistema de horda** - se acelera cuando hay otros zombies cerca
- **Memoria de olfato** - sigue rastros del jugador durante 5 segundos
- Boost de velocidad 40% cuando forma horda

#### 🦹 **Villano - Estratega Táctico**
- Alterna entre persecución directa y emboscadas
- Predice movimientos del jugador para emboscadas
- Cambia de estrategia cada 8 segundos
- Comportamiento balanceado (delay 0.5s)

#### 👺 **Demonio - Teletransportador Aleatorio**
- **Teletransporte completamente aleatorio** a cualquier posición válida del mapa
- Cooldown de 4 segundos entre teletransportes
- Movimiento normal lento entre teletransportes
- Efectos de sonido únicos para teletransporte

#### 🤡 **Payaso - Caos Impredecible**
- **4 modos de velocidad** que cambia aleatoriamente (lento, normal, rápido, loco)
- **Imitación de movimientos** del jugador con delay
- **Modo confusión** con movimientos erráticos
- **Comportamiento de burla** (acercarse y alejarse)

#### 👹 **Diablo - Líder de Manada**
- Comportamiento base inteligente con A*
- Diseñado para coordinación con otros enemigos
- Pathfinding eficiente y agresivo

### 🎯 **Sistema de Aim Bot Avanzado**
**Ubicación:** `main.py` - Clase `AimBot`
- **Implementación:** Sistema inteligente desde cero
- **Características:**
  - Detección automática de enemigos en rango de 6 casillas
  - Cálculo de dirección óptima usando distancia euclidiana
  - Indicador visual de objetivos activos
  - Toggle con tecla A (activar/desactivar)
  - Integración perfecta con el sistema de disparo

## 🎮 Controles

### ⌨️ **Teclado**
- **↑↓←→** - Mover al héroe protagonista
- **ESPACIO** - Disparar proyectiles (SIEMPRE funciona)
- **A** - Activar/desactivar aim bot
- **R** - Recargar sprites en tiempo real
- **ESC** - Volver al menú principal
- **F11** - Pantalla completa ON/OFF
- **+/-** - Ajustar tamaño del laberinto dinámicamente

### 🎮 **Control Xbox 360 (Soporte Completo)**
- **Joystick Izquierdo/D-pad** - Mover al héroe protagonista
- **Botón A** - Disparar proyectiles
- **Botón B** - Volver al menú/salir del juego
- **Navegación en menús** - Joystick + A/B para seleccionar
- **Detección automática** de conexión/desconexión

## 🎨 Sistema de Sprites Automático

### 📁 **Estructura de Assets**
```
assets/
├── images/                # Sprites personalizados (PNG)
│   ├── perro.png         # 🐶 Protagonista héroe (con direcciones automáticas)
│   ├── fantasma.png      # 👻 Enemigo fantasma
│   ├── alien.png         # 👽 Enemigo alien
│   ├── zombie.png        # 🧟 Enemigo zombie
│   ├── villano.png       # 🦹 Enemigo villano
│   ├── demonio.png       # 👺 Enemigo demonio
│   ├── payaso.png        # 🤡 Enemigo payaso
│   ├── diablo.png        # 👹 Enemigo diablo
│   ├── caca.png          # 💩 Proyectiles (con efectos de rotación)
│   ├── bloquerojo.png    # 🧱 Paredes infernales
│   ├── diamante.png      # 💎 Diamantes mágicos (con brillo dorado)
│   ├── puerta.png        # 🚪 Puertas infernales (abierta/cerrada)
│   ├── corazon.png       # 💖 Vidas del jugador
│   ├── humo.png          # 💨 Efecto de invisibilidad del fantasma
│   ├── fuego.png         # 🔥 Sprites de fuego (para UI y efectos)
│   └── portada.png       # 🖼️ Imagen del menú principal
├── sounds/               # Efectos de sonido (WAV)
│   ├── disparo.wav       # 🔫 Sonido de disparo
│   ├── diamante.wav      # 💎 Sonido de recolección
│   ├── puerta.wav        # 🚪 Sonido de puerta abriéndose
│   ├── muerte.wav        # 💀 Sonido de pérdida de vida
│   ├── click.wav         # 🖱️ Sonido de navegación en menús
│   ├── fantasma.wav      # 👻 Sonido de invisibilidad
│   └── teletransporte.wav # ✨ Sonido de teletransporte del demonio
└── music/               # Música de fondo (MP3)
    ├── menu.mp3         # 🎵 Música del menú
    ├── juego.mp3        # 🎵 Música durante el gameplay
    ├── victoria.mp3     # 🏆 Música de victoria
    └── derrota.mp3      # 💀 Música de derrota
```

### 🔄 **Características de Carga**
- ✅ **Detección automática** de sprites al iniciar
- ✅ **Escalado inteligente** automático al tamaño de pantalla detectado
- ✅ **Fallback robusto** - usa emojis si no encuentra sprites
- ✅ **Efectos especiales** - rotación, brillo, transparencias
- ✅ **Recarga en tiempo real** con tecla R
- ✅ **Informes detallados** de estado de carga

## 🔊 Sistema de Audio Completo

### 🎵 **Características**
- ✅ **4 pistas de música** con transiciones automáticas entre estados
- ✅ **7 efectos de sonido** contextuales para diferentes acciones
- ✅ **Volumen balanceado** automáticamente (música 30-40%, sonidos 50-80%)
- ✅ **Detección automática** de archivos con informes detallados
- ✅ **Fallback silencioso** - el juego funciona sin audio

### 🎧 **Implementación**
- **Música del menú** se reproduce automáticamente al iniciar
- **Música de juego** cambia automáticamente al iniciar partida
- **Música de victoria/derrota** según el resultado final
- **Efectos contextuales** específicos para cada acción del juego
- **Sonidos únicos** para habilidades especiales de enemigos

## 🏗️ Instalación y Ejecución

### 📋 **Prerrequisitos**
- **Python 3.9 o superior**
- **Git** (para clonar el repositorio)
- **Control Xbox 360** (opcional pero recomendado)

### 🚀 **Pasos de Instalación**

1. **Clonar el repositorio:**
```bash
git clone https://github.com/aalann34/Proyecto-Parcial-IA.git
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

### 📁 **Estructura del Proyecto**

```
Proyecto-Parcial-IA/
├── main.py                 # 🎮 Archivo principal del juego (2000+ líneas)
├── scripts/                # 🧠 Módulos de IA y lógica
│   ├── __init__.py        # 📦 Inicializador del módulo
│   ├── astar.py           # 🎯 Algoritmo A* desde cero (150+ líneas)
│   ├── behavior_tree.py   # 🌳 Sistema de árboles de comportamiento (200+ líneas)
│   ├── enemy_behaviors.py # 👾 Comportamientos específicos (800+ líneas)
│   └── node.py            # 🔗 Nodos para árboles de comportamiento (50+ líneas)
├── assets/                # 🎨 Recursos del juego
│   ├── images/            # 🖼️ Sprites y gráficos (14 archivos PNG)
│   ├── sounds/            # 🔊 Efectos de sonido (7 archivos WAV)
│   └── music/             # 🎵 Música de fondo (4 archivos MP3)
├── requirements.txt       # 📋 Dependencias de Python
└── README.md             # 📖 Documentación completa
```

## 🎯 Niveles del Juego

### 🔥 **5 Dimensiones Infernales**
1. **🚪 Portal de Entrada** (Principiante) - 5 diamantes distribuidos estratégicamente
2. **⚰️ Cámaras de Tormento** (Iniciado) - 5 diamantes en configuración desafiante  
3. **🔥 Laberinto de Fuego** (Guerrero) - 5 diamantes en laberinto complejo
4. **🏰 Fortaleza Demoníaca** (Veterano) - 5 diamantes en diseño táctico
5. **👑 Trono de Lucifer** (Señor Infernal) - 5 diamantes en configuración épica

### ⚡ **Dificultades**
- **😈 Alma Perdida (Fácil)** - 5 FPS, enemigos lentos, más tiempo para estrategia
- **👹 Demonio (Medio)** - 7 FPS, velocidad equilibrada, dificultad balanceada
- **🔥 Señor del Infierno (Difícil)** - 9 FPS, velocidad máxima, desafío extremo

### 🎭 **Sistema de Enemigos por Nivel**
- **Nivel 1:** 3 enemigos aleatorios
- **Nivel 2:** 4 enemigos aleatorios  
- **Nivel 3:** 4 enemigos aleatorios
- **Nivel 4:** 5 enemigos aleatorios
- **Nivel 5:** 5 enemigos aleatorios (batalla final épica)

## 🧪 Tecnologías y Algoritmos

### 📚 **Librerías Utilizadas**
- **Python 3.13** - Lenguaje principal
- **Pygame 2.6.1** - Motor gráfico, audio y controles
- **Matemáticas nativas** - Sin librerías externas para IA

### 🔧 **Algoritmos Implementados 100% Desde Cero**
- **🎯 A* (A-Star)** - Pathfinding y navegación inteligente
- **🌳 Árboles de Comportamiento** - IA compleja de enemigos
- **🎮 Máquina de Estados** - Gestión de menús y gameplay
- **💥 Detección de Colisiones** - Física básica del juego
- **🎯 Aim Bot Inteligente** - Asistencia de disparo con detección de rango
- **📐 Auto-Escalado** - Adaptación automática a cualquier resolución

## 📊 Optimizaciones y Rendimiento

### ⚡ **Rendimiento**
- **FPS Configurable:** 5-9 FPS según dificultad seleccionada
- **Pathfinding Eficiente:** A* optimizado con validación rápida
- **Sprites Optimizados:** Escalado una sola vez al cargar
- **Memoria Gestionada:** Limpieza automática de proyectiles y estados
- **Detección Inteligente:** Solo verifica colisiones necesarias

### 🖥️ **Compatibilidad**
- **✅ Windows** (optimizado para Windows 10/11)
- **✅ macOS** (compatible con versiones recientes)
- **✅ Linux** (Ubuntu, Debian, Fedora)
- **🎮 Xbox 360 Controller** (detección automática de conexión/desconexión)

## 🔍 Características Técnicas Avanzadas

### 🎨 **Sistema de Rendering**
- **Auto-escalado inteligente** según resolución detectada automáticamente
- **Efectos visuales avanzados** - brillos, transparencias, animaciones suaves
- **Efectos especiales únicos** - sprite de humo para invisibilidad, rotación de proyectiles
- **UI adaptativa** que se ajusta perfectamente a cualquier tamaño de pantalla
- **Mensajes temporales** con efectos de fade y transparencia

### 🧠 **IA Avanzada**
- **Comportamiento emergente** - enemigos coordinan estrategias complejas
- **Estados dinámicos** - enemigos reaccionan inteligentemente al entorno
- **Habilidades únicas** - cada tipo tiene características completamente diferentes
- **Pathfinding cooperativo** - enemigos evitan chocar entre sí
- **Sistema de memoria** - algunos enemigos recuerdan posiciones del jugador

### 🎮 **Experiencia de Usuario**
- **Menús interactivos** con navegación fluida por teclado y control
- **Feedback visual inmediato** para todas las acciones del jugador
- **Sistema de ayuda** integrado en la UI con información contextual
- **Configuración dinámica** - ajustes en tiempo real sin reiniciar

## 🏆 Cumplimiento de Requisitos del Examen

- ✅ **Algoritmo A*** implementado completamente desde cero (150+ líneas)
- ✅ **Árboles de Comportamiento** implementados desde cero (1000+ líneas total)
- ✅ **Sprites personalizados** para todos los personajes y elementos
- ✅ **Sistema de sonidos y música** completamente integrado y funcional
- ✅ **Soporte obligatorio para gamepad** Xbox 360 con detección automática
- ✅ **Menú completo** con opciones de inicio, configuración y salida
- ✅ **Sistema de puntuación** con progresión y vidas
- ✅ **Comentarios detallados** en todo el código fuente
- ✅ **Historial completo en Git** con commits organizados y descriptivos
- ✅ **README completo** con instalación y documentación técnica
- ✅ **Funcionalidad extra:** Sistema de auto-escalado, aim bot y efectos avanzados

## 🎥 Video Demostrativo

**Formato:** MP4, 1080p, relación 16:9  
**Contenido incluido:**
- ✅ Explicación detallada del código A* y su implementación
- ✅ Demostración completa de Árboles de Comportamiento por enemigo
- ✅ Gameplay completo mostrando todas las características
- ✅ Explicación técnica de la implementación de IA desde cero
- ✅ Demostración del sistema de sprites, audio y controles

**Ubicación:** [Será proporcionado antes de la presentación]

## 📝 Estadísticas del Proyecto

### 📈 **Métricas de Desarrollo**
- **Líneas de código:** 3200+ líneas de Python puro
- **Archivos principales:** 5 módulos organizados por funcionalidad
- **Sprites soportados:** 14 sprites personalizados con efectos
- **Efectos de audio:** 7 sonidos + 4 músicas con integración perfecta
- **Algoritmos IA:** 2 algoritmos principales implementados desde cero
- **Comportamientos únicos:** 7 tipos de enemigos con IA diferenciada
- **Tiempo de desarrollo:** 4 semanas de programación intensiva

### 🎯 **Características Únicas**
- **Sistema de auto-escalado** que se adapta a cualquier resolución
- **Aim bot inteligente** con detección de rango y direccionamiento automático
- **Enemigos con habilidades especiales** (invisibilidad, teletransporte, horda)
- **Proyectiles realistas** con efectos de rotación, estela y partículas
- **Audio contextual** con efectos específicos para cada habilidad especial
- **Interfaz completamente adaptativa** con sprites de fuego personalizados

## 🆘 Solución de Problemas

### 🔧 **Problemas Comunes**
```bash
# Si pygame no se instala correctamente:
pip install --upgrade pip
pip install pygame==2.6.1

# Si el control no se detecta:
# Conectar control Xbox 360 antes de ejecutar el juego
# Verificar que Windows reconozca el control en Dispositivos

# Si faltan sprites o audio:
# El juego usa emojis y funcionamiento silencioso como respaldo
# Verificar que las carpetas assets/images/, assets/sounds/, assets/music/ existan
# Revisar que los nombres de archivo coincidan exactamente

# Si el juego va muy rápido o lento:
# Cambiar dificultad en el menú (Fácil: 5 FPS, Medio: 7 FPS, Difícil: 9 FPS)
# Usar +/- para ajustar tamaño del laberinto si afecta rendimiento
```

### 🎮 **Consejos de Gameplay**
- **Usa el aim bot** (tecla A) para facilitar el combate contra múltiples enemigos
- **Observa los patrones** de comportamiento de cada tipo de enemigo
- **Los fantasmas invisibles** no pueden ser golpeados - espera a que sean visibles
- **Los zombies en horda** se mueven más rápido - sepáralos si es posible
- **El demonio se teletransporta** aleatoriamente - mantente alerta
- **Recolecta los 5 diamantes** antes de ir a la puerta - estará cerrada sin ellos

### 📞 **Información de Contacto**
- **Estudiante:** Alan Alberto Martinez Ubiera
- **Matrícula:** 23-EISN-2-062
- **Universidad:** Universidad O&M
- **Email:** aalann34@gmail.com

## 📄 Información Académica

**Universidad:** Universidad O&M  
**Carrera:** Ingeniería en Sistemas y Computación  
**Materia:** Inteligencia Artificial  
**Profesor:** Yoel Andeyci Pilier Martínez  
**Periodo:** Julio 2025  
**Tipo:** Examen Parcial - Proyecto Final (20 puntos)  

### 📋 **Criterios Cumplidos al 100%**
- ✅ **Implementación original** de algoritmos de IA sin uso de librerías externas
- ✅ **Funcionalidad completa** del juego con todos los requisitos
- ✅ **Documentación técnica** detallada y profesional
- ✅ **Presentación profesional** del código con comentarios explicativos
- ✅ **Video demostrativo** explicativo completo
- ✅ **Entrega puntual** y organizada según especificaciones
- ✅ **Características adicionales** que superan los requisitos mínimos

### 🎖️ **Logros Técnicos**
- **A* desde cero:** Implementación completa del algoritmo de pathfinding
- **Árboles de Comportamiento:** Sistema complejo con 7 comportamientos únicos
- **Auto-escalado:** Sistema inteligente de adaptación a cualquier pantalla
- **Audio integrado:** Sistema completo de música y efectos de sonido
- **Controles duales:** Soporte perfecto para teclado y Xbox 360
- **Sprites personalizados:** Sistema completo de carga y escalado automático

---

**🔥 ¡Bienvenido a las Dimensiones Infernales! ¡Demuestra tu valor enfrentando las criaturas del abismo! 🔥**

*Este proyecto representa la culminación de conocimientos en Inteligencia Artificial, desarrollo de videojuegos y programación avanzada en Python, implementando algoritmos complejos desde cero y creando una experiencia de juego completa y profesional.*