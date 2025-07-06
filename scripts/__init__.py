"""
scripts/__init__.py
Paquete de módulos para Dimensiones Infernales
Estudiante: Alan Alberto Martinez Ubiera 
Matrícula: 23-EISN-2-062
Email: aalann34@gmail.com
"""

from .astar import AStar
from .node import Node
from .behavior_tree import (
    BehaviorTree, BehaviorState, BehaviorNode, 
    Selector, Sequence, Action, Condition, Inverter, Timer
)
from .enemy_behaviors import (
    EnemyBehavior, AlienBehavior, GhostBehavior, 
    ZombieBehavior, VillainBehavior, DemonBehavior, ClownBehavior,
    create_enemy_behavior
)

__all__ = [
    'AStar', 'Node',
    'BehaviorTree', 'BehaviorState', 'BehaviorNode',
    'Selector', 'Sequence', 'Action', 'Condition', 'Inverter', 'Timer',
    'EnemyBehavior', 'AlienBehavior', 'GhostBehavior', 
    'ZombieBehavior', 'VillainBehavior', 'DemonBehavior', 'ClownBehavior',
    'create_enemy_behavior'
]