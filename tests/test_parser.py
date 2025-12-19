import sys
import os

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser import Parser
from src.evaluator import Evaluator
import pytest


def test_numbers():
    parser = Parser("42")
    ast = parser.parse()
    evaluator = Evaluator()
    result = evaluator.evaluate(ast)
    assert result == 42

def test_let_and_add():
    parser = Parser("let x = 5 !{x + 3}")
    ast = parser.parse()
    evaluator = Evaluator()
    result = evaluator.evaluate(ast)
    assert result == 8

def test_array():
    parser = Parser("list(1, 2, 3)")
    ast = parser.parse()
    evaluator = Evaluator()
    result = evaluator.evaluate(ast)
    assert result == [1, 2, 3]

def test_sort():
    parser = Parser("!{sort(list(3, 1, 2))}")
    ast = parser.parse()
    evaluator = Evaluator()
    result = evaluator.evaluate(ast)
    assert result == [1, 2, 3]

def test_dict():
    """Тест парсинга словарей с правильным синтаксисом $[...]."""
    parser = Parser('$[name: "test", value: 42]')
    ast = parser.parse()
    evaluator = Evaluator()
    result = evaluator.evaluate(ast)
    assert result == {"name": "test", "value": 42}
    
    # Пустой словарь
    parser = Parser("$[]")
    ast = parser.parse()
    evaluator = Evaluator()
    result = evaluator.evaluate(ast)
    assert result == {}
    
    # Словарь с вложенными значениями
    parser = Parser('$[arr: list(1, 2), nested: $[a: 1]]')
    ast = parser.parse()
    evaluator = Evaluator()
    result = evaluator.evaluate(ast)
    assert result == {"arr": [1, 2], "nested": {"a": 1}}
