import unittest

from augeias.collections import Collection
from augeias.uri import DefaultUriGenerator
from augeias.uri import UriPatternGenerator


class TestUriPatternGenerator(unittest.TestCase):

    def test_uripatterngenrator_uri(self):
        uri_generator = UriPatternGenerator('https://things.erfgoed.net/')
        self.assertEqual('https://things.erfgoed.net/horses',
                         uri_generator.generate_collection_uri('horses'))
        self.assertEqual('https://things.erfgoed.net/horses/pegasus',
                         uri_generator.generate_container_uri('horses', 'pegasus'))
        self.assertEqual('https://things.erfgoed.net/horses/pegasus',
                         uri_generator.generate_container_uri('horses', 'pegasus'))
        self.assertEqual('https://things.erfgoed.net/horses/pegasus/1965',
                         uri_generator.generate_object_uri('horses', 'pegasus', '1965'))
        test_collection = Collection(name='TEST_COLLECTION', object_store='test',
                                     uri_generator=UriPatternGenerator('https://things.erfgoed.net/'))
        self.assertEqual('https://things.erfgoed.net/horses',
                         test_collection.uri_generator.generate_collection_uri('horses'))

    def test_uripatterngenrator_urn(self):
        uri_generator = UriPatternGenerator('urn:things-erfgoed:', ':')
        self.assertEqual('urn:things-erfgoed:horses',
                         uri_generator.generate_collection_uri('horses'))
        self.assertEqual('urn:things-erfgoed:horses:pegasus',
                         uri_generator.generate_container_uri('horses', 'pegasus'))
        self.assertEqual('urn:things-erfgoed:horses:pegasus',
                         uri_generator.generate_container_uri('horses', 'pegasus'))
        self.assertEqual('urn:things-erfgoed:horses:pegasus:1965',
                         uri_generator.generate_object_uri('horses', 'pegasus', '1965'))

    def test_defaultpatterngenrator_uri(self):
        uri_generator = DefaultUriGenerator()
        self.assertEqual('https://storage.onroerenderfgoed.be/collections/horses',
                         uri_generator.generate_collection_uri('horses'))
