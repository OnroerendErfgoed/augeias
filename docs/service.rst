========
Services
========

The augeias provides services on `Collections`, `Containers` and
`Objects`. You can think of them as a three-leveled hierarchy. At the top there
are the collections. Each collection contains containers. And within each
container are 1 or more objects.


.. http:get:: /collections

    Show a list of all collections. Every collection is a set of containers.
    They might have some sort of meaning as defined by the implementer. In
    practice quite often there will be a collection for every application.


    **Example request**

    .. sourcecode:: http

        GET /collections HTTP/1.1
        Host: augeias.onroerenderfgoed.be
        Accept: application/json

    **Example response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        [
            {
                'collection_key': 'default',
                'uri': 'https://storage.onroerenderfgoed.be/collections/default'
            } , {
                'collection_key': 'my_collection',
                'uri': 'https://storage.onroerenderfgoed.be/collections/my_collection'
            }
        ]

    :reqheader Accept: The response content type depends on this header. 
        Currently only :mimetype:`application/json` is supported.

    :resheader Content-Type: This service currently always returns 
        :mimetype:`application/json`


.. http:post:: /collections/{collection_key}/containers

    Create a new container. The server will generate a random container key.


    **Example request**:

    .. sourcecode:: http

        POST /collections/mine/containers HTTP/1.1
        Host: augeias.onroerenderfgoed.be
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
        Content-Type: application/json
        Location: https://storage.onroerenderfgoed.be/collections/mine/containers/6ed5a007-41cf-49ed-8cb8-184fa5f48e42

        {
            'container_key': '6ed5a007-41cf-49ed-8cb8-184fa5f48e42',
            'uri': 'https://storage.onroerenderfgoed.be/collections/mine/containers/6ed5a007-41cf-49ed-8cb8-184fa5f48e42'
        }

    :param collection_key: Key for the collection within which the container
        will be placed.

    :reqheader Accept: The response content type depends on this header. 
        Currently only :mimetype:`application/json` is supported.

    :resheader Location: The url where the newly added container can be found.
    :resheader Content-Type: This service currently always returns 
        :mimetype:`application/json`

    :statuscode 201: The container was added succesfully.
    :statuscode 404: The collection `collection_key` does not exist.


.. http:put:: /collections/{collection_key}/containers/{container_key}

    Create a new container. Allowsyou to choose your own container key. If the
    container already exists, nothing will happen.


    **Example request**:

    .. sourcecode:: http

        PUT /collections/mine/containers/abcd HTTP/1.1
        Host: augeias.onroerenderfgoed.be
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
        Content-Type: application/json
        Location: https://storage.onroerenderfgoed.be/collections/mine/containers/abcd

        {
            'container_key': 'abcd'
            'uri': 'https://storage.onroerenderfgoed.be/collections/mine/containers/abcd'
        }

    :param collection_key: Key for the collection within which the container
        will be placed.
    :param container_key: Key for the container that will be created.

    :reqheader Accept: The response content type depends on this header. 
        Currently only :mimetype:`application/json` is supported.

    :resheader Location: The url where the newly added container can be found.
    :resheader Content-Type: This service currently always returns 
        :mimetype:`application/json`

    :statuscode 200: The container already existed.
    :statuscode 201: The container was added succesfully.
    :statuscode 404: The collection `collection_key` does not exist.


.. http:delete:: /collections/{collection_key}/containers/{container_key}

    Remove a container and all the objects in it.


    **Example request**:

    .. sourcecode:: http

        DELETE /collections/mine/containers/abcd HTTP/1.1
        Host: augeias.onroerenderfgoed.be
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            'container_key': 'abcd'
            'uri': 'https://storage.onroerenderfgoed.be/collections/mine/containers/abcd'
        }

    :param collection_key: Key for the collection where the container lives.
    :param container_key: Key for the container that will be deleted.

    :reqheader Accept: The response content type depends on this header. 
        Currently only :mimetype:`application/json` is supported.

    :resheader Content-Type: This service currently always returns 
        :mimetype:`application/json`

    :statuscode 200: The container was deleted.
    :statuscode 404: The collection `collection_key` does not exist or the
        container `container_key` does not exist within this collection.


