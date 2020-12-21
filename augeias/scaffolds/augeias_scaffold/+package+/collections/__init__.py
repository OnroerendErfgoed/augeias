from augeias.stores.PairTreeFileSystemStore import PairTreeFileSystemStore
from augeias.collections.model import Collection


def includeme(config):   # pragma: no cover
    default = Collection(
        name='default',
        object_store=PairTreeFileSystemStore(config.registry.settings['default.store.data_dir'])
    )
    config.registry.collections[default.name] = default
