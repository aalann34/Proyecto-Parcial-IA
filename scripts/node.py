"""
Node.py - Clase Node para el algoritmo A*
Autor: Alan Alberto Martinez Ubiera - 23-EISN-2-062
"""

class Node:
    """
    Representa un nodo en el algoritmo A*
    """
    def __init__(self, x, y, g_cost=0, h_cost=0, parent=None):
        self.x = x  # Coordenada X
        self.y = y  # Coordenada Y
        self.g_cost = g_cost  # Costo desde el inicio
        self.h_cost = h_cost  # Heurística (distancia estimada al objetivo)
        self.parent = parent  # Nodo padre para reconstruir el camino
    
    @property
    def f_cost(self):
        """Costo total f(n) = g(n) + h(n)"""
        return self.g_cost + self.h_cost
    
    @property
    def position(self):
        """Retorna la posición como tupla (x, y)"""
        return (self.x, self.y)
    
    def __eq__(self, other):
        """Compara dos nodos por su posición"""
        if isinstance(other, Node):
            return self.x == other.x and self.y == other.y
        return False
    
    def __lt__(self, other):
        """Comparación para la cola de prioridad (heap)"""
        if isinstance(other, Node):
            return self.f_cost < other.f_cost
        return False
    
    def __hash__(self):
        """Hash para usar en sets y diccionarios"""
        return hash((self.x, self.y))
    
    def __repr__(self):
        """Representación string para debugging"""
        return f"Node({self.x}, {self.y}, f={self.f_cost})"