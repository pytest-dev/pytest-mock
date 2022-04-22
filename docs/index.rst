pytest-mock
===========

This `pytest`_ plugin provides a ``mocker`` fixture which is a thin-wrapper around the patching API
provided by the `mock package <http://pypi.python.org/pypi/mock>`_:

.. code-block:: python

    import os

    class UnixFS:

        @staticmethod
        def rm(filename):
            os.remove(filename)

    def test_unix_fs(mocker):
        mocker.patch('os.remove')
        UnixFS.rm('file')
        os.remove.assert_called_once_with('file')


Besides undoing the mocking automatically after the end of the test, it also provides other
nice utilities such as ``spy`` and ``stub``, and uses pytest introspection when
comparing calls.


Install
=======

Install using `pip <http://pip-installer.org/>`_:

.. code-block:: console

    $ pip install pytest-mock


.. _`pytest`: https://pytest.org

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   configuration
   remarks
   contributing
   about
   changelog
