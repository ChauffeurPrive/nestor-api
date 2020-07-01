"""Dictionary utilities"""

import copy


def deep_merge(destination: dict, source: dict) -> dict:
    """Recursively add all keys from `source` into `destination`.

    Example:
        >>> destination = {'a': 1, 'b': {'c': 3}}
        >>> source = {'a': 11, 'b': {'d': 44}, 'e': 55}
        >>> deep_merge(destination, source)
        {'a': 11, 'b': {'c': 3, 'd': 44}, 'e': 55}
    """

    def _deep_merge_rec(dest, src):
        for key in src:
            # pylint: disable=bad-continuation
            if key in dest and isinstance(dest.get(key), dict) and isinstance(src[key], dict):
                dest[key] = _deep_merge_rec(dest[key], src[key])
            else:
                dest[key] = src[key]
        return dest

    return _deep_merge_rec(copy.deepcopy(destination), source)
