"""List utilities."""

from typing import Any, Callable, Optional


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
