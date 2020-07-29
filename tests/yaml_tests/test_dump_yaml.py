from unittest import TestCase

import yaml_lib


class TestDumpYaml(TestCase):
    def test_convert_to_yaml(self):
        dictionary_to_convert = {
            "name": "John Doe",
            "contact": {"phone": 1234567890, "mail": "john@doe.com"},
            "items": ["items1", "items2"],
        }

        yaml = yaml_lib.convert_to_yaml(dictionary_to_convert)

        self.assertEqual(
            yaml,
            "contact:\n  mail: john@doe.com\n  phone: 1234567890\nitems:\n- "
            "items1\n- items2\nname: John Doe\n",
        )
