import io
import tarfile
import uuid
import zipfile

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPLengthRequired
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
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

    @view_config(route_name="update_file_in_zip", permission="edit")
    def update_file_in_zip(self):
        """
        Update a file in an archive object in the data store.
        """
        file_content = _get_object_data(self.request)
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict["container_key"]
        object_key = self.request.matchdict["object_key"]
        file_to_replace = self.request.matchdict["file_name"]
        if "new_file_name" not in self.request.params:
            raise HTTPBadRequest("new_file_name parameter is required")
        new_file_name = self.request.params["new_file_name"]
        zip_content = collection.object_store.get_object(
            container_key, object_key
        )
        new_archive = replace_file_in_zip(
            zip_content, file_to_replace, file_content.read(), new_file_name
        )
        collection.object_store.update_object(
            container_key, object_key, new_archive
        )
        res = Response(content_type="application/json", status=200)
        res.json_body = {
            "container_key": container_key,
            "object_key": object_key,
            "uri": collection.uri_generator.generate_object_uri(
                collection=collection.name,
                container=container_key,
                object=object_key)
        }
        return res

    @view_config(route_name="create_object_and_id", permission="edit")
    def create_object_and_id(self):
        """create an object in the data store and generate an id"""
        object_data = _get_object_data(self.request)
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict["container_key"]
        object_key = str(uuid.uuid4())
        collection.object_store.update_object(
            container_key, object_key, object_data)
        res = Response(content_type="application/json", status=201)
        res.json_body = {
            "container_key": container_key,
            "object_key": object_key,
            "uri": collection.uri_generator.generate_object_uri(
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

    @view_config(route_name='get_file_from_zip', permission='view')
    def get_object_from_archive(self):
        """retrieve a file from an archive object from the data store"""
        collection = _retrieve_collection(self.request)
        container_key = self.request.matchdict['container_key']
        object_key = self.request.matchdict['object_key']
        object_data = collection.object_store.get_object(
            container_key, object_key
        )
        file = get_file_from_archive(object_data, self.request.matchdict['file_name'])
        res = Response(content_type='application/octet-stream', status=200)
        res.body = file
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


def get_file_from_archive(archive_bytes, file_name):
    """
    get a file from a zip/tar in the data store

    :param container_key: key of the container in the data store
    :param object_key: specific object key for the object in the container
    :param file_name: name of the file to get from the zip
    :return content of the file or None
    """
    archive_bytes_as_file = io.BytesIO(archive_bytes)
    for name, file_bytes in get_archive_members(archive_bytes_as_file):
        if name == file_name:
            return file_bytes
    raise HTTPBadRequest("File not found in archive")


def get_archive_members(archive_content):
    """
    yield the members of a zip or tar archive

    :param archive_content: content of the archive
    :return: generator of the members of the archive
    """
    with open_archive(archive_content) as archive:
        if isinstance(archive, zipfile.ZipFile):
            for name in archive.namelist():
                yield name, archive.read(name)
        else:
            for member in archive.getmembers():
                f = archive.extractfile(member)
                yield member.name, f.read()


def open_archive(archive_content):
    """
    Open a zip or tar archive

    :param archive_content: content of the archive
    :return: the opened archive
    """
    if zipfile.is_zipfile(archive_content):
        archive_content.seek(0)  # the zip check actually reads the bytes, so reset.
        return zipfile.ZipFile(archive_content)
    else:
        archive_content.seek(0)
        return tarfile.open(fileobj=archive_content)


def replace_file_in_zip(zip_content, file_to_replace, file_content, new_file_name):
    """
    Replace a file in a zip file with new content

    :param zip_content: content of the original zip file
    :param file_to_replace: name of the file to replace
    :param file_content: content of the new file
    :param new_file_name: name of the new file
    :return: content of the updated zip file
    """
    with io.BytesIO(zip_content) as original_zip_buffer:
        with zipfile.ZipFile(original_zip_buffer, "r") as original_zip:
            # Create a new in-memory zip file
            with io.BytesIO() as new_zip_buffer:
                with zipfile.ZipFile(
                    new_zip_buffer, "a", zipfile.ZIP_DEFLATED
                ) as new_zip:
                    current_file_names = original_zip.namelist()
                    if file_to_replace not in current_file_names:
                        raise HTTPBadRequest("File to replace not found in archive")
                    for filename in current_file_names:
                        # Skip the file to be replaced
                        if filename == file_to_replace:
                            continue
                        # Copy all other files
                        content = original_zip.read(filename)
                        new_zip.writestr(filename, content)
                    # Add the new file
                    new_zip.writestr(new_file_name, file_content)
                # Get the content of the new zip file
                updated_zip_content = new_zip_buffer.getvalue()

    return updated_zip_content
