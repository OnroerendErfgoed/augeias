import uuid
from pyramid.response import Response
from pyramid.httpexceptions import HTTPLengthRequired, HTTPBadRequest, HTTPNotFound
from pyramid.view import view_config
from augeias.stores.error import NotFoundException


@view_config(context=NotFoundException, renderer='json')
def failed_not_found(exc, request):
    request.response.status_int = 404
    return {'message': exc.value}


class AugeiasView(object):

    @staticmethod
    def _is_long(s):
        try:
            long(s)
            return True
        except ValueError:
            return False

    def __init__(self, request):
        self.request = request

    @view_config(route_name='home', renderer='json')
    def my_view(self):
        return {'project': 'augeias'}

    def _get_object_data(self):
        if 'Content-Length' not in self.request.headers or not self._is_long(self.request.headers['Content-Length']):
            raise HTTPLengthRequired
        content_length = long(self.request.headers['Content-Length'])
        object_data = self.request.body_file
        if content_length == 0:
            raise HTTPBadRequest('body is empty')
        return object_data

    @view_config(route_name='list_collections')
    def list_collections(self):
        res = Response(content_type='application/json', status=200)
        res.json_body = [c for c in self.request.registry.collections]
        return res

    @view_config(route_name='update_object')
    def update_object(self):
        '''update an object in the data store'''
        store = self.retrieve_object_store()
        container_key = self.request.matchdict['container_key']
        object_key = self.request.matchdict['object_key']
        object_data = self._get_object_data()
        store.update_object(container_key, object_key, object_data)
        res = Response(content_type='application/json', status=200)
        res.json_body = {'container_key': container_key, 'object_key': object_key}
        return res

    @view_config(route_name='delete_object')
    def delete_object(self):
        '''delete an object from the data store'''
        store = self.retrieve_object_store()
        container_key = self.request.matchdict['container_key']
        object_key = self.request.matchdict['object_key']
        store.delete_object(container_key, object_key)
        res = Response(content_type='application/json', status=200)
        res.json_body = {'container_key': container_key, 'object_key': object_key}
        return res

    @view_config(route_name='get_object')
    def get_object(self):
        '''retrieve an object from the data store'''
        store = self.retrieve_object_store()
        container_key = self.request.matchdict['container_key']
        object_key = self.request.matchdict['object_key']
        object_data = store.get_object(container_key, object_key)
        res = Response(content_type='application/octet-stream', status=200)
        res.body = object_data
        return res

    @view_config(route_name='list_object_keys_for_container')
    def list_object_keys_for_container(self):
        '''list all object keys for a container in the data store'''
        store = self.retrieve_object_store()
        container_key = self.request.matchdict['container_key']
        res = Response(content_type='application/json', status=200)
        res.json_body = store.list_object_keys_for_container(container_key)
        return res

    @view_config(route_name='create_container')
    def create_container(self):
        '''create a new container in the data store'''
        store = self.retrieve_object_store()
        container_key = self.request.matchdict['container_key']
        store.create_container(container_key)
        res = Response(content_type='application/json', status=200)
        res.json_body = {'container_key': container_key}
        return res

    @view_config(route_name='create_container_and_id')
    def create_container_and_id(self):
        '''create a new container in the data store and generate an id'''
        store = self.retrieve_object_store()
        container_key = str(uuid.uuid4())
        store.create_container(container_key)
        res = Response(content_type='application/json', status=201)
        res.json_body = {'container_key': container_key}
        return res

    @view_config(route_name='delete_container')
    def delete_container(self):
        '''delete a container in the data store'''
        store = self.retrieve_object_store()
        container_key = self.request.matchdict['container_key']
        store.delete_container(container_key)
        res = Response(content_type='application/json', status=200)
        res.json_body = {'container_key': container_key}
        return res

    def retrieve_object_store(self):
        collection_name = self.request.matchdict['collection_key']
        if collection_name in self.request.registry.collections:
            store = self.request.registry.collections[collection_name].object_store
        else:
            raise HTTPNotFound('collection not found')
        return store