.. http:get:: /collections/{collection_key}/containers/{container_key}

    Show all objects present in this container.


    **Example request**:

    .. sourcecode:: http

        GET /collections/mine/containers/a311efb7-f125-4d0a-aa26-69d3657a2d06 HTTP/1.1
        Host: augeias.onroerenderfgoed.be
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        [
            "square",
            "small",
            "medium",
            "original",
            "large",
            "full"
        ]

    :param collection_key: Key for the collection where the container lives.
    :param container_key: Key for the container that will be queried.

    :reqheader Accept: The response content type depends on this header. 
        Currently only :mimetype:`application/json` is supported.

    :resheader Content-Type: This service currently always returns 
        :mimetype:`application/json`

    :statuscode 200: The container exists.
    :statuscode 404: The collection `collection_key` or the container
        `container_key` does not exist.


.. http:head:: /collections/{collection_key}/containers/{container_key}/{object_key}

    Fetch metadata on a object without actually fetching the object.


    **Example request**:

    .. sourcecode:: http

        HEAD /collections/mine/containers/a311efb7-f125-4d0a-aa26-69d3657a2d06/full HTTP/1.1
        Host: augeias.onroerenderfgoed.be
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Date: Fri, 30 Oct 2015 07:11:44 GMT
        Server: Apache/2.4.7 (Ubuntu)
        Content-type: image/jpeg
        Content-Length: 23562

    :param collection_key: Key for the collection where the container lives.
    :param container_key: Key for the container where the object lives.
    :param object_key: Key for the object that will be fetched

    :statuscode 200: The object was found.
    :statuscode 404: The collection `collection_key` or the container
        `container_key` or the `object_key` does not exist.


.. http:get:: /collections/{collection_key}/containers/{container_key}/{object_key}

    Fetch an object from a container.


    **Example request**:

    .. sourcecode:: http

        GET /collections/mine/containers/a311efb7-f125-4d0a-aa26-69d3657a2d06/full HTTP/1.1
        Host: augeias.onroerenderfgoed.be
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Date: Fri, 30 Oct 2015 07:11:44 GMT
        Server: Apache/2.4.7 (Ubuntu)
        Content-type: image/jpeg
        Content-Length: 23562

        <snipped>

    :param collection_key: Key for the collection where the container lives.
    :param container_key: Key for the container where the object lives.
    :param object_key: Key for the object that will be fetched

    :statuscode 200: The object was found.
    :statuscode 404: The collection `collection_key` or the container
        `container_key` or the `object_key` does not exist.

.. http:get:: /collections/{collection_key}/containers/{container_key}/{object_key}/meta

    Fetch object info (mimetype, size, time last modification).


    **Example request**:

    .. sourcecode:: http

        GET /collections/mine/containers/a311efb7-f125-4d0a-aa26-69d3657a2d06/full/meta HTTP/1.1
        Host: augeias.onroerenderfgoed.be
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-type: image/jpeg

        {
                "time_last_modification": "2017-08-18T13:52:25.970242",
                "mime": "image/jpeg",
                "size": 11370
        }


    :param collection_key: Key for the collection where the container lives.
    :param container_key: Key for the container where the object lives.
    :param object_key: Key for the object that will be fetched

    :statuscode 200: The object was found.
    :statuscode 404: The collection `collection_key` or the container
        `container_key` or the `object_key` does not exist.


.. http:post:: /collections/{collection_key}/containers/{container_key}

    Create a new object. The server will generate a random object key.


    **Example request**:

    .. sourcecode:: http

        POST /collections/mine/containers/mine_container HTTP/1.1
        Host: augeias.onroerenderfgoed.be
        Content-Type: application/octet-stream
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
        Content-Type: application/json
        Location: https://storage.onroerenderfgoed.be/collections/mine/containers/mine_container/6ed5a007-41cf-49ed-8cb8-184fa5f48e42

        {
            'container_key': 'mine_container',
            'object_key': '6ed5a007-41cf-49ed-8cb8-184fa5f48e42',
            'collection_key': 'mine'
            'uri': 'https://storage.onroerenderfgoed.be/collections/mine/containers/mine_container/6ed5a007-41cf-49ed-8cb8-184fa5f48e42'
        }

    :param collection_key: Key for the collection where the container lives.
    :param container_key: Key for the container where the object lives.
    :param object_key: Key for the object that will be created or updated.

    :reqheader Content-Type:
        :mimetype:`application/json` or :mimetype:`application/octet-stream`
    :reqheader Accept: The response content type depends on this header.
        Currently only :mimetype:`application/json` is supported.

    :resheader Content-Type: This service currently always returns
        :mimetype:`application/json`

    :statuscode 201: The object and the key were created.
    :statuscode 404: The collection `collection_key` or the container
        `container_key` does not exist.


