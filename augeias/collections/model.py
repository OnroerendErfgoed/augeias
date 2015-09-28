# -*- coding: utf-8 -*-

from augeias.uri import DefaultUriGenerator


class Collection(object):

    def __init__(self, name, object_store, **kwargs):
        self.object_store = object_store
        self.name = name
        if 'uri_generator' in kwargs:
            self.uri_generator = kwargs.get('uri_generator')
        else:
            self.uri_generator = DefaultUriGenerator()
