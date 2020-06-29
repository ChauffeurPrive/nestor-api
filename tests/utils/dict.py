# pylint: disable=missing-function-docstring disable=missing-module-docstring

import nestor_api.utils.dict as dict_utils


def test_deep_merge_should_correctly_merge_nested_dicts():
    dict_a = {1: "1a", 2: {3: "3a", 4: "4a"}}
    dict_b = {2: {3: "3b", 5: "5b"}, 6: "6b"}

    result = dict_utils.deep_merge(dict_a, dict_b)

    assert result == {1: "1a", 2: {3: "3b", 4: "4a", 5: "5b"}, 6: "6b"}
