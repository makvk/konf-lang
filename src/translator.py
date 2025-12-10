import tomli_w
from typing import Any

class TOMLTranslator:
    @staticmethod
    def to_toml(data: Any) -> str:
        """Преобразует Python-объект в строку TOML."""
        if isinstance(data, dict):
            return tomli_w.dumps(data)
        elif isinstance(data, (int, float, str, bool, list)):
            # Если на верхнем уровне не словарь, оборачиваем в ключ 'value'
            return tomli_w.dumps({'value': data})
        else:
            raise TypeError(f"Неподдерживаемый тип для TOML: {type(data)}")