"""SQM config-format serializer.

ARMA 3 mission.sqm uses a proprietary config format:
- Tab indentation
- Semicolons after every value and closing brace
- Arrays: key[]={v1,v2,v3};
- Strings: key="value";
- Numbers: key=123; or key=1.5;
- Classes: class Name { ... };
"""

from io import StringIO
from typing import Any


class SQMWriter:
    """Writes ARMA 3 SQM config format."""

    def __init__(self):
        self._buf = StringIO()
        self._indent = 0

    def _write_line(self, line: str) -> None:
        prefix = "\t" * self._indent
        self._buf.write(f"{prefix}{line}\n")

    def write_value(self, key: str, value: Any) -> None:
        if isinstance(value, bool):
            self._write_line(f"{key}={1 if value else 0};")
        elif isinstance(value, int):
            self._write_line(f"{key}={value};")
        elif isinstance(value, float):
            self._write_line(f"{key}={_format_float(value)};")
        elif isinstance(value, str):
            safe = _sanitize_sqm_string(value)
            self._write_line(f'{key}="{safe}";')
        else:
            self._write_line(f"{key}={value};")

    def write_array(self, key: str, values: list) -> None:
        if not values:
            self._write_line(f"{key}[]={{}};")
            return
        formatted = ",".join(_format_array_item(v) for v in values)
        self._write_line(f"{key}[]={{{formatted}}};")

    def begin_class(self, name: str) -> None:
        self._write_line(f"class {name}")
        self._write_line("{")
        self._indent += 1

    def end_class(self) -> None:
        self._indent -= 1
        self._write_line("};")

    def write_raw(self, line: str) -> None:
        self._write_line(line)

    def get_output(self) -> str:
        return self._buf.getvalue()


def _sanitize_sqm_string(value: str) -> str:
    """Sanitize string for SQM - replace Polish chars and escape quotes."""
    # Polish char replacements for SQM safety
    _PL_MAP = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
        'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
        'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z',
    }
    for pl, ascii_char in _PL_MAP.items():
        value = value.replace(pl, ascii_char)
    # Escape double quotes
    value = value.replace('"', "'")
    return value


def _format_float(value: float) -> str:
    """Format float for SQM - round to 1 decimal for coordinates, clean output."""
    # Round to avoid Python float precision artifacts (0.29999999999 -> 0.3)
    value = round(value, 4)
    if value == int(value):
        return str(int(value))
    result = f"{value:.4f}".rstrip("0")
    if result.endswith("."):
        result += "0"
    return result


def _format_array_item(value: Any) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return "1" if value else "0"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return _format_float(value)
    return str(value)
