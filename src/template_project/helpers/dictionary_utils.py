# standard library imports
from typing import (
    Any,
    Tuple,
    Iterable,
)


def count_final_values_in_dict(dictionary: dict) -> int:
    """Count the number of final elements in a dictionary"""
    dictionary_final_elements_count: int = 0
    value: Any
    for value in dictionary.values():
        if isinstance(value, dict):
            dictionary_final_elements_count += count_final_values_in_dict(value)
        else:
            dictionary_final_elements_count += 1
    return dictionary_final_elements_count


def flatten_dict(
    dictionary: dict,
    parent_key: str = '',
    sep: str = '.',
) -> dict[str, Any]:
    """Flatten a nested dictionary to a dictionary one level deep, concatenating the original keys with a separator."""
    items: list[tuple[str, Any]] = []
    key: str
    value: Any
    for key, value in dictionary.items():
        new_key: str = parent_key + sep + key if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def dictionary_deepest_key_value_pairs(
    dictionary: dict,
    max_level: int | None = None,
) -> list[Tuple[Any, Any]]:
    """Return the list of the deepest key-value pairs of a dictionary, discarding all higher-level keys."""
    # set max_level to infinity if not specified
    if max_level is None:
        max_level = float("inf")

    # iterate through dictionary
    result = []
    for key, value in dictionary.items():
        (
            result.extend(dictionary_deepest_key_value_pairs(value, (max_level - 1)))  # go one level deeper
            if isinstance(value, dict) and (max_level > 0)  # if more levels to go or maximum level
            else result.append((key, value))  # otherwise, add key-value pair to result
        )
    return result


def sort_dict_by_values(dictionary: dict, reverse: bool = False) -> dict[Any, Iterable]:
    """Sort a dictionary by its values"""
    return dict(
        sorted(
            dictionary.items(),
            key=lambda item: item[1]
        )
    )


# Demonstration
if __name__ == "__main__":
    # nested dict for example
    nested_dict: dict = {
        "a": {
            "b": {
                "c": 66,
                "d": 22,
            },
            "e": 33,
        },
        "f": 88,
    }

    print("Example of a nested dictionary")
    print(nested_dict)
    print()
    print(f"Nested dictionary has {count_final_values_in_dict(nested_dict)} final values")
    print()
    print("Flattened dictionary with higher-level keys concatenated with '.'")
    print(flatten_dict(nested_dict))
    print()
    print("Then sorting by values")
    print(sort_dict_by_values(flatten_dict(nested_dict)))
    print()
    print("Deepest key-value pairs of nested dictionary")
    print(dictionary_deepest_key_value_pairs(nested_dict))
