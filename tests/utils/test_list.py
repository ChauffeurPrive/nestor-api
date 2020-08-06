from unittest import TestCase

import nestor_api.utils.list as list_utils


class TestListUtil(TestCase):
    def test_compute_diff_when_both_empty(self):
        """Should return empty report."""
        list_1 = []
        list_2 = []

        result = list_utils.compute_diff(list_1, list_2)

        self.assertEqual(list_1, [])
        self.assertEqual(list_2, [])
        self.assertEqual(result, {"added": [], "modified": [], "removed": []})

    def test_compute_diff_when_first_empty(self):
        """Should consider all members of list_2 as "added" and sort them."""
        list_1 = []
        list_2 = [3, 2, 1]

        result = list_utils.compute_diff(list_1, list_2)

        self.assertEqual(list_1, [])
        self.assertEqual(list_2, [3, 2, 1])
        self.assertEqual(result, {"added": [1, 2, 3], "modified": [], "removed": []})

    def test_compute_diff_when_second_empty(self):
        """Should consider all members of list_1 as "removed" and sort them."""
        list_1 = [3, 2, 1]
        list_2 = []

        result = list_utils.compute_diff(list_1, list_2)

        self.assertEqual(list_1, [3, 2, 1])
        self.assertEqual(list_2, [])
        self.assertEqual(result, {"added": [], "modified": [], "removed": [1, 2, 3]})

    def test_compute_diff_with_additions_and_deletions(self):
        """Should correctly find the added and removed items."""
        list_1 = [1, 3, 5, 6]
        list_2 = [2, 3, 4, 6, 7]

        result = list_utils.compute_diff(list_1, list_2)

        self.assertEqual(list_1, [1, 3, 5, 6])
        self.assertEqual(list_2, [2, 3, 4, 6, 7])
        self.assertEqual(result, {"added": [2, 4, 7], "modified": [], "removed": [1, 5]})

    def test_compute_diff_with_custom_key(self):
        """Should correctly match the modified values."""
        list_1 = ["a", "b", "c"]
        list_2 = ["A", "B", "C"]
        key_getter = lambda x: x.lower()  # The keys will match but not the values

        result = list_utils.compute_diff(list_1, list_2, key=key_getter)

        self.assertEqual(list_1, ["a", "b", "c"])
        self.assertEqual(list_2, ["A", "B", "C"])
        self.assertEqual(
            result,
            {
                "added": [],
                "modified": [
                    {"old": "a", "new": "A"},
                    {"old": "b", "new": "B"},
                    {"old": "c", "new": "C"},
                ],
                "removed": [],
            },
        )

    def test_compute_diff_with_complex_values(self):
        """Should correctly use the provided comparator."""
        list_1 = [{"key": "a", "value": 1}, {"key": "b", "value": 1}, {"key": "c", "value": 1}]
        list_2 = [{"key": "b", "value": 1}, {"key": "c", "value": 2}, {"key": "d", "value": 2}]
        key_getter = lambda x: x["key"]
        comparator = (
            lambda v1, v2: None
            if v1["value"] == v2["value"]
            else {v1["key"]: {"old": v1["value"], "new": v2["value"]}}
        )

        result = list_utils.compute_diff(list_1, list_2, key=key_getter, comparator=comparator)

        self.assertEqual(
            result,
            {
                "added": [{"key": "d", "value": 2}],
                "modified": [{"c": {"old": 1, "new": 2}}],
                "removed": [{"key": "a", "value": 1}],
            },
        )

    def test_flatten(self):
        """Should correctly flatten the given list."""
        double_list = [[1, 2], [3, 4], [5, 6]]

        result = list_utils.flatten(double_list)

        self.assertEqual(result, [1, 2, 3, 4, 5, 6])

    def test_find_with_one_match(self):
        """Should correctly find the match."""
        items = [1, 3, 5, 6, 7]
        predicate = lambda n: n % 2 == 0

        result = list_utils.find(items, predicate)

        self.assertEqual(result, 6)

    def test_find_with_several_matches(self):
        """Should correctly find the first match."""
        items = [1, 3, 4, 5, 6, 7]
        predicate = lambda n: n % 2 == 0

        result = list_utils.find(items, predicate)

        self.assertEqual(result, 4)

    def test_find_with_no_matches(self):
        """Should return None."""
        items = [1, 3, 5, 7]
        predicate = lambda n: n % 2 == 0

        result = list_utils.find(items, predicate)

        self.assertIsNone(result)
