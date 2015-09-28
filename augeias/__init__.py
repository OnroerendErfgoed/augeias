from pyramid.config import Configurator
from pyramid.settings import asbool


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

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
                     pattern='/collections/{collection_key}/containers/{container_key}', request_method="GET")
    config.add_route('update_object', pattern='/collections/{collection_key}/containers/{container_key}/{object_key}',
                     request_method="PUT")
    config.add_route('delete_object', pattern='/collections/{collection_key}/containers/{container_key}/{object_key}',
                     request_method="DELETE")
    config.add_route('get_object', pattern='/collections/{collection_key}/containers/{container_key}/{object_key}',
                     request_method="GET")

    if asbool(settings.get('augeias.init_collections', True)):  # pragma: no cover
        config.include('augeias.collections')

    config.scan()
    return config.make_wsgi_app()
