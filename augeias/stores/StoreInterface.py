"""
This module defines the interface every store needs to adhere to.
"""

from abc import ABCMeta, abstractmethod


class IStore:
    """
    This interface handles object-storage.
    Implementations of this interface can be made for different object-storages
    Currently this interface is only implemented for PairTreeFileSystemStore
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_object(self, container_key, object_key, object_data):
        """
        Save a new object in the data store

        :param str container_key: Key of the container to create an object in.
        :param str object_key: Key of the object to create.
        :param str object_data: The data for the object to create.
        :raises augeias.stores.error.NotFoundException: When the container could not be found.
        """

    @abstractmethod
    def delete_object(self, container_key, object_key):
        """
        Delete an object from the data store.

        :param str container_key: Key of the container that the object lives in.
        :param str object_key: Key of the object to delete.
        :raises augeias.stores.error.NotFoundException: When the object or container could not be found.
        """

    @abstractmethod
    def get_object(self, container_key, object_key):
        """
        Retrieve an object from the data store.

        :param str container_key: Key of the container that the object lives in.
        :param str object_key: Key of the object to retrieve.
        :raises augeias.stores.error.NotFoundException: When the object or container could not be found.
        """

    @abstractmethod
    def get_object_info(self, container_key, object_key):
        """
        Retrieve object info (mimetype, size, time last modification) from the data store.

        :param str container_key: Key of the container that the object lives in.
        :param str object_key: Key of the object to retrieve.
        :raises augeias.stores.error.NotFoundException: When the object or container could not be found.
        """

    @abstractmethod
    def update_object(self, container_key, object_key, object_data):
        """
        Update an object in the data store.

        :param str container_key: Key of the container that the object lives in.
        :param str object_key: Key of the object to update.
        :param str object_data: New data for the object.
        :raises augeias.stores.error.NotFoundException: When the object or container could not be found.
        """

    @abstractmethod
    def list_object_keys_for_container(self, container_key):
        """
        List all object keys for a container in the data store.

        :param str container_key: Key of the container to list the objects for.
        :returns: A list of container keys.
        :rtype: lst
        :raises augeias.stores.error.NotFoundException: When the container could not be found.
        """

    @abstractmethod
    def get_container_data(self, container_key, translations=None):
        """
        Find a container and return a zip file of its contents.

        :param container_key: Key of the container which must be retrieved.
        :param translations: Dict of object IDs and file names to use for them.
        :return: a zip file containing all files of the container.
        """

    @abstractmethod
    def create_container(self, container_key):
        """
        Create a new container in the data store.

        :param str container_key: Key of the container to create.
        """

    @abstractmethod
    def delete_container(self, container_key):
        """
        Delete a container and all it's objects in the data store.

        :param str container_key: Key of the container to delete.
        :raises augeias.stores.error.NotFoundException: When the container could not be found.
        """
