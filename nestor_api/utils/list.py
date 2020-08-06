"""List utilities."""

from typing import Any, Callable, Optional


def compute_diff(
    list_1: list,
    list_2: list,
    key=lambda x: x,
    comparator=lambda v1, v2: None if v1 == v2 else {"old": v1, "new": v2},
) -> dict:
    """Compute the differences between two lists. It assumes `list_1` is the previous state
    and `list_2` the new one when comparing."""
    diff: dict = {"added": [], "modified": [], "removed": []}

    list_1 = list_1.copy()
    list_2 = list_2.copy()
    list_1.sort(key=key)
    list_2.sort(key=key)

    idx_1 = 0
    idx_2 = 0
    while idx_1 < len(list_1) and idx_2 < len(list_2):
        key_1 = key(list_1[idx_1])
        key_2 = key(list_2[idx_2])
        if key_1 < key_2:
            diff["removed"].append(list_1[idx_1])
            idx_1 += 1
        elif key_1 > key_2:
            diff["added"].append(list_2[idx_2])
            idx_2 += 1
        else:
            comparison = comparator(list_1[idx_1], list_2[idx_2])
            if comparison is not None:
                diff["modified"].append(comparison)
            idx_1 += 1
            idx_2 += 1

    if idx_1 < len(list_1):
        diff["removed"].extend(list_1[idx_1:])

    if idx_2 < len(list_2):
        diff["added"].extend(list_2[idx_2:])

    return diff


def flatten(double_list: list) -> list:
    """Flatten a list of list into a simple list.

    Example:
       >>> flatten([[1, 2], [3, 4], [5, 6]])
       [1, 2, 3, 4, 5, 6]
    """
    return [item for sublist in double_list for item in sublist]


def find(items: list, predicate: Callable[[Any], bool]) -> Optional[Any]:
    """Find the first item in the list matching the predicate
    or returns `None` if no match is found."""
    return next((item for item in items if predicate(item)), None)
