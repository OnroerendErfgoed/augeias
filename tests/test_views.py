import unittest
from unittest.mock import Mock

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

    def test_get_container_data(self):
        collection = Mock()
        collection.object_store.get_container_data.return_value = Mock(
            read=Mock(return_value=b'zip-file')
        )
        self.request.registry.collections = {'collection': collection}
        self.request.matchdict = {
            'container_key': 'container',
            'collection_key': 'collection'
        }
        response = self.view.get_container_data()
        self.assertEqual(b'zip-file', response.body)

    def test_get_container_data_translations(self):
        collection = Mock()
        collection.object_store.get_container_data.return_value = Mock(
            read=Mock(return_value=b'zip-file')
        )
        self.request.GET = {
            '001': 'name1.pdf',
            '002': 'name2.pdf',
        }
        self.request.registry.collections = {'collection': collection}
        self.request.matchdict = {
            'container_key': 'container',
            'collection_key': 'collection'
        }
        response = self.view.get_container_data()
        self.assertEqual(b'zip-file', response.body)
        args, kwargs = collection.object_store.get_container_data.call_args_list[0]
        self.assertEqual(args, ('container',))
        self.assertEqual(
            kwargs,
            {
                'translations': {
                    '001': 'name1.pdf',
                    '002': 'name2.pdf',
                }
            }
        )
