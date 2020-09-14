from unittest import TestCase
from util import JSONFile
from json.decoder import JSONDecodeError


class TestJSONFile(TestCase):
    def test_get_value(self) -> None:
        json = JSONFile(file_content='{"value":42}')
        self.assertEqual(json.get("value", 0), 42)

    def test_get_default(self) -> None:
        json = JSONFile(file_content='{"value":42}')
        self.assertEqual(json.get("does_not_exist", 1337), 1337)

    def test_fail(self) -> None:
        json = JSONFile(file_content='{"value":42}')
        with self.assertRaises(ValueError):
            json.get("does_not_exist", 13, fail=True)

    def test_nontrivial_path(self) -> None:
        json = JSONFile(file_content='{"more":{"depth":{"value": 7}}}')
        self.assertEqual(
            json.get("more.depth.value", 0),
            7
        )

    def test_invalid_json(self) -> None:
        with self.assertRaises(JSONDecodeError):
            JSONFile(file_content='{value: 42}')
