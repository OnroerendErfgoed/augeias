from augeias.stores.StoreInterface import IStore


class CephStore(IStore):

    def __init__(self):
        pass

    def get_object(self, container_key, object_key):
        pass

    def get_object_info(self, container_key, object_key):
        pass

    def create_object(self, container_key, object_key, object_data):
        pass

    def list_object_keys_for_container(self, container_key):
        pass

    def delete_object(self, container_key, object_key):
        pass

    def update_object(self, container_key, object_key, object_data):
        pass

    def get_container_data(self, container_key, translations=None):
        pass

    def create_container(self, container_key):
        pass

    def delete_container(self, container_key):
        pass
