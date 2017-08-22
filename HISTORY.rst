0.3.0 (22-08-2017)
------------------

- Add 'copy' functionality to update_object endpoint. In this case the view accepts the (augeias) location of the file object (host url, collection_key, container_key and object_key) and copies it to a new location on the same augeias instance. (#17)
- Add Endpoint to create object and key. (#20)
- Add Endpoint to retrieve meta data (mimetype (#13), size, time last modification) from object.

0.2.0 (07-11-2015)
------------------

- Add a scaffold for generating an Augeias instance. Use by running `pcreate -s
  augeias`. (#6)
- Update docs with information about making a HEAD request for an object's
  metdata. (#9)
- Added permission hooks so it's possible for an Augeias instance to add
  authentication. (#2)
- Removed some OE specific configuration and made it more generic. (#8)
- Added some installation instructions.

0.1.0 (20-10-2015)
------------------

- Initial version
- Has as single, filesystem based, store.
