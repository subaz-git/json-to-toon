"""
TOON (Token Oriented Object Notation) Converter
Converts JSON data structures to TOON format.

TOON Format Rules:
  - Array of uniform objects:  key[N]{field1,field2,...}:
                                 val1,val2,...
                                 val1,val2,...
  - Nested object:             key{
                                 ...
                               }
  - Array of primitives:       key[N]: val1,val2,...
  - Scalar key-value:          key: value
"""

from typing import Any


def _get_uniform_fields(arr: list) -> list[str] | None:
    """Return ordered field list if every item is a dict sharing the same keys."""
    if not arr or not all(isinstance(item, dict) for item in arr):
        return None
    fields = list(arr[0].keys())
    if all(list(item.keys()) == fields for item in arr):
        return fields
    # Fallback: union of all keys (preserving first-seen order)
    seen: dict[str, None] = {}
    for item in arr:
        for k in item.keys():
            seen[k] = None
    return list(seen.keys())


def _convert(data: Any, indent: int = 0) -> list[str]:
    pad = "  " * indent
    lines: list[str] = []

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                fields = _get_uniform_fields(value)
                if fields:
                    # Array of objects → TOON table
                    lines.append(f"{pad}{key}[{len(value)}]{{{','.join(fields)}}}:")
                    for item in value:
                        row = ",".join(str(item.get(f, "")) for f in fields)
                        lines.append(f"{pad}  {row}")
                else:
                    # Array of primitives
                    items_str = ",".join(_scalar(v) for v in value)
                    lines.append(f"{pad}{key}[{len(value)}]: {items_str}")
            elif isinstance(value, dict):
                lines.append(f"{pad}{key}{{")
                lines.extend(_convert(value, indent + 1))
                lines.append(f"{pad}}}")
            else:
                lines.append(f"{pad}{key}: {_scalar(value)}")
    elif isinstance(data, list):
        fields = _get_uniform_fields(data)
        if fields:
            lines.append(f"[{len(data)}]{{{','.join(fields)}}}:")
            for item in data:
                row = ",".join(str(item.get(f, "")) for f in fields)
                lines.append(f"  {row}")
        else:
            for item in data:
                lines.extend(_convert(item, indent))
    else:
        lines.append(f"{pad}{_scalar(data)}")

    return lines


def _scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)


def json_to_toon(data: Any) -> str:
    return "\n".join(_convert(data))
