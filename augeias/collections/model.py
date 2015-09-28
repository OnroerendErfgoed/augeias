# -*- coding: utf-8 -*-

class Collection(object):

    def __init__(self, name, object_store):
        self.object_store = object_store
        self.name = name
