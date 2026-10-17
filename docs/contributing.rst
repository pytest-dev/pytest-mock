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

    $ tox -e py314,norewrite

Use ``tox`` rather than running ``pytest`` directly in the virtual env: with the
editable install, pytest does not rewrite the assertions inside ``pytest_mock``
itself, so the tests that check assertion introspection fail there regardless
of your changes.

Style checks and formatting are done automatically during commit courtesy of
`pre-commit <https://pre-commit.com>`_.

Changelog
---------

Changes that affect users need an entry in ``CHANGELOG.rst``, under the
``UNRELEASED`` section at the top. Each entry is a single bullet that starts
with a link to the PR, and the entries are kept in PR number order, without
blank lines between them:

.. code-block:: rst

    * `#123 <https://github.com/pytest-dev/pytest-mock/pull/123>`_: Fixed ``mocker.spy`` ...

Open the PR first to get its number, then add the entry. Changes that only
touch tests or internal tooling don't need an entry.
