from pairtree import PairtreeStorageFactory, PartNotFoundException, ObjectNotFoundException
from augeias.stores.StoreInterface import IStore
from augeias.stores.error import NotFoundException


class PairTreeFileSystemStore(IStore):
    def __init__(self, store_dir, uri_base='urn:x-vioe:'):
        sf = PairtreeStorageFactory()
        self.store = sf.get_store(store_dir=store_dir, uri_base=uri_base)

    def _get_container(self, container_key):
        try:
            return self.store.get_object(container_key, False)
        except ObjectNotFoundException:
            raise NotFoundException

    def get_object(self, container_key, object_key):
        container = self._get_container(container_key)
        try:
            return container.get_bytestream(object_key)
        except PartNotFoundException:
            raise NotFoundException

    def create_object(self, container_key, object_key, object_data):
        container = self._get_container(container_key)
        container.add_bytestream(object_key, object_data)

    def update_object(self, container_key, object_key, object_data):
        container = self.store.get_object(container_key, False)
        container.add_bytestream(object_key, object_data)

    def list_object_keys_for_container(self, container_key):
        container = self._get_container(container_key)
        return container.list_parts()

    def delete_object(self, container_key, object_key):
        container = self._get_container(container_key)
        try:
            container.del_file(object_key)
        except PartNotFoundException:
            raise NotFoundException

    def create_container(self, container_key):
        self.store.get_object(container_key)

    def delete_container(self, container_key):
        try:
            self.store.delete_object(container_key)
        except ObjectNotFoundException:
            raise NotFoundException
