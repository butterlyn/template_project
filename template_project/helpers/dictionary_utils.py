# standard library imports
from typing import (
    Any,
    Tuple,
    Iterable,
    Hashable,
    Union,
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
    parent_key: str = "",
    sep: str = ".",
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

    max_level_resolved: int | float = float("inf") if max_level is None else max_level

    # iterate through dictionary
    result: list[Tuple[Any, Any]] = []
    for key, value in dictionary.items():
        (
            result.extend(
                dictionary_deepest_key_value_pairs(dictionary=value, max_level=(max_level_resolved - 1))  # type: ignore  # unavoidable self-referencing type issues
            )  # go one level deeper
            if isinstance(value, dict)
            and (max_level_resolved > 0)  # if more levels to go or maximum level
            else result.append((key, value))  # otherwise, add key-value pair to result
        )
    return result


def sort_dict_by_values(dictionary: dict, reverse: bool = False) -> dict[Any, Iterable]:
    """Sort a dictionary by its values"""
    return dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=reverse))  # type: ignore  # sorted has very bespoke typehint requirements


# WIP, not working yet. The function is not recursive.
# def append_string_to_dict_values(
#     input_dictionary: dict[Hashable, Any],
#     string_to_append: str,
#     included_keys: Hashable | Iterable[Hashable] | None = None,
# ) -> dict:
#     """
#     Append a string to the end of string values in a dictionary (including multi-level dictionaries).
#     Will default to all string values found, but can optionally select one or a set of key filters.

#     Parameters
#     ----------
#     input_dictionary : dict[Hashable, Any]
#         The input dictionary to modify.
#     string_to_append : str
#         The string to append to the end of string values in the dictionary.
#     included_keys : Hashable | Iterable[Hashable] | None, optional
#         A key or iterable of keys to include. If specified, the string will only
#         be appended to values corresponding to these included keys. By default,
#         the string is appended to all string values in the dictionary.

#     Returns
#     -------
#     dict
#         A new dictionary with the same keys as the input dictionary, but with
#         string values appended with the specified string.

#     Notes
#     -----
#     This function recursively iterates through nested dictionaries to append
#     the string to all string values. If a key filter is specified, the function
#     will only append the string to values corresponding to the filtered keys.

#     Non-string values are skipped.

#     Examples
#     --------
#     >>> input_dict = {'a': 'hello', 'b': {'c': 'world', 'd': 'foo'}}
#     >>> output_dict = append_string_to_dict_values(input_dict, '!')
#     >>> print(output_dict)
#     {'a': 'hello!', 'b': {'c': 'world!', 'd': 'foo!'}}
#     """
#     output_dictionary: dict[Hashable, Any] = {}
#     key: Hashable
#     value: Any
#     for key, value in input_dictionary.items():
#         if not isinstance(value, str):  # only append to strings, otherwise skip
#             output_dictionary[key] = value
#         elif isinstance(value, dict):  # recursively call this function if the value is a dictionary
#             output_dictionary[key] = append_string_to_dict_values(
#                 input_dictionary=value,
#                 included_keys=included_keys,
#                 string_to_append=string_to_append
#             )
#         elif any(  # append string if the key is in the keys_filter or keys_filter is not specified
#             (
#                 included_keys is None,
#                 not isinstance(included_keys, Iterable) and key == included_keys,
#                 isinstance(included_keys, Iterable) and key in included_keys,
#             )
#         ):
#             output_dictionary[key] = value + string_to_append
#         else:  # otherwise, just copy the value without appending the string
#             output_dictionary[key] = value

#     return output_dictionary


# Demonstration
if __name__ == "__main__":
    # nested dict for example
    nested_dict: dict[str, Union[dict, int]] = {
        "a": {
            "b": {
                "c": 66,
                "d": 22,
            },
            "e": 33,
        },
        "f": 88,
    }

    nested_dict_string: dict[str, Union[dict, str]] = {
        "a": {
            "b": {
                "c": "hello",
                "d": "world",
            },
            "e": "foo",
        },
        "f": "bar",
    }

    print("Example of a nested dictionary")
    print(nested_dict)
    print()
    print(
        f"Nested dictionary has {count_final_values_in_dict(nested_dict)} final values"
    )
    print()
    print("Flattened dictionary with higher-level keys concatenated with '.'")
    print(flatten_dict(nested_dict))
    print()
    print("Then sorting by values")
    print(sort_dict_by_values(flatten_dict(nested_dict)))
    print()
    print("Deepest key-value pairs of nested dictionary")
    print(dictionary_deepest_key_value_pairs(nested_dict))
    print()
    # WIP
    # print("Appending string to all string values in nested dictionary")
    # print(append_string_to_dict_values(nested_dict_string, '!', ['a', 'b', 'c', 'f']))
    # print()
