from typing import Any


def _replace_an_item_in_list(
    list_: list[Any],
    new_item: Any,
    item_index: int,
) -> list[str]:
    """Replaces an item in a list with a new item for a given index."""
    list_.pop(item_index)
    list_.insert(item_index, new_item)
    return list_
