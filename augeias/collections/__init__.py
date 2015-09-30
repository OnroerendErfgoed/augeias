# -*- coding: utf-8 -*-
from augeias.stores.PairTreeFileSystemStore import PairTreeFileSystemStore
from augeias.collections.model import Collection
import os

def includeme(config):   # pragma: no cover
    beeldbank = Collection(name='beeldbank', object_store=PairTreeFileSystemStore(os.path.expanduser('~/data/beeldbank_store/data')))
    config.registry.collections[beeldbank.name] = beeldbank

    besluiten = Collection(name='besluiten', object_store=PairTreeFileSystemStore(os.path.expanduser('~/data/besluiten_store/data')))
    config.registry.collections[besluiten.name] = besluiten

