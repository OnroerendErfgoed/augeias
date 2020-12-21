import unittest

from augeias.stores.error import NotFoundException


class TestErrors(unittest.TestCase):
    def test_notfound_error(self):
        error = NotFoundException()
        self.assertIsNotNone(error)
        self.assertEqual(
            "Nothing matching the key value was found in the store", error.value
        )
