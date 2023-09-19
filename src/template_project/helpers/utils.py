# standard library imports
from typing import Any, Tuple
import logging
# local imports
from rich_logger import getRichLogger

getRichLogger(
    logging_level="DEBUG",
    traceback_show_locals=True,
    traceback_extra_lines=10,
    traceback_suppressed_modules=(),
)
logging.debug("Rich logger and rich traceback enabled")


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
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + sep + key if parent_key else key
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


# Demonstration
if __name__ == "__main__":
    # nested dict for example
    nested_dict: dict = {
        "a": {
            "b": {
                "c": 1,
                "d": 2,
            },
            "e": 3,
        },
        "f": 4,
    }

    print("Example of a nested dictionary")
    print(nested_dict)
    print()
    print(f"Nested dictionary has {count_final_values_in_dict(nested_dict)} final values")
    print()
    print("Flattened dictionary with higher-level keys concatenated with '.'")
    print(flatten_dict(nested_dict))
    print()
    print("Deepest key-value pairs of nested dictionary")
    print(dictionary_deepest_key_value_pairs(nested_dict))