import os

from augeias.collections.model import Collection
from augeias.stores.PairTreeFileSystemStore import PairTreeFileSystemStore


def includeme(config):  # pragma: no cover
    cheeses = Collection(
        name="cheeses",
        object_store=PairTreeFileSystemStore(os.path.expanduser("~/data/cheeses/data")),
    )
    config.registry.collections[cheeses.name] = cheeses

    trees = Collection(
        name="trees",
        object_store=PairTreeFileSystemStore(os.path.expanduser("~/data/trees/data")),
    )
    config.registry.collections[trees.name] = trees
