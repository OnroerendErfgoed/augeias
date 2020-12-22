"""
This module provides utilities for working with :term:`URIS <URI>`.
"""


from abc import ABCMeta, abstractmethod


class UriGenerator:
    """
    An abstract class for generating URIs.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def generate_collection_uri(self, collection):
        """
        Generate a :term:`URI` for a collection based on parameters passed.
        """

    @abstractmethod
    def generate_container_uri(self, collection, container):
        """
        Generate a :term:`URI` for a container based on parameters passed.
        """

    @abstractmethod
    def generate_object_uri(self, collection, container, object):
        """
        Generate a :term:`URI` for a object based on parameters passed.
        """


class UriPatternGenerator(UriGenerator):
    """
    Generate a :term:`URI` based on a simple pattern.
    """

    def __init__(self, pattern, separator='/'):
        self.pattern = pattern
        self.sep = separator

    def generate_collection_uri(self, collection):
        """
        Generate a :term:`URI` for a collection based on parameters passed.

        :param collection: The collection.
        :rtype: string
        """
        return self.pattern + collection

    def generate_container_uri(self, collection, container):
        """
        Generate a :term:`URI` for collection and container based on parameters passed.

        :param collection: The collection.
        :param container: The container.
        :rtype: string
        """
        return self.pattern + f'{collection}{self.sep}{container}'

    def generate_object_uri(self, collection, container, object):
        """
        Generate a :term:`URI` for collections, container and object based on parameters passed.

        :param collection: The collection.
        :param container: The container.
        :param object: The object.
        :rtype: string
        """
        return self.pattern + f'{collection}{self.sep}{container}{self.sep}{object}'


class DefaultUriGenerator(UriGenerator):
    """
    Generate a `URI` specific to storageprovider.

    Used for providers that do not implement a specific :class:`UriGenerator`.
    """

    def __init__(self, pattern='https://storage.onroerenderfgoed.be/'):
        self.pattern = pattern

    def generate_collection_uri(self, collection):
        """
        Generate a :term:`URI` for collections based on parameters passed.

        :param collection: The collection.
        :rtype: string
        """
        return self.pattern + f'collections/{collection}'

    def generate_container_uri(self, collection, container):
        """
        Generate a :term:`URI` for collection and container based on parameters passed.

        :param collection: The collection.
        :param container: The container.
        :rtype: string
        """
        return self.pattern + f'collections/{collection}/containers/{container}'

    def generate_object_uri(self, collection, container, object):
        """
        Generate a :term:`URI` for collections, container and object based on parameters passed.

        :param collection: The collection.
        :param container: The container.
        :param object: The object.
        :rtype: string
        """
        return self.pattern + f'collections/{collection}/containers/{container}/{object}'