.. http:put:: /collections/{collection_key}/containers/{container_key}/{object_key}

    Add or update an object in a container.

    If an object with this key already exists, it will be overwritten. If not,
    it will be created.


    **Example request**:

    .. sourcecode:: http

        PUT /collections/mine/containers/a311efb7-f125-4d0a-aa26-69d3657a2d06/circle HTTP/1.1
        Host: augeias.onroerenderfgoed.be
        Content-Type: application/octet-stream
        Accept: application/json

    **Exmaple response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            'uri': 'https://id.erfgoed.net/storage/collections/mine/containers/a311efb7-f125-4d0a-aa26-69d3657a2d06/circle',
            'object_key': 'circle',
            'container_key': 'a311efb7-f125-4d0a-aa26-69d3657a2d06',
            'collection_key': 'mine'
        }

    :param collection_key: Key for the collection where the container lives.
    :param container_key: Key for the container where the object lives.
    :param object_key: Key for the object that will be created or updated.

    :reqheader Content-Type:
        :mimetype:`application/json` or :mimetype:`application/octet-stream`
    :reqheader Accept: The response content type depends on this header. 
        Currently only :mimetype:`application/json` is supported.

    :resheader Content-Type: This service currently always returns
        :mimetype:`application/json`

    :statuscode 200: The object was updated.
    :statuscode 201: There was no object present with this key, it was created.
    :statuscode 404: The collection `collection_key` or the container
        `container_key` does not exist.

.. http:put:: /collections/{collection_key}/containers/{container_key}/{object_key}

    Copy an object from one store location into another within the same Augeias instance.
    The input json data must contain host url, collection_key, container_key and object_key of the object that needs to be copied.

    If an object with this key already exists, it will be overwritten. If not,
    it will be created.


    **Example request**:

    .. sourcecode:: http

        PUT /collections/mine/containers/a311efb7-f125-4d0a-aa26-69d3657a2d06/circle HTTP/1.1
        Host: augeias.onroerenderfgoed.be
        Content-Type: application/json
        Accept: application/json

        {
          "host_url": "http://augeias.onroerenderfgoed.be",
          "collection_key": "temp",
          "container_key": "container_id",
          "object_key": "circletemp"
        }

    **Exmaple response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "uri": "https://id.erfgoed.net/storage/collections/mine/containers/a311efb7-f125-4d0a-aa26-69d3657a2d06/circle",
            "object_key": "circle",
            "container_key": "a311efb7-f125-4d0a-aa26-69d3657a2d06",
            "collection_key": "mine"
        }

    :param collection_key: Key for the collection where the container lives.
    :param container_key: Key for the container where the object lives.
    :param object_key: Key for the object that will be created or updated.

    :reqheader Content-Type:
        :mimetype:`application/json` or :mimetype:`application/octet-stream`
    :reqheader Accept: The response content type depends on this header.
        Currently only :mimetype:`application/json` is supported.

    :resheader Content-Type: This service currently always returns
        :mimetype:`application/json`

    :statuscode 200: The object was copied.
    :statuscode 201: There was no object present with this key, it was created.
    :statuscode 400: Validation failure. The input url of the object in the json body is not correct.
    :statuscode 404: The collection `collection_key` or the container
        `container_key` does not exist.


.. http:delete:: /collections/{collection_key}/containers/{container_key}/{object_key}

    Delete an object from a container.

    **Example request**:

    .. sourcecode:: http

        DELETE /collections/mine/containers/a311efb7-f125-4d0a-aa26-69d3657a2d06/full HTTP/1.1
        Host: augeias.onroerenderfgoed.be
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "uri": "https://id.erfgoed.net/storage/collections/mine/containers/a311efb7-f125-4d0a-aa26-69d3657a2d06/circle",
            "object_key":"full",
            "container_key":"a311efb7-f125-4d0a-aa26-69d3657a2d06",
            "collection_key": "mine"
        }

    :statuscode 200: The object was deleted.
    :statuscode 404: The collection `collection_key` or the container
        `container_key` or the `object_key` does not exist.

