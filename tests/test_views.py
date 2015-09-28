import unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # pragma: no cover
from pyramid import testing
from augeias.views import AugeiasView


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = Mock()
        self.request.registry.object_store = Mock()
        self.view = AugeiasView(self.request)

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        info = self.view.my_view()
        self.assertEqual(info['project'], 'augeias')
