import re
from dataclasses import dataclass
from typing import Any, Union, List, Dict

# ============================
# AST-узлы
# ============================

@dataclass
class Number:
    value: Union[int, float]

@dataclass
class String:
    value: str

@dataclass
class Array:
    elements: List[Any]

@dataclass
class Dictionary:
    pairs: Dict[str, Any]

@dataclass
class Variable:
    name: str

@dataclass
class Let:
    name: str
    value: Any

@dataclass
class BinOp:
    left: Any
    op: str
    right: Any

@dataclass
class FunctionCall:
    name: str
    args: List[Any]

@dataclass
class Program:
    statements: List[Any]

# ============================
# Парсер
# ============================

class Parser:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.length = len(text)
    
    def parse(self) -> Program:
        """Парсит всю программу."""
        statements = []
        
        while self.pos < self.length:
            self.skip_whitespace()
            if self.is_at_end():
                break
            
            try:
                statement = self.parse_statement()
                if statement is not None:
                    statements.append(statement)
            except EOFError:
                break
        
        return Program(statements)
    
    def parse_statement(self) -> Any:
        """Парсит одно утверждение."""
        self.skip_whitespace()
        
        # Проверяем на let
        if self.match('let'):
            return self.parse_let()
        
        # В противном случае парсим как выражение
        return self.parse_expression()
    
    def parse_let(self) -> Let:
        """Парсит объявление константы: let имя = значение"""
        self.skip_whitespace()
        
        # Парсим имя
        name = self.parse_identifier().name
        self.skip_whitespace()
        
        # Ожидаем '='
        if not self.match('='):
            raise SyntaxError(f"Ожидалось '=' после имени переменной '{name}'")
        
        self.skip_whitespace()
        
        # Парсим значение
        value = self.parse_expression()
        
        return Let(name, value)
    
    def parse_const_expr(self):
        """Парсит константное выражение: !{выражение}"""
        # Проверяем, что начинается с '!{'
        if not self.text.startswith('!{', self.pos):
            raise SyntaxError("Ожидалось '!{'")
        
        # Пропускаем '!{'
        self.advance()  # '!'
        self.advance()  # '{'
        self.skip_whitespace()
        
        # Парсим выражение внутри
        expr = self.parse_expression()
        
        # Ожидаем '}'
        self.skip_whitespace()
        if self.peek() != '}':
            raise SyntaxError(f"Ожидалось '' в конце константного выражения, получено: '{self.peek()}'")
        
        self.advance()  # '}'
        return expr
    
    def parse_expression(self) -> Any:
        """Парсит выражение (сложение)."""
        left = self.parse_term()
        
        while self.peek() == '+':
            op = self.advance()
            self.skip_whitespace()
            right = self.parse_term()
            left = BinOp(left, op, right)
        
        return left
    
    def parse_term(self) -> Any:
        """Парсит терм (функции или факторы)."""
        # Проверяем на функцию sort
        if self.match('sort'):
            # Ожидаем открывающую скобку
            self.skip_whitespace()
            if not self.match('('):
                raise SyntaxError(f"Ожидалась '(' после 'sort', получено: '{self.peek()}'")
            
            self.skip_whitespace()
            
            # Парсим аргумент
            arg = self.parse_expression()
            
            # Ожидаем закрывающую скобку
            self.skip_whitespace()
            if not self.match(')'):
                raise SyntaxError(f"Ожидалась ')' после аргумента sort(), получено: '{self.peek()}'")
            
            return FunctionCall('sort', [arg])
        
        return self.parse_factor()

    def parse_factor(self) -> Any:
        """Парсит фактор (числа, строки, переменные, массивы, словари, скобки)."""
        self.skip_whitespace()
        
        # Проверяем на константное выражение
        if self.peek() == '!':
            if self.text.startswith('!{', self.pos):
                return self.parse_const_expr()
        
        if self.peek().isdigit() or self.peek() in '+-.':
            return self.parse_number()
        
        elif self.peek() == '"':
            return self.parse_string()
        
        elif self.match('list('):
            return self.parse_array()
        
        elif self.match('$['):  
            return self.parse_dict()
        
        elif self.peek() == '(':
            self.advance()  # '('
            self.skip_whitespace()
            expr = self.parse_expression()
            self.skip_whitespace()
            if not self.match(')'):
                raise SyntaxError(f"Ожидалась ')', получено: '{self.peek()}'")
            return expr
        
        elif self.peek().isalpha() or self.peek() == '_':
            return self.parse_identifier()
        
        else:
            raise SyntaxError(f"Неожиданный символ в выражении: '{self.peek()}'")
    
    def parse_array(self) -> Array:
        """Парсит массив: list(значение, значение, ...)"""
        # Уже пропустили 'list('
        self.skip_whitespace()
        
        elements = []
        
        # Если сразу закрывающая скобка
        if self.peek() == ')':
            self.advance()  # ')'
            return Array(elements)
        
        # Парсим элементы
        while True:
            element = self.parse_expression()
            elements.append(element)
            
            self.skip_whitespace()
            
            # Если следующая запятая, пропускаем её
            if self.peek() == ',':
                self.advance()
                self.skip_whitespace()
            elif self.peek() == ')':
                self.advance()  # ')'
                break
            else:
                raise SyntaxError(f"Ожидалась ',' или ')' в массиве, получено: '{self.peek()}'")
        
        return Array(elements)
    
    def parse_dict(self) -> Dictionary:
        """Парсит словарь: $[имя: значение, имя: значение, ...]"""
        self.skip_whitespace()
        pairs = {}
        
        # Если сразу закрывающая скобка
        if self.peek() == ']':
            self.advance()  # ']'
            return Dictionary(pairs)
        
        # Парсим пары ключ-значение
        while True:
            key_node = self.parse_identifier()
            key = key_node.name
            
            if self.peek() != ':':
                raise SyntaxError(f"Ожидалось ':' после ключа '{key}' в словаре, получено: '{self.peek()}'")
            
            self.advance()  # ':'
            self.skip_whitespace()
            
            value = self.parse_expression()
            pairs[key] = value
            
            self.skip_whitespace()
            
            # Если следующая запятая, пропускаем её
            if self.peek() == ',':
                self.advance()
                self.skip_whitespace()
            elif self.peek() == ']':
                self.advance()  # ']'
                break
            else:
                raise SyntaxError(f"Ожидалась ',' или ']' в словаре, получено: '{self.peek()}'")
        
        return Dictionary(pairs)
    
    def parse_number(self) -> Number:
        """Парсит число (целое или вещественное)."""
        start = self.pos
        
        # Обработка знака
        if self.peek() in '+-':
            self.advance()
        
        # Парсим целую часть
        while self.pos < self.length and self.text[self.pos].isdigit():
            self.pos += 1
        
        # Парсим дробную часть
        if self.pos < self.length and self.text[self.pos] == '.':
            self.pos += 1
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        
        # Парсим экспоненциальную часть
        if self.pos < self.length and self.text[self.pos].lower() == 'e':
            self.pos += 1
            if self.pos < self.length and self.text[self.pos] in '+-':
                self.pos += 1
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        
        number_str = self.text[start:self.pos]
        
        if not number_str:
            raise SyntaxError("Ожидалось число")
        
        # Преобразуем строку в число
        try:
            if '.' in number_str or 'e' in number_str.lower():
                value = float(number_str)
            else:
                value = int(number_str)
        except ValueError:
            raise SyntaxError(f"Некорректное число: {number_str}")
        
        self.skip_whitespace()
        return Number(value)
    
    def parse_string(self) -> String:
        """Парсит строку в двойных кавычках."""
        self.expect('"')
        
        start = self.pos
        while self.pos < self.length and self.text[self.pos] != '"':
            # Обработка escape-последовательностей
            if self.text[self.pos] == '\\' and self.pos + 1 < self.length:
                self.pos += 2
            else:
                self.pos += 1
        
        if self.pos >= self.length:
            raise SyntaxError("Незакрытая строка")
        
        value = self.text[start:self.pos]
        self.advance()  # Закрывающая кавычка
        
        # Простейшая обработка escape-последовательностей
        value = value.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
        
        self.skip_whitespace()
        return String(value)
    
    def parse_identifier(self) -> Variable:
        """Парсит идентификатор: [_a-zA-Z][_a-zA-Z0-9]*"""
        start = self.pos
        
        # Первый символ
        if self.pos < self.length and (self.text[self.pos].isalpha() or self.text[self.pos] == '_'):
            self.pos += 1
        else:
            raise SyntaxError(f"Ожидался идентификатор, получено: '{self.peek()}'")
        
        # Остальные символы
        while self.pos < self.length and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
            self.pos += 1
        
        name = self.text[start:self.pos]
        
        self.skip_whitespace() 
        
        return Variable(name)
    
    def skip_whitespace(self):
        """Пропускает пробельные символы."""
        while self.pos < self.length and self.text[self.pos].isspace():
            self.pos += 1
    
    def peek(self) -> str:
        """Возвращает символ на текущей позиции."""
        return self.text[self.pos] if self.pos < self.length else ''
    
    def advance(self) -> str:
        """Перемещает позицию на следующий символ и возвращает его."""
        if self.pos >= self.length:
            raise EOFError("Конец входных данных")
        
        ch = self.text[self.pos]
        self.pos += 1
        return ch
    
    def match(self, expected: str) -> bool:
        """Проверяет, начинается ли текст с ожидаемой строки."""
        if self.text.startswith(expected, self.pos):
            self.pos += len(expected)
            return True
        return False
    
    def expect(self, expected: str):
        """Ожидает определенную строку, иначе вызывает ошибку."""
        if not self.match(expected):
            raise SyntaxError(f"Ожидалось '{expected}', получено: '{self.peek()}'")
    
    def is_at_end(self) -> bool:
        """Проверяет, достигнут ли конец входных данных."""
        return self.pos >= self.length