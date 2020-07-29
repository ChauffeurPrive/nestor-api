"""Dictionary utilities"""

import copy


def deep_merge(destination: dict, source: dict, concat_lists: bool = False) -> dict:
    """Recursively add all keys from `source` into `destination`.

    Example:
        >>> destination = {'a': 1, 'b': {'c': 3}}
        >>> source = {'a': 11, 'b': {'d': 44}, 'e': 55}
        >>> deep_merge(destination, source)
        {'a': 11, 'b': {'c': 3, 'd': 44}, 'e': 55}
    """

    def _deep_merge_rec(dest, src):
        for key in src:
            if isinstance(dest.get(key), dict) and isinstance(src[key], dict):
                dest[key] = _deep_merge_rec(dest[key], src[key])
            elif isinstance(dest.get(key), list) and isinstance(src[key], list) and concat_lists:
                dest[key].extend(src[key])
            else:
                dest[key] = src[key]
        return dest

    return _deep_merge_rec(copy.deepcopy(destination), source)
