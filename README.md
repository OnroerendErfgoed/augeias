# Augeias

[![image](https://badge.fury.io/py/augeias.png)](http://badge.fury.io/py/augeias)
[![image](https://readthedocs.org/projects/augeias/badge/?version=latest)](https://readthedocs.org/projects/augeias/?badge=latest)
[![image](https://travis-ci.org/OnroerendErfgoed/augeias.png?branch=master)](https://travis-ci.org/OnroerendErfgoed/augeias)
[![image](https://coveralls.io/repos/OnroerendErfgoed/augeias/badge.svg?branch=master&service=github)](https://coveralls.io/r/OnroerendErfgoed/augeias?branch=master)
[![image](https://scrutinizer-ci.com/g/OnroerendErfgoed/augeias/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/OnroerendErfgoed/augeias/?branch=master)

Augeias. Stores your files.

Augeias is a small, RESTful, webapplication that allows you to store
digital objects in an object store. While it allows you to communicate
with you objects as a service, it also decouples the storage
implementation from the interface.

## How to work with pip-compile / pip-sync
full docs: https://pip-tools.readthedocs.io/en/latest/

First install the package:
```sh
pip install pip-tools
```

#### local development
Create a virutal environment and sync with the requirements-dev.txt file.

```sh
pip-sync requirements-dev.txt
```
This will install all the packages needed for development, including testing libraries and waitress.

Fast pip-compile
```sh
PIP_COMPILE_ARGS="-v --no-header --strip-extras --no-emit-find-links pyproject.toml"
uv pip compile $PIP_COMPILE_ARGS -o requirements.txt
uv pip compile $PIP_COMPILE_ARGS -o requirements-dev.txt --all-extras
```