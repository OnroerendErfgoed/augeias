import unittest

from augeias.stores.error import NotFoundException


class TestErrors(unittest.TestCase):
    def test_notfound_error(self):
        error = NotFoundException()
        self.assertIsNotNone(error)
        self.assertEqual(
            "Nothing matching the key value was found in the store", error.value
        )

    def test_notfound_error_str(self):
        error = NotFoundException()
        self.assertIn(
            "Nothing matching the key value was found in the store", str(error)
        )

    def test_notfound_error_custom_message(self):
        error = NotFoundException("Custom error message")
        self.assertEqual("Custom error message", error.value)
        self.assertIn("Custom error message", str(error))
