# -*- coding: utf-8 -*-
from storageprovider.stores.PairTreeFileSystemStore import PairTreeFileSystemStore
from storageprovider.collections.model import Collection


def includeme(config):   # pragma: no cover
    beeldbank = Collection(name='beeldbank', object_store=PairTreeFileSystemStore('/home/bart/data/beeldbank_store/data'))
    config.registry.collections[beeldbank.name] = beeldbank

    besluiten = Collection(name='besluiten', object_store=PairTreeFileSystemStore('/home/bart/data/besluiten_store/data'))
    config.registry.collections[besluiten.name] = besluiten

