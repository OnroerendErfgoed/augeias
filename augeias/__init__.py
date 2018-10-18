from pyramid.config import Configurator
from pyramid.settings import asbool


def includeme(config):
    """this function adds some configuration for the application"""
    # Rewrite urls with trailing slash
    config.include('pyramid_rewrite')
    config.add_rewrite_rule(r'/(?P<path>.*)/', r'/%(path)s')

    config.registry.collections = {}
    config.add_route('home', '/')
    config.add_route('list_collections', pattern='/collections', request_method="GET")
    config.add_route('create_container_and_id', pattern='/collections/{collection_key}/containers',
                     request_method="POST")
    config.add_route('create_container', pattern='/collections/{collection_key}/containers/{container_key}',
                     request_method="PUT")
    config.add_route('delete_container', pattern='/collections/{collection_key}/containers/{container_key}',
                     request_method="DELETE")
    config.add_route('list_object_keys_for_container',
                     pattern='/collections/{collection_key}/containers/{container_key}', request_method="GET",
                     accept='application/json')
    config.add_route('get_container_data',
                     pattern='/collections/{collection_key}/containers/{container_key}',
                     request_method="GET", accept='application/zip')
    config.add_route('create_object_and_id', pattern='/collections/{collection_key}/containers/{container_key}',
                     request_method="POST")
    config.add_route('update_object', pattern='/collections/{collection_key}/containers/{container_key}/{object_key}',
                     request_method="PUT")
    config.add_route('delete_object', pattern='/collections/{collection_key}/containers/{container_key}/{object_key}',
                     request_method="DELETE")
    config.add_route('get_object', pattern='/collections/{collection_key}/containers/{container_key}/{object_key}',
                     request_method="GET")
    config.add_route('get_object_info',
                     pattern='/collections/{collection_key}/containers/{container_key}/{object_key}/meta',
                     request_method="GET")

    config.scan()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    includeme(config)

    if asbool(settings.get('augeias.init_collections', False)):  # pragma: no cover
        config.include('augeias.collections')

    return config.make_wsgi_app()
