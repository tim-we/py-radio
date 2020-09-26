from unittest import TestCase
from util import JSONFile
from json.decoder import JSONDecodeError
from util import HourRange


class TestJSONFile(TestCase):
    def test_get_value(self) -> None:
        json = JSONFile(file_content='{"value":42}')
        self.assertEqual(json.get_or_default("value", 0, int), 42)

    def test_get_default(self) -> None:
        json = JSONFile(file_content='{"value":42}')
        self.assertEqual(
            json.get_or_default("does_not_exist", 1337, int),
            1337
        )

    def test_fail(self) -> None:
        json = JSONFile(file_content='{"value":42}')
        with self.assertRaises(ValueError):
            json.get_or_fail("does_not_exist", int)

    def test_wrong_type(self) -> None:
        json = JSONFile(file_content='{"value":"bubka"}')
        with self.assertRaises(TypeError):
            json.get_or_fail("value", float)

    def test_nontrivial_path(self) -> None:
        json = JSONFile(file_content='{"more":{"depth":{"value": 7}}}')
        self.assertEqual(
            json.get_or_default("more.depth.value", 0, int),
            7
        )

    def test_invalid_json(self) -> None:
        with self.assertRaises(JSONDecodeError):
            JSONFile(file_content='{value: 42}')


class TestTimeUtils(TestCase):
    def test_no_wrap_around(self) -> None:
        hr = HourRange(2, 15)
        self.assertTrue(hr.is_in(2))
        self.assertTrue(hr.is_in(4))
        self.assertTrue(hr.is_in(15))
        self.assertFalse(hr.is_in(1))
        self.assertFalse(hr.is_in(16))

    def test_wrap_around(self) -> None:
        hr = HourRange(23, 6)
        self.assertTrue(hr.is_in(23))
        self.assertTrue(hr.is_in(0))
        self.assertTrue(hr.is_in(2))
        self.assertTrue(hr.is_in(6))
        self.assertFalse(hr.is_in(22))
        self.assertFalse(hr.is_in(7))

    def test_error(self) -> None:
        hr = HourRange(0, 23)
        with self.assertRaises(ValueError):
            hr.is_in(24)
