import uuid

from pyramid.response import Response
from pyramid.httpexceptions import HTTPLengthRequired, HTTPBadRequest, HTTPNotFound
from pyramid.view import view_config

from augeias.stores.error import NotFoundException


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


class AugeiasView:

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
        """
        Update an object in the data store.
        The input object data may be:
        - an object stream (Content-Type: application/octet-stream),
        - or a store location (host url, collection_key, container_key and object_key)
            within the same Augeias instance (Content-Type: application/json).
        """
        object_data = _get_object_data(self.request)
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict['container_key']
        object_key = self.request.matchdict['object_key']
        if len(object_key) < 3:
            raise ValidationFailure('The object key must be 3 characters long')
        collection.object_store.update_object(
            container_key, object_key, object_data)
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
        """create an object in the data store and generate an id"""
        object_data = _get_object_data(self.request)
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict['container_key']
        object_key = str(uuid.uuid4())
        collection.object_store.update_object(
            container_key, object_key, object_data)
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
        """delete an object from the data store"""
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
        """retrieve an object from the data store"""
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict['container_key']
        object_key = self.request.matchdict['object_key']
        object_data = collection.object_store.get_object(
            container_key, object_key)
        content_type = collection.object_store.get_object_info(
            container_key, object_key)['mime']
        res = Response(content_type=content_type, status=200)
        res.body = object_data
        return res

    @view_config(route_name='get_object_info', permission='view')
    def get_object_info(self):
        """retrieve object info (mimetype, size, time last modification) from the data store"""
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict['container_key']
        object_key = self.request.matchdict['object_key']
        res = Response(content_type='application/json', status=200)
        res.json_body = collection.object_store.get_object_info(
            container_key, object_key)
        return res

    @view_config(route_name='list_object_keys_for_container', permission='view')
    def list_object_keys_for_container(self):
        """list all object keys for a container in the data store"""
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict['container_key']
        res = Response(content_type='application/json', status=200)
        res.json_body = collection.object_store.list_object_keys_for_container(
            container_key)
        return res

    @view_config(route_name='get_container_data', permission='view')
    def get_container_data(self):
        """Get a container from the data store as zip."""
        parameters = self.request.GET
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict['container_key']
        zip_file = collection.object_store.get_container_data(
            container_key, translations=parameters
        )
        filename = str(container_key) + '.zip'
        disposition = (f'attachment; filename={filename}')
        res = Response(content_type='application/zip', status=200,
                       content_disposition=disposition)
        res.body = zip_file.read()
        return res

    @view_config(route_name='create_container', permission='edit')
    def create_container(self):
        """create a new container in the data store"""
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
        """create a new container in the data store and generate an id"""
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
        """delete a container in the data store"""
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


def _is_integer(s):
    try:
        int(s)  # python 2.7 'auto-promotes' int to long if required
        return True
    except ValueError:
        return False


def _get_object_data(request):
    if request.content_type == 'application/json':
        return _get_object_data_from_json_body(request)
    else:
        return _get_object_data_from_stream(request)


def _get_object_data_from_stream(request):
    if 'Content-Length' not in request.headers or not _is_integer(request.headers['Content-Length']):
        raise HTTPLengthRequired
    content_length = int(request.headers['Content-Length'])
    object_data = request.body_file
    if content_length == 0:
        raise HTTPBadRequest('body is empty')
    return object_data


def _get_object_data_from_json_body(request):
    """
    The json body contains the location of the input object.
    The body must include be the host url, collection_key, container_key and object_key.
    """
    json_data = _get_json_from_request(request)
    required_keys = ['host_url', 'collection_key',
                     'container_key', 'object_key']
    missing_keys = set(required_keys) - set(json_data.keys())
    if missing_keys:
        raise HTTPBadRequest(
            '\n'.join(f'{key} is Required.' for key in missing_keys))
    if request.host_url != json_data['host_url']:
        raise ValidationFailure(
            f'Host must be equal to the current host url {request.host}.')
    collection = request.registry.collections.get(json_data['collection_key'])
    if not collection:
        raise HTTPBadRequest('Collection {} was not found'.format(
            json_data['collection_key']))
    try:
        object_data = collection.object_store.get_object(
            json_data['container_key'], json_data['object_key'])
    except NotFoundException:
        raise HTTPBadRequest('Container - object ({} - {}) combination was not found in Collection {}'.format(
            json_data['container_key'], json_data['object_key'], json_data['collection_key']))
    return object_data


def _get_json_from_request(request):
    try:
        return request.json_body
    except AttributeError as e:
        raise HTTPBadRequest(
            detail="Request has no json body. \n%s" % e)  # pragma: no cover
    except ValueError as e:
        raise HTTPBadRequest(
            detail="Request has incorrect json body. \n%s" % e)


def _retrieve_collection(request):
    collection_name = request.matchdict['collection_key']
    if collection_name in request.registry.collections:
        collection = request.registry.collections[collection_name]
    else:
        raise HTTPNotFound('collection not found')
    return collection
