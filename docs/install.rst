============
Installation
============

Getting an installation of Augeias running is very simple. As always we
recommend working with a separate virtualenvironment for this.

.. code-block:: bash

    $ mkvirtualenv augeias_demo
    $ pip install -U augeias


Once Augeias is installed, you can call upon a pyramid scaffold to generate
the demo site.

.. code-block:: bash

    $ pcreate -s augeias augeias_demo
    $ cd augeias_demo

Just a few more steps and you've got a demo version running.

.. code-block:: bash

    $ pip install -r requirements-dev.txt
    $ python setup.py develop
    $ pserve development.ini

The Augeias demo instance is now running on your localhost at port 6543. To
reach it, open your browser and surf to the address `<http://localhost:6543>`_.

This basic version comes with one configured collection `default`.
