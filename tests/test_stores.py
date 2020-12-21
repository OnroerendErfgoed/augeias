import os
import unittest
from zipfile import ZipFile

import tempdir

from augeias.stores.CephStore import CephStore
from augeias.stores.PairTreeFileSystemStore import PairTreeFileSystemStore
from augeias.stores.PairTreeFileSystemStore import _is_allowed_data
from augeias.stores.PairTreeFileSystemStore import _validate_data
from augeias.stores.error import NotFoundException


class TestPairTreeStore(unittest.TestCase):
    """
    series of tests to check the implementation of the PairTreeFileSystemStore.
    Not really unittests, more integration tests
    """

    def setUp(self):
        self.temp = tempdir.TempDir()
        store_dir = os.path.join(os.path.abspath(self.temp.name), 'test_data')
        self.store = PairTreeFileSystemStore(store_dir)

    def tearDown(self):
        self.temp.dissolve()

    def test_usage_scenario(self):
        container_key = 'testing'
        object_key = 'metadata'
        self.store.create_container(container_key)
        self.store.create_object(container_key, object_key, b'some test data')
        object_list = self.store.list_object_keys_for_container(container_key)
        self.assertEqual(1, len(object_list))
        self.assertEqual(object_key, object_list[0])
        object_value = self.store.get_object(container_key, object_key)
        self.assertEqual(b'some test data', object_value)
        self.store.delete_object(container_key, object_key)
        object_list = self.store.list_object_keys_for_container(container_key)
        self.assertEqual(0, len(object_list))

    def test_usage_real_file(self):
        here = os.path.dirname(__file__)
        testdata = os.path.join(here, '../', 'fixtures/kasteel.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        filesize = len(bdata)
        container_key = 'testing'
        object_key = 'metadata'
        self.store.create_container(container_key)
        self.store.create_object(container_key, object_key, bdata)
        object_list = self.store.list_object_keys_for_container(container_key)
        self.assertEqual(1, len(object_list))
        self.assertEqual(object_key, object_list[0])
        object_value = self.store.get_object(container_key, object_key)
        self.assertEqual(filesize, len(object_value))
        self.assertEqual(bdata, object_value)
        self.store.delete_object(container_key, object_key)
        object_list = self.store.list_object_keys_for_container(container_key)
        self.assertEqual(0, len(object_list))

    def test_get_file_info(self):
        here = os.path.dirname(__file__)
        testdata = os.path.join(here, '../', 'fixtures/kasteel.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        container_key = 'testing'
        object_key = 'metadata'
        self.store.create_container(container_key)
        self.store.create_object(container_key, object_key, bdata)
        object_info = self.store.get_object_info(container_key, object_key)
        self.assertEqual(11370, object_info['size'])
        self.assertEqual('image/jpeg', object_info['mime'])
        self.assertIn('time_last_modification', object_info)

    def test_update_scenario(self):
        container_key = 'testing'
        object_key = 'metadata'
        self.store.create_container(container_key)
        self.store.create_object(container_key, object_key, b'some test data')
        object_value = self.store.get_object(container_key, object_key)
        self.assertEqual(b'some test data', object_value)
        self.store.update_object(container_key, object_key, b'updated data')
        object_value = self.store.get_object(container_key, object_key)
        self.assertEqual(b'updated data', object_value)

    def test_delete_nonexisting(self):
        container_key = 'testing'
        object_key = 'metadata'
        self.store.create_container(container_key)
        self.store.create_object(container_key, object_key, b'some test data')
        self.assertRaises(NotFoundException, self.store.delete_object, container_key, 'nogo')

    def test_add_object_to_nonexisting_container(self):
        error_raised = False
        self.store.create_container('x')
        try:
            self.store.create_object('xx', '253', b'some test data')
        except NotFoundException:
            error_raised = True
        self.assertTrue(error_raised)

    def test_get_container_data(self):
        container_key = 'container'
        self.store.create_container(container_key)
        self.store.create_object(container_key, 'object_key', b'file-data')

        zip_file = self.store.get_container_data(container_key)
        with ZipFile(zip_file) as zf:
            filenames = zf.namelist()
            self.assertEqual(1, len(filenames))
            self.assertIn('object_key', filenames)

        zip_file = self.store.get_container_data(
            container_key,
            translations={'object_key': 'filename.pdf'}
        )
        with ZipFile(zip_file) as zf:
            filenames = zf.namelist()
            self.assertEqual(1, len(filenames))
            self.assertIn('filename.pdf', filenames)

    def test_delete_container(self):
        self.store.create_container('x')
        self.store.delete_container('x')

    def test_delete_nonexisting_container(self):
        error_raised = False
        try:
            self.store.delete_container('x')
        except NotFoundException:
            error_raised = True
        self.assertTrue(error_raised)

    def test_is_allowed_data(self):
        self.assertFalse(_is_allowed_data('foo'))
        self.assertTrue(_is_allowed_data(b'data'))

    def test_validate_data(self):
        self.assertRaises(IOError, _validate_data, 'foo')


class TestCephStore(unittest.TestCase):
    """series of tests to check the implementation of the CephStore.
        Not really unittests, more integration tests"""

    def setUp(self):
        self.store = CephStore()

    def tearDown(self):
        pass

    def test_usage_scenario(self):
        container_key = 'testing'
        object_key = 'metadata'
        self.store.create_container(container_key)
        self.store.create_object(container_key, object_key, 'some test data')
        object_value = self.store.get_object(container_key, object_key)
        self.assertEqual(None, object_value)
        object_value = self.store.get_object_info(container_key, object_key)
        self.assertEqual(None, object_value)
        self.store.delete_object(container_key, object_key)
        object_list = self.store.list_object_keys_for_container(container_key)
        self.assertEqual(None, object_list)
        self.store.update_object(container_key, object_key, 'updated data')
        self.store.delete_container(container_key)
