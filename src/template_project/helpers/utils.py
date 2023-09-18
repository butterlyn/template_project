from typing import Any

def _count_final_elements_in_dict(dictionary: dict) -> int:
    """count the number of final elements in a dictionary"""
    dictionary_final_elements_count: int = 0
    value: Any
    for value in dictionary.values():
        if isinstance(value, dict):
            dictionary_final_elements_count += _count_final_elements_in_dict(value)
        else:
            dictionary_final_elements_count += 1
    return dictionary_final_elements_count