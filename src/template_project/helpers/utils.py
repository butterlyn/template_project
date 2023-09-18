from typing import Any
from collections.abc import MutableMapping

def count_final_elements_in_dict(dictionary: dict) -> int:
    """count the number of final elements in a dictionary"""
    dictionary_final_elements_count: int = 0
    value: Any
    for value in dictionary.values():
        if isinstance(value, dict):
            dictionary_final_elements_count += count_final_elements_in_dict(value)
        else:
            dictionary_final_elements_count += 1
    return dictionary_final_elements_count


def _flatten_dict_gen(d, parent_key, sep):
    for key, value in d.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, MutableMapping):
            yield from flatten_dict(value, new_key, sep=sep).items()
        else:
            yield new_key, value


def flatten_dict(dictionary: MutableMapping, parent_key: str = '', sep: str = '.'):
    return dict(_flatten_dict_gen(dictionary, parent_key, sep))


def flatten_dict_deepest_pair(dictionary: dict, max_level: int | None = None) -> list[Tuple[Any, Any]]:
    result = []
    for key, value in dictionary.items():
        (
            result.extend(flatten_dict_deepest_pair(value, max_level - 1)) if isinstance(value, dict) and (max_level > 0 or max_level is None)
            else result.append(tuple(key) + tuple(value))
        )
    return result