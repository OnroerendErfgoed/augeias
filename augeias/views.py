import uuid

from pyramid.response import Response
from pyramid.httpexceptions import HTTPLengthRequired, HTTPBadRequest, HTTPNotFound
from pyramid.view import view_config
import urllib

from augeias.stores.error import NotFoundException
import re


@view_config(context=NotFoundException, renderer='json')
def failed_not_found(exc, request):
    request.response.status_int = 404
    return {'message': exc.value}


class ValidationFailure(Exception):
    def __init__(self, msg):
        self.msg = msg


@view_config(context=ValidationFailure, renderer='json')
def failed_validation(exc, request):
    request.response.status_int = 400
    return {'message': 'Failed validation: %s' % exc.msg}


class AugeiasView(object):

    def __init__(self, request):
        self.request = request

    @view_config(route_name='home', renderer='json')
    def my_view(self):
        return {'project': 'augeias'}

    @view_config(route_name='list_collections', permission='view')
    def list_collections(self):
        res = Response(content_type='application/json', status=200)
        res.json_body = [c for c in self.request.registry.collections]
        return res

    @view_config(route_name='update_object', permission='edit')
    def update_object(self):
        '''update an object in the data store'''
        object_data = _get_object_data(self.request)
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict['container_key']
        object_key = self.request.matchdict['object_key']
        if len(object_key) < 3:
            raise ValidationFailure('The object key must be 3 characters long')
        collection.object_store.update_object(container_key, object_key, object_data)
        res = Response(content_type='application/json', status=200)
        res.json_body = {
            'container_key': container_key,
            'object_key': object_key,
            'uri': collection.uri_generator.generate_object_uri(
                collection=collection.name,
                container=container_key,
                object=object_key)
        }
        return res

    @view_config(route_name='create_object_and_id', permission='edit')
    def create_object_and_id(self):
        '''create an object in the data store and generate an id'''
        object_data = _get_object_data(self.request)
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict['container_key']
        object_key = str(uuid.uuid4())
        collection.object_store.update_object(container_key, object_key, object_data)
        res = Response(content_type='application/json', status=201)
        res.json_body = {
            'container_key': container_key,
            'object_key': object_key,
            'uri': collection.uri_generator.generate_object_uri(
                collection=collection.name,
                container=container_key,
                object=object_key)
        }
        return res

    @view_config(route_name='delete_object', permission='edit')
    def delete_object(self):
        '''delete an object from the data store'''
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict['container_key']
        object_key = self.request.matchdict['object_key']
        collection.object_store.delete_object(container_key, object_key)
        res = Response(content_type='application/json', status=200)
        res.json_body = {
            'container_key': container_key,
            'object_key': object_key,
            'uri': collection.uri_generator.generate_object_uri(
                collection=collection.name,
                container=container_key,
                object=object_key)
        }
        return res

    @view_config(route_name='get_object', permission='view')
    def get_object(self):
        '''retrieve an object from the data store'''
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict['container_key']
        object_key = self.request.matchdict['object_key']
        object_data = collection.object_store.get_object(container_key, object_key)
        res = Response(content_type='application/octet-stream', status=200)
        res.body = object_data
        return res

    @view_config(route_name='list_object_keys_for_container', permission='view')
    def list_object_keys_for_container(self):
        '''list all object keys for a container in the data store'''
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict['container_key']
        res = Response(content_type='application/json', status=200)
        res.json_body = collection.object_store.list_object_keys_for_container(container_key)
        return res

    @view_config(route_name='create_container', permission='edit')
    def create_container(self):
        '''create a new container in the data store'''
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict['container_key']
        collection.object_store.create_container(container_key)
        res = Response(content_type='application/json', status=200)
        res.json_body = {
            'container_key': container_key,
            'uri': collection.uri_generator.generate_container_uri(
                collection=collection.name,
                container=container_key)
        }
        return res

    @view_config(route_name='create_container_and_id', permission='edit')
    def create_container_and_id(self):
        '''create a new container in the data store and generate an id'''
        collection = _retrieve_collection(self.request)
        container_key = str(uuid.uuid4())
        collection.object_store.create_container(container_key)
        res = Response(content_type='application/json', status=201)
        res.json_body = {
            'container_key': container_key,
            'uri': collection.uri_generator.generate_container_uri(
                collection=collection.name,
                container=container_key)
        }
        return res

    @view_config(route_name='delete_container', permission='edit')
    def delete_container(self):
        '''delete a container in the data store'''
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict['container_key']
        collection.object_store.delete_container(container_key)
        res = Response(content_type='application/json', status=200)
        res.json_body = {
            'container_key': container_key,
            'uri': collection.uri_generator.generate_container_uri(
                collection=collection.name,
                container=container_key)
        }
        return res


# HELPERS


def _is_long(s):
    try:
        long(s)
        return True
    except ValueError:
        return False


def _get_object_data(request):
    if request.content_type == 'application/json':
        return _get_object_data_from_json_body(request)
    else:
        return _get_object_data_from_stream(request)


def _get_object_data_from_stream(request):
    if 'Content-Length' not in request.headers or not _is_long(request.headers['Content-Length']):
        raise HTTPLengthRequired
    content_length = long(request.headers['Content-Length'])
    object_data = request.body_file
    if content_length == 0:
        raise HTTPBadRequest('body is empty')
    return object_data


def _get_object_data_from_json_body(request):
    json_data = _get_json_from_request(request)
    if 'url' not in json_data:
        raise ValidationFailure('Url is required.')
    keys = _parse_keys_from_url(request, json_data['url'])
    collection = request.registry.collections.get(keys['collection_key'])
    if not collection:
        raise HTTPBadRequest('Collection {} was not found'.format(keys['collection_key']))
    try:
        object_data = collection.object_store.get_object(keys['container_key'], keys['object_key'])
    except NotFoundException:
        raise HTTPBadRequest('Container - object ({0} - {1}) combination was not found in Collection {2}'.format(
            keys['container_key'], keys['object_key'], keys['collection_key']))
    return object_data


def _get_json_from_request(request):
    try:
        return request.json_body
    except AttributeError as e:
        raise HTTPBadRequest(detail="Request has no json body. \n%s" % e)  # pragma: no cover
    except ValueError as e:
        raise HTTPBadRequest(detail="Request has incorrect json body. \n%s" % e)


def _parse_keys_from_url(request, url):
    pattern_get_object = request.route_url('get_object',
                                           collection_key='(?P<collection_key>\w+)',
                                           container_key='(?P<container_key>\w+)',
                                           object_key='(?P<object_key>\w+)'
                                           )
    pattern_re = re.compile(urllib.unquote_plus(pattern_get_object))
    match = pattern_re.match(url)
    if match:
        return match.groupdict()
    else:
        raise ValidationFailure('Url does not match following pattern: {}.'.format(
            urllib.unquote_plus(request.route_url('get_object',
                                                  collection_key='{collection_key}',
                                                  container_key='{container_key}',
                                                  object_key='{object_key}'))))


def _retrieve_collection(request):
    collection_name = request.matchdict['collection_key']
    if collection_name in request.registry.collections:
        collection = request.registry.collections[collection_name]
    else:
        raise HTTPNotFound('collection not found')
    return collection
