"""
behavior_tree.py - Sistema base de Árboles de Comportamiento
Autor: Alan Alberto Martinez Ubiera - 23-EISN-2-062
"""

import time
from enum import Enum

class BehaviorState(Enum):
    """Estados posibles de un nodo de comportamiento"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE" 
    RUNNING = "RUNNING"

class BehaviorNode:
    """Nodo base para todos los elementos del árbol de comportamiento"""
    
    def __init__(self, name="BehaviorNode"):
        self.name = name
        self.children = []
        self.parent = None
        
    def add_child(self, child):
        """Agrega un nodo hijo"""
        child.parent = self
        self.children.append(child)
        
    def execute(self, blackboard=None):
        """Ejecuta el nodo - debe ser implementado por subclases"""
        return BehaviorState.FAILURE

class Selector(BehaviorNode):
    """
    Nodo Selector - Ejecuta hijos hasta que uno tenga éxito
    Retorna SUCCESS si algún hijo tiene éxito
    Retorna FAILURE si todos los hijos fallan
    """
    
    def __init__(self, name="Selector"):
        super().__init__(name)
        
    def execute(self, blackboard=None):
        for child in self.children:
            result = child.execute(blackboard)
            
            if result == BehaviorState.SUCCESS:
                return BehaviorState.SUCCESS
            elif result == BehaviorState.RUNNING:
                return BehaviorState.RUNNING
                
        return BehaviorState.FAILURE

class Sequence(BehaviorNode):
    """
    Nodo Secuencia - Ejecuta todos los hijos en orden
    Retorna SUCCESS solo si todos los hijos tienen éxito
    Retorna FAILURE si algún hijo falla
    """
    
    def __init__(self, name="Sequence"):
        super().__init__(name)
        
    def execute(self, blackboard=None):
        for child in self.children:
            result = child.execute(blackboard)
            
            if result == BehaviorState.FAILURE:
                return BehaviorState.FAILURE
            elif result == BehaviorState.RUNNING:
                return BehaviorState.RUNNING
                
        return BehaviorState.SUCCESS

class Action(BehaviorNode):
    """
    Nodo Acción - Ejecuta una función específica
    """
    
    def __init__(self, action_function, name="Action"):
        super().__init__(name)
        self.action_function = action_function
        
    def execute(self, blackboard=None):
        try:
            if blackboard is not None:
                result = self.action_function(blackboard)
            else:
                result = self.action_function()
                
            # Convertir resultado booleano a BehaviorState
            if isinstance(result, bool):
                return BehaviorState.SUCCESS if result else BehaviorState.FAILURE
            elif isinstance(result, BehaviorState):
                return result
            else:
                return BehaviorState.SUCCESS if result else BehaviorState.FAILURE
                
        except Exception as e:
            print(f"Error en acción {self.name}: {e}")
            return BehaviorState.FAILURE

class Condition(BehaviorNode):
    """
    Nodo Condición - Evalúa una condición sin efectos secundarios
    """
    
    def __init__(self, condition_function, name="Condition"):
        super().__init__(name)
        self.condition_function = condition_function
        
    def execute(self, blackboard=None):
        try:
            if blackboard is not None:
                result = self.condition_function(blackboard)
            else:
                result = self.condition_function()
                
            return BehaviorState.SUCCESS if result else BehaviorState.FAILURE
            
        except Exception as e:
            print(f"Error en condición {self.name}: {e}")
            return BehaviorState.FAILURE

class Inverter(BehaviorNode):
    """
    Nodo Inversor - Invierte el resultado de su hijo
    SUCCESS -> FAILURE
    FAILURE -> SUCCESS
    RUNNING -> RUNNING
    """
    
    def __init__(self, child=None, name="Inverter"):
        super().__init__(name)
        if child:
            self.add_child(child)
            
    def execute(self, blackboard=None):
        if not self.children:
            return BehaviorState.FAILURE
            
        result = self.children[0].execute(blackboard)
        
        if result == BehaviorState.SUCCESS:
            return BehaviorState.FAILURE
        elif result == BehaviorState.FAILURE:
            return BehaviorState.SUCCESS
        else:  # RUNNING
            return BehaviorState.RUNNING

class Timer(BehaviorNode):
    """
    Nodo Timer - Ejecuta su hijo después de un delay
    """
    
    def __init__(self, delay_seconds, child=None, name="Timer"):
        super().__init__(name)
        self.delay_seconds = delay_seconds
        self.start_time = None
        if child:
            self.add_child(child)
            
    def execute(self, blackboard=None):
        if not self.children:
            return BehaviorState.FAILURE
            
        current_time = time.time()
        
        # Iniciar el timer si no está iniciado
        if self.start_time is None:
            self.start_time = current_time
            return BehaviorState.RUNNING
            
        # Verificar si el tiempo ha pasado
        if current_time - self.start_time >= self.delay_seconds:
            # Resetear el timer
            self.start_time = None
            # Ejecutar el hijo
            return self.children[0].execute(blackboard)
        else:
            return BehaviorState.RUNNING

class BehaviorTree:
    """
    Árbol de Comportamiento principal que maneja la ejecución
    """
    
    def __init__(self, root_node, name="BehaviorTree"):
        self.root = root_node
        self.name = name
        self.blackboard = {}  # Memoria compartida para el árbol
        
    def execute(self):
        """Ejecuta el árbol de comportamiento"""
        if self.root:
            return self.root.execute(self.blackboard)
        return BehaviorState.FAILURE
        
    def set_blackboard_value(self, key, value):
        """Establece un valor en la pizarra"""
        self.blackboard[key] = value
        
    def get_blackboard_value(self, key, default=None):
        """Obtiene un valor de la pizarra"""
        return self.blackboard.get(key, default)
        
    def reset(self):
        """Resetea el estado del árbol"""
        self.blackboard.clear()