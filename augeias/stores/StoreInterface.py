'''
This interface handles object-storage.
Implementations of this interface can be made for different object-storages
Currently this interface is only implemented for PairTreeFileSystemStore
'''

from abc import ABCMeta, abstractmethod

class IStore:
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_object(self, container_key, object_key, object_data):
        '''save a new object in the data store'''

    @abstractmethod
    def delete_object(self, container_key, object_key):
        '''delete an object from the data store'''

    @abstractmethod
    def get_object(self, container_key, object_key):
        '''retrieve an object from the data store'''

    @abstractmethod
    def update_object(self, container_key, object_key, object_data):
        '''update an object in the data store'''

    @abstractmethod
    def list_object_keys_for_container(self, container_key):
        '''list all object keys for a container in the data store'''

    @abstractmethod
    def create_container(self, container_key):
        '''create a new container in the data store'''

    @abstractmethod
    def delete_container(self, container_key):
        '''delete a container in the data store'''
