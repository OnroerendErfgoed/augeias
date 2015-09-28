# -*- coding: utf-8 -*-
from augeias.stores.PairTreeFileSystemStore import PairTreeFileSystemStore
from augeias.collections.model import Collection


def includeme(config):   # pragma: no cover
    beeldbank = Collection(name='beeldbank', object_store=PairTreeFileSystemStore('~/data/beeldbank_store/data'))
    config.registry.collections[beeldbank.name] = beeldbank

    besluiten = Collection(name='besluiten', object_store=PairTreeFileSystemStore('~/data/besluiten_store/data'))
    config.registry.collections[besluiten.name] = besluiten

