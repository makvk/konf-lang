#!/usr/bin/env python3
import sys
from src.parser import Parser
from src.evaluator import Evaluator
from src.translator import TOMLTranslator

def main():
    # Чтение из stdin
    input_text = sys.stdin.read()
    
    try:
        # Парсинг
        parser = Parser(input_text)
        program = parser.parse()
        
        # Вычисление
        evaluator = Evaluator()
        result = evaluator.evaluate(program)
        
        # Преобразование в TOML
        toml_output = TOMLTranslator.to_toml(result)
        
        # Вывод в stdout
        sys.stdout.write(toml_output)
        
    except SyntaxError as e:
        sys.stderr.write(f"Синтаксическая ошибка: {e}\n")
        sys.exit(1)
    except NameError as e:
        sys.stderr.write(f"Ошибка имени: {e}\n")
        sys.exit(1)
    except TypeError as e:
        sys.stderr.write(f"Ошибка типа: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Неизвестная ошибка: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()