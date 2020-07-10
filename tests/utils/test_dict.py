from unittest import TestCase

import nestor_api.utils.dict as dict_utils


class TestDictUtil(TestCase):
    def test_deep_merge_should_correctly_merge_nested_dicts(self):
        dict_a = {1: "1a", 2: {3: "3a", 4: "4a"}, 7: {8: "8a"}}
        dict_b = {2: {3: "3b", 5: "5b"}, 6: "6b", 9: {10: "10b"}}

        result = dict_utils.deep_merge(dict_a, dict_b)
        self.assertEqual(dict_a, {1: "1a", 2: {3: "3a", 4: "4a"}, 7: {8: "8a"}})
        self.assertEqual(dict_b, {2: {3: "3b", 5: "5b"}, 6: "6b", 9: {10: "10b"}})
        self.assertEqual(
            result,
            {1: "1a", 2: {3: "3b", 4: "4a", 5: "5b"}, 6: "6b", 7: {8: "8a"}, 9: {10: "10b"},},
        )
