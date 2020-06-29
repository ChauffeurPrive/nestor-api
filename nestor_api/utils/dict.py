"""Dictionary utilities"""


def deep_merge(destination: dict, source: dict) -> dict:
    """Recursively add all keys from `source` into `destination`.

    Note that this will mutate `destination`. If you want to keep its value intact, do:
        deep_merge(dict(destination), source)

    Example:
        >>> destination = {'a': 1, 'b': {'c': 3}}
        >>> source = {'a': 11, 'b': {'d': 44}, 'e': 55}
        >>> deep_merge(destination, source)
        {'a': 11, 'b': {'c': 3, 'd': 44}, 'e': 55}
    """
    for key in source:
        # pylint: disable=bad-continuation
        if (
            key in destination
            and isinstance(destination[key], dict)
            and isinstance(source[key], dict)
        ):
            deep_merge(destination[key], source[key])
        else:
            destination[key] = source[key]

    return destination
