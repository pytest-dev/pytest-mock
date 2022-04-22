
============
Contributing
============

Contributions are welcome! After cloning the repository, create a virtual env
and install ``pytest-mock`` in editable mode with ``dev`` extras:

.. code-block:: console

    $ pip install --editable .[dev]
    $ pre-commit install

Tests are run with ``tox``, you can run the baseline environments before submitting a PR:

.. code-block:: console

    $ tox -e py38,linting

Style checks and formatting are done automatically during commit courtesy of
`pre-commit <https://pre-commit.com>`_.
