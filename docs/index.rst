.. Augeias documentation master file, created by
   sphinx-quickstart on Wed May 21 12:13:08 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Augeias's documentation!
===================================

Augeias is a small, RESTful, webapplication that allows you to store digital
objects in an object store. While it allows you to communicate with you objects
as a service, it also decouples the storage implementation from the interface. 

For this purpose, Augeias, allows you to define multiple collections. Every
collection can be served by a different storage module. So, one collection might
store it's objects on the filesystem while another one might store it's objects
in an Amazon S3 environment. The client that communicates  with Augeias doesn't
need to know where the digit alobjects it's receiving are stored.

.. toctree::
   :maxdepth: 2

   install
   service
   api
   changes
   glossary

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
