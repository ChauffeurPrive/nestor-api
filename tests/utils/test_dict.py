from unittest import TestCase

import nestor_api.utils.dict as dict_utils


class TestDictUtil(TestCase):
    def test_deep_merge_should_correctly_merge_nested_dicts(self):
        """Should correctly deep merge 2 dictionaries."""
        dict_a = {1: "1a", 2: {3: "3a", 4: "4a"}, 7: {8: "8a"}}
        dict_b = {2: {3: "3b", 5: "5b"}, 6: "6b", 9: {10: "10b"}}

        result = dict_utils.deep_merge(dict_a, dict_b)

        self.assertEqual(dict_a, {1: "1a", 2: {3: "3a", 4: "4a"}, 7: {8: "8a"}})
        self.assertEqual(dict_b, {2: {3: "3b", 5: "5b"}, 6: "6b", 9: {10: "10b"}})
        self.assertEqual(
            result, {1: "1a", 2: {3: "3b", 4: "4a", 5: "5b"}, 6: "6b", 7: {8: "8a"}, 9: {10: "10b"}}
        )

    def test_should_concat_lists_if_specified(self):
        """Should concat the new list at the end of the original one."""
        dict_a = {1: "1a", 2: {3: ["a", "b"]}}
        dict_b = {1: "1b", 2: {3: ["c", "d"]}}

        result = dict_utils.deep_merge(dict_a, dict_b, concat_lists=True)

        self.assertEqual(dict_a, {1: "1a", 2: {3: ["a", "b"]}})
        self.assertEqual(dict_b, {1: "1b", 2: {3: ["c", "d"]}})
        self.assertEqual(result, {1: "1b", 2: {3: ["a", "b", "c", "d"]}})

    def test_should_not_concat_lists_by_default(self):
        """Should replace a list value by the new value."""
        dict_a = {1: "1a", 2: {3: ["a", "b"]}}
        dict_b = {1: "1b", 2: {3: ["c", "d"]}}

        result = dict_utils.deep_merge(dict_a, dict_b)

        self.assertEqual(dict_a, {1: "1a", 2: {3: ["a", "b"]}})
        self.assertEqual(dict_b, {1: "1b", 2: {3: ["c", "d"]}})
        self.assertEqual(result, {1: "1b", 2: {3: ["c", "d"]}})
