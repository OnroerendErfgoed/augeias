"""
This module provide a simple filesystem based store
"""
import datetime
import os
from io import BytesIO
from zipfile import ZipFile

import magic
from pairtree import ObjectNotFoundException
from pairtree import PairtreeStorageFactory
from pairtree import PartNotFoundException
from pairtree import id2path

from augeias.stores.StoreInterface import IStore
from augeias.stores.error import NotFoundException


class PairTreeFileSystemStore(IStore):
    """
    Provides a filesystem based store.

    Will store your digital objects on disk using a PairTree.
    """

    def __init__(self, store_dir, uri_base='urn:x-vioe:'):
        sf = PairtreeStorageFactory()
        self.store = sf.get_store(store_dir=store_dir, uri_base=uri_base)

    def _get_container(self, container_key):
        try:
            return self.store.get_object(container_key, False)
        except ObjectNotFoundException:
            raise NotFoundException

    def get_object(self, container_key, object_key):
        """
        Retrieve an object from the data store.

        :param str container_key: Key of the container that the object lives in.
        :param str object_key: Key of the object to retrieve.
        :raises augeias.stores.error.NotFoundException: When the object or container could not be found.
        """
        container = self._get_container(container_key)
        try:
            return container.get_bytestream(object_key)
        except PartNotFoundException:
            raise NotFoundException

    def get_object_info(self, container_key, object_key):
        """
        Retrieve object info (mimetype, size, time last modification) from the data store.

        :param str container_key: Key of the container that the object lives in.
        :param str object_key: Key of the object to retrieve.
        :raises augeias.stores.error.NotFoundException: When the object or container could not be found.
        """
        # todo magic.from_buffer(open(file_path).read(1048576), mime=True) cannot microsoft mimetypes
        # https://stackoverflow.com/questions/17779560/django-python-magic-identify-ppt-docx-word-uploaded-file-as-application-zip
        file_path = '/'.join([self.store.store_dir,
                              'pairtree_root', id2path(container_key), object_key])
        if not os.path.exists(file_path):
            raise NotFoundException
        file_stat = os.stat(file_path)
        return {
            'time_last_modification': datetime.datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            'size': file_stat.st_size,
            'mime': magic.from_buffer(open(file_path, 'rb').read(1048576), mime=True) or 'application/octet-stream'
        }

    def create_object(self, container_key, object_key, object_data):
        """
        Save a new object in the data store

        :param str container_key: Key of the container to create an object in.
        :param str object_key: Key of the object to create.
        :param str object_data: The data for the object to create.
        :raises augeias.stores.error.NotFoundException: When the container could not be found.
        """
        _validate_data(object_data)
        container = self._get_container(container_key)
        container.add_bytestream(object_key, object_data)

    def update_object(self, container_key, object_key, object_data):
        """
        Update an object in the data store.

        :param str container_key: Key of the container that the object lives in.
        :param str object_key: Key of the object to update.
        :param str object_data: New data for the object.
        :raises augeias.stores.error.NotFoundException: When the object or container could not be found.
        """
        _validate_data(object_data)
        container = self.store.get_object(container_key, False)
        container.add_bytestream(object_key, object_data)

    def list_object_keys_for_container(self, container_key):
        """
        List all object keys for a container in the data store.

        :param str container_key: Key of the container to list the objects for.
        :returns: A list of container keys.
        :rtype: lst
        :raises augeias.stores.error.NotFoundException: When the container could not be found.
        """
        container = self._get_container(container_key)
        return container.list_parts()

    def delete_object(self, container_key, object_key):
        """
        Delete an object from the data store.

        :param str container_key: Key of the container that the object lives in.
        :param str object_key: Key of the object to delete.
        :raises augeias.stores.error.NotFoundException: When the object or container could not be found.
        """
        container = self._get_container(container_key)
        try:
            container.del_file(object_key)
        except PartNotFoundException:
            raise NotFoundException

    def get_container_data(self, container_key, translations=None):
        """
        Find a container and return a zip file of its contents.

        :param container_key: Key of the container which must be retrieved.
        :param translations: Dict of object IDs and file names to use for them.
        :return: a zip file containing all files of the container.
        """
        translations = translations or {}
        container = self.store.get_object(container_key,
                                          create_if_doesnt_exist=False)
        in_memory_file = BytesIO()
        with ZipFile(in_memory_file, 'w') as zf:
            for object_key in container.list_parts():
                zf.writestr(
                    translations.get(object_key, object_key),
                    container.get_bytestream(object_key)
                )
        in_memory_file.seek(0)
        return in_memory_file

    def create_container(self, container_key):
        """
        Create a new container in the data store.

        :param str container_key: Key of the container to create.
        """
        self.store.get_object(container_key)

    def delete_container(self, container_key):
        """
        Delete a container and all it's objects in the data store.

        :param str container_key: Key of the container to delete.
        :raises augeias.stores.error.NotFoundException: When the container could not be found.
        """
        try:
            self.store.delete_object(container_key)
        except ObjectNotFoundException:
            raise NotFoundException


def _is_allowed_data(data):  # pragma: no cover
    # not exhaustive.
    if isinstance(data, str):
        return False

    return True


def _validate_data(data):
    if not _is_allowed_data(data):
        raise OSError('Data type is not allowed')
