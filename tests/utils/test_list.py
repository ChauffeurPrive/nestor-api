from unittest import TestCase

import nestor_api.utils.list as list_utils


class TestListUtil(TestCase):
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
