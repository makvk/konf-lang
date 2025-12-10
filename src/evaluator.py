from typing import Any
from src.parser import *

class Evaluator:
    def __init__(self):
        self.env = {}
    
    def evaluate(self, node: Any) -> Any:
        if isinstance(node, Program):
            # Выполняем все утверждения, возвращаем результат последнего
            result = None
            for stmt in node.statements:
                result = self.evaluate(stmt)
            return result
        
        elif isinstance(node, Number):
            return node.value
        
        elif isinstance(node, String):
            return node.value
        
        elif isinstance(node, Array):
            return [self.evaluate(elem) for elem in node.elements]
        
        elif isinstance(node, Dictionary):
            return {k: self.evaluate(v) for k, v in node.pairs.items()}
        
        elif isinstance(node, Variable):
            if node.name not in self.env:
                raise NameError(f"Неизвестная переменная: {node.name}")
            return self.env[node.name]
        
        elif isinstance(node, Let):
            value = self.evaluate(node.value)
            self.env[node.name] = value
            return value
        
        elif isinstance(node, BinOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            
            if node.op == '+':
                # Поддержка сложения разных типов
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            
            raise ValueError(f"Неизвестная операция: {node.op}")
        
        elif isinstance(node, FunctionCall):
            if node.name == 'sort':
                args = [self.evaluate(arg) for arg in node.args]
                if len(args) != 1:
                    raise TypeError(f"sort() ожидает 1 аргумент, получено {len(args)}")
                
                arg = args[0]
                if not isinstance(arg, list):
                    raise TypeError(f"sort() ожидает массив, получено {type(arg).__name__}")
                
                try:
                    return sorted(arg)
                except TypeError as e:
                    raise TypeError(f"Невозможно отсортировать массив: {e}")
            
            raise NameError(f"Неизвестная функция: {node.name}")
        
        else:
            raise TypeError(f"Неизвестный тип узла AST: {type(node).__name__}")