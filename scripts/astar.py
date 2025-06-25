"""
astar.py - Implementación del algoritmo A* para pathfinding
Autor: [Tu nombre y matrícula]
"""

import heapq
from .node import Node

class AStar:
    """
    Implementación del algoritmo A* para encontrar el camino más corto
    en un laberinto representado como matriz 2D
    """
    
    def __init__(self, maze):
        """
        Inicializa el pathfinder con el laberinto
        
        Args:
            maze: Matriz 2D donde 1 = pared, 0 = espacio libre, 2 = objetivo especial
        """
        self.maze = maze
        self.height = len(maze)
        self.width = len(maze[0]) if maze else 0
        
        # Direcciones de movimiento: arriba, derecha, abajo, izquierda
        self.directions = [
            (0, -1),  # Arriba
            (1, 0),   # Derecha  
            (0, 1),   # Abajo
            (-1, 0)   # Izquierda
        ]
    
    def heuristic(self, node1, node2):
        """
        Función heurística: Distancia Manhattan
        
        Args:
            node1: Nodo inicial
            node2: Nodo objetivo
            
        Returns:
            int: Distancia Manhattan entre los nodos
        """
        return abs(node1.x - node2.x) + abs(node1.y - node2.y)
    
    def is_valid_position(self, x, y):
        """
        Verifica si una posición es válida (dentro del laberinto y no es pared)
        
        Args:
            x: Coordenada X
            y: Coordenada Y
            
        Returns:
            bool: True si la posición es válida
        """
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                self.maze[y][x] != 1)  # 1 = pared
    
    def get_neighbors(self, node):
        """
        Obtiene los nodos vecinos válidos de un nodo dado
        
        Args:
            node: Nodo actual
            
        Returns:
            list: Lista de nodos vecinos válidos
        """
        neighbors = []
        
        for dx, dy in self.directions:
            new_x = node.x + dx
            new_y = node.y + dy
            
            if self.is_valid_position(new_x, new_y):
                neighbors.append(Node(new_x, new_y))
        
        return neighbors
    
    def reconstruct_path(self, node):
        """
        Reconstruye el camino desde el nodo objetivo hasta el inicio
        
        Args:
            node: Nodo objetivo con referencias a sus padres
            
        Returns:
            list: Lista de posiciones (x, y) que forman el camino
        """
        path = []
        current = node
        
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        
        # Invertir para obtener el camino desde inicio hasta objetivo
        path.reverse()
        return path
    
    def find_path(self, start_x, start_y, goal_x, goal_y):
        """
        Encuentra el camino más corto usando el algoritmo A*
        
        Args:
            start_x: Coordenada X de inicio
            start_y: Coordenada Y de inicio
            goal_x: Coordenada X del objetivo
            goal_y: Coordenada Y del objetivo
            
        Returns:
            list: Lista de posiciones (x, y) que forman el camino, 
                  o lista vacía si no hay camino
        """
        # Verificar que las posiciones de inicio y objetivo sean válidas
        if not self.is_valid_position(start_x, start_y):
            return []
        if not self.is_valid_position(goal_x, goal_y):
            return []
        
        # Si ya estamos en el objetivo
        if start_x == goal_x and start_y == goal_y:
            return [(start_x, start_y)]
        
        # Crear nodos de inicio y objetivo
        start_node = Node(start_x, start_y)
        goal_node = Node(goal_x, goal_y)
        
        # Listas abierta y cerrada
        open_list = []  # Cola de prioridad (heap)
        closed_set = set()  # Conjunto de nodos ya explorados
        
        # Agregar nodo inicial a la lista abierta
        heapq.heappush(open_list, start_node)
        
        # Diccionario para rastrear el mejor costo g para cada posición
        g_costs = {start_node.position: 0}
        
        while open_list:
            # Obtener el nodo con menor f_cost
            current_node = heapq.heappop(open_list)
            
            # Si llegamos al objetivo
            if current_node == goal_node:
                return self.reconstruct_path(current_node)
            
            # Marcar como explorado
            closed_set.add(current_node.position)
            
            # Explorar vecinos
            for neighbor in self.get_neighbors(current_node):
                neighbor_pos = neighbor.position
                
                # Si ya fue explorado, continuar
                if neighbor_pos in closed_set:
                    continue
                
                # Calcular nuevo g_cost
                tentative_g_cost = current_node.g_cost + 1
                
                # Si encontramos un mejor camino a este vecino
                if (neighbor_pos not in g_costs or 
                    tentative_g_cost < g_costs[neighbor_pos]):
                    
                    # Actualizar el vecino
                    neighbor.parent = current_node
                    neighbor.g_cost = tentative_g_cost
                    neighbor.h_cost = self.heuristic(neighbor, goal_node)
                    
                    # Actualizar g_costs
                    g_costs[neighbor_pos] = tentative_g_cost
                    
                    # Agregar a la lista abierta si no está
                    heapq.heappush(open_list, neighbor)
        
        # No se encontró camino
        return []
    
    def get_next_move(self, start_x, start_y, goal_x, goal_y):
        """
        Obtiene la siguiente dirección de movimiento hacia el objetivo
        
        Args:
            start_x: Coordenada X de inicio
            start_y: Coordenada Y de inicio  
            goal_x: Coordenada X del objetivo
            goal_y: Coordenada Y del objetivo
            
        Returns:
            tuple: (dx, dy) dirección del siguiente movimiento, 
                   o (0, 0) si no hay camino
        """
        path = self.find_path(start_x, start_y, goal_x, goal_y)
        
        if len(path) >= 2:
            # Obtener la siguiente posición en el camino
            next_pos = path[1]  # path[0] es la posición actual
            
            # Calcular la dirección
            dx = next_pos[0] - start_x
            dy = next_pos[1] - start_y
            
            return (dx, dy)
        
        return (0, 0)  # No hay movimiento o ya está en el objetivo