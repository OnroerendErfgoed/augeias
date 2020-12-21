import ast
import json
import os
import re
import unittest
from io import BytesIO
from zipfile import ZipFile

import tempdir
from pyramid.paster import get_appsettings
from webtest import TestApp

from augeias import main
from augeias.collections import Collection
from augeias.stores.PairTreeFileSystemStore import PairTreeFileSystemStore

here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, 'conf_test.ini'))


def collections_include(config, store_dir):
    test_collection = Collection(
        name='TEST_COLLECTION', object_store=PairTreeFileSystemStore(store_dir))
    config.registry.collections[test_collection.name] = test_collection


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempdir.TempDir()
        self.store_dir = os.path.join(
            os.path.abspath(self.temp.name), 'test_data')
        self.app = main({}, **settings)
        self.storage_location = 'https://storage.onroerenderfgoed.be/'
        collections_include(self.app, self.store_dir)
        self.testapp = TestApp(self.app)

    def tearDown(self):
        self.temp.dissolve()

    def test_list_collections(self):
        res = self.testapp.get('/collections')
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertEqual(['TEST_COLLECTION'], res.json_body)

    def test_unexisting_collection(self):
        res = self.testapp.put(
            '/collections/NO_COLLECTION/containers/TEST_CONTAINER_ID', expect_errors=True)
        self.assertEqual('404 Not Found', res.status)

    def test_get_home(self):
        res = self.testapp.get('/')
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])

    def test_create_container(self):
        res = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIn('TEST_CONTAINER_ID', res.text)
        self.assertIn(
            self.storage_location
            + 'collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID',
            res.text
        )

    def test_add_object(self):
        # create a container
        cres = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', cres.status)

        testdata = os.path.join(here, '../', 'fixtures/kasteel.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        res = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300', bdata)
        self.assertEqual('200 OK', res.status)
        self.assertIn(self.storage_location + 'collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300',
                      res.text)
        self.assertIn('TEST_CONTAINER_ID', res.text)
        self.assertIn('200x300', res.text)

    def test_add_object_content_length_errors(self):
        # create a container
        cres = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', cres.status)

        testdata = os.path.join(here, '../', 'fixtures/kasteel.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        res = self.testapp.put('/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300', bdata,
                               headers={'Content-Length': ''},
                               expect_errors=True, status=411)
        self.assertEqual('411 Length Required', res.status)
        res = self.testapp.put('/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300', expect_errors=True,
                               status=400)
        self.assertEqual('400 Bad Request', res.status)

    def test_get_object(self):
        # create container and add object
        cres = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', cres.status)
        self.assertIn(self.storage_location + 'collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID',
                      cres.text)
        testdata = os.path.join(here, '../', 'fixtures/kasteel.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        file_size = len(bdata)
        ores = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300', bdata)
        self.assertIn(self.storage_location + 'collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300',
                      ores.text)
        self.assertEqual('200 OK', ores.status)

        res = self.testapp.get(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300')
        self.assertEqual('200 OK', res.status)
        self.assertEqual(file_size, len(res.body))
        self.assertEqual(bdata, res.body)

    def test_get_object_info(self):
        # create container and add object
        cres = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', cres.status)
        self.assertIn(self.storage_location + 'collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID',
                      cres.text)
        testdata = os.path.join(here, '../', 'fixtures/kasteel.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        ores = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300', bdata)
        self.assertIn(self.storage_location + 'collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300',
                      ores.text)
        self.assertEqual('200 OK', ores.status)

        res = self.testapp.get(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300/meta')
        self.assertEqual('200 OK', res.status)
        self.assertEqual(11370, res.json_body['size'])
        self.assertEqual('image/jpeg', res.json_body['mime'])
        self.assertIn('time_last_modification', res.json_body)

    def test_get_object_info_not_found(self):
        # create container and add object
        cres = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', cres.status)

        res = self.testapp.get('/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/not_found/meta',
                               expect_errors=True)
        self.assertEqual('404 Not Found', res.status)
        res2 = self.testapp.get('/collections/TEST_COLLECTION/containers/TEST_CONTAINER_NOT_FOUND/not_found/meta',
                                expect_errors=True)
        self.assertEqual('404 Not Found', res2.status)

    def test_list_object_keys_for_container(self):
        # create container and add objects
        cres = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', cres.status)
        testdata = os.path.join(here, '../', 'fixtures/kasteel.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        ores = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300', bdata)
        self.assertEqual('200 OK', ores.status)
        testdata = os.path.join(here, '../', 'fixtures/brug.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        ores = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/400x600', bdata)
        self.assertEqual('200 OK', ores.status)

        res = self.testapp.get(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', res.status)
        _list = ast.literal_eval(res.text)
        _list = [i.strip() for i in _list]
        self.assertTrue('200x300' in _list and '400x600' in _list)

    def test_download_container_zip(self):
        # create container and add objects
        cres = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', cres.status)
        testdata = os.path.join(here, '../', 'fixtures/kasteel.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        ores = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300', bdata)
        self.assertEqual('200 OK', ores.status)
        testdata = os.path.join(here, '../', 'fixtures/brug.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        ores = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/400x600', bdata)
        self.assertEqual('200 OK', ores.status)

        res = self.testapp.get('/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID',
                               headers={'Accept': 'application/zip'})
        self.assertEqual('200 OK', res.status)
        with ZipFile(BytesIO(res.body)) as zf:
            filenames = zf.namelist()
            self.assertEqual(2, len(filenames))
            self.assertIn('200x300', filenames)
            self.assertIn('400x600', filenames)

        res = self.testapp.get(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID?200x300=file1.pdf',
            headers={'Accept': 'application/zip'}
        )
        self.assertEqual('200 OK', res.status)
        with ZipFile(BytesIO(res.body)) as zf:
            filenames = zf.namelist()
            self.assertEqual(2, len(filenames))
            self.assertIn('file1.pdf', filenames)
            self.assertIn('400x600', filenames)

    def test_update_object(self):
        # create container and add object
        cres = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', cres.status)
        testdata = os.path.join(here, '../', 'fixtures/kasteel.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        ores = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300', bdata)
        self.assertEqual('200 OK', ores.status)
        self.assertIn(self.storage_location + 'collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300',
                      ores.text)

        testdata = os.path.join(here, '../', 'fixtures/brug.jpg')
        with open(testdata, 'rb') as f:
            ubdata = f.read()
        file_size = len(ubdata)
        res = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300', ubdata)
        self.assertEqual('200 OK', res.status)
        res = self.testapp.get(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300')
        self.assertEqual('200 OK', res.status)
        self.assertEqual(file_size, len(res.body))
        self.assertEqual(ubdata, res.body)
        self.assertNotEqual(bdata, res.body)

    def test_update_object_validation_failure(self):
        cres = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', cres.status)
        testdata = os.path.join(here, '../', 'fixtures/kasteel.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        res = self.testapp.put('/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/1', bdata,
                               expect_errors=True, status=400)
        self.assertDictEqual({'message': 'Failed validation: The object key must be 3 characters long'},
                             res.json_body)

    def test_copy_object(self):
        # create container and add object
        cres = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', cres.status)
        testdata = os.path.join(here, '../', 'fixtures/kasteel.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        ores = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300', bdata)
        self.assertEqual('200 OK', ores.status)
        self.assertIn(self.storage_location + 'collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300',
                      ores.text)
        cres2 = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID2')
        self.assertEqual('200 OK', cres2.status)
        json_data = json.dumps({
            'host_url': 'http://localhost',
            'collection_key': 'TEST_COLLECTION',
            'container_key': 'TEST_CONTAINER_ID',
            'object_key': '200x300'
        })
        ores2 = self.testapp.put('/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID2/kasteel',
                                 json_data, headers={'content-type': 'application/json'})

        self.assertEqual('200 OK', ores2.status)
        res2 = self.testapp.get(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID2/kasteel')
        self.assertEqual('200 OK', res2.status)
        self.assertEqual(bdata, res2.body)

    def test_copy_object_invalid_body(self):
        json_data = 'test'
        res = self.testapp.put('/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID2/kasteel',
                               json_data, headers={'content-type': 'application/json'}, expect_errors=True)
        self.assertEqual(res.status, '400 Bad Request')
        json_data = '{"path": "test"}'
        res3 = self.testapp.put('/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID2/kasteel',
                                json_data, headers={'content-type': 'application/json'}, expect_errors=True)
        self.assertEqual(res3.status, '400 Bad Request')
        json_data = json.dumps({
            'host_url': 'bad host url',
            'collection_key': 'TEST_COLLECTION',
            'container_key': 'TEST_CONTAINER_ID',
            'object_key': '200x300'
        })
        res4 = self.testapp.put('/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID2/kasteel',
                                json_data, headers={'content-type': 'application/json'}, expect_errors=True)
        self.assertEqual(res4.status, '400 Bad Request')

    def test_copy_object_invalid_body_not_found(self):
        json_data = json.dumps({
            'host_url': 'http://localhost',
            'collection_key': 'TEST_COLLECTION_INVALID',
            'container_key': 'TEST_CONTAINER_ID',
            'object_key': '200x300'
        })
        res = self.testapp.put('/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID2/kasteel',
                               json_data, headers={'content-type': 'application/json'}, expect_errors=True)
        self.assertEqual(res.status, '400 Bad Request')
        self.assertIn(
            'Collection TEST_COLLECTION_INVALID was not found', res.text)
        json_data = json.dumps({
            'host_url': 'http://localhost',
            'collection_key': 'TEST_COLLECTION',
            'container_key': 'TEST_CONTAINER_ID',
            'object_key': '200'
        })
        res2 = self.testapp.put('/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID2/kasteel',
                                json_data, headers={'content-type': 'application/json'}, expect_errors=True)
        self.assertEqual(res2.status, '400 Bad Request')
        self.assertIn(
            'Container - object (TEST_CONTAINER_ID - 200) combination was not found in Collection TEST_COLLECTION',
            res2.text
        )

    def test_delete_object(self):
        # create container and add object
        cres = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', cres.status)
        testdata = os.path.join(here, '../', 'fixtures/kasteel.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        ores = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300', bdata)
        self.assertEqual('200 OK', ores.status)

        res = self.testapp.delete(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300')
        self.assertIn(self.storage_location + 'collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300',
                      res.json_body['uri'])
        self.assertEqual('200 OK', res.status)
        self.assertIn('TEST_CONTAINER_ID', res.text)
        self.assertIn('200x300', res.text)

        res = self.testapp.get('/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/200x300', status=404,
                               expect_errors=True)
        self.assertEqual('404 Not Found', res.status)

    def test_delete_non_existing_object(self):
        cres = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', cres.status)
        res = self.testapp.delete('/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID/2000x30000',
                                  expect_errors=True)
        self.assertEqual('404 Not Found', res.status)

    def test_delete_container(self):
        # create container
        cres = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', cres.status)

        res = self.testapp.delete(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', res.status)

    def test_create_container_with_id(self):
        res = self.testapp.post('/collections/TEST_COLLECTION/containers')
        self.assertEqual('201 Created', res.status)
        uuid4hex = re.compile(
            r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z', re.I)
        container_key = res.json_body['container_key']
        self.assertTrue(uuid4hex.match(container_key))
        print(res.json_body['uri'])

    def test_create_object_with_id(self):
        cres = self.testapp.put(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID')
        self.assertEqual('200 OK', cres.status)
        testdata = os.path.join(here, '../', 'fixtures/kasteel.jpg')
        with open(testdata, 'rb') as f:
            bdata = f.read()
        res = self.testapp.post(
            '/collections/TEST_COLLECTION/containers/TEST_CONTAINER_ID', bdata)
        self.assertEqual('201 Created', res.status)
        uuid4hex = re.compile(
            r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z', re.I)
        object_key = res.json_body['object_key']
        self.assertTrue(uuid4hex.match(object_key))
        print(res.json_body['uri'])
