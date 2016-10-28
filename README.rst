===========
pytest-mock
===========

This plugin installs a ``mocker`` fixture which is a thin-wrapper around the patching API
provided by the `mock package <http://pypi.python.org/pypi/mock>`_,
but with the benefit of not having to worry about undoing patches at the end
of a test:

.. code-block:: python


    def test_unix_fs(mocker):
        mocker.patch('os.remove')
        UnixFS.rm('file')
        os.remove.assert_called_once_with('file')


.. Using PNG badges because PyPI doesn't support SVG

|python| |version| |downloads| |ci| |appveyor| |coverage|

.. |version| image:: http://img.shields.io/pypi/v/pytest-mock.png
  :target: https://pypi.python.org/pypi/pytest-mock

.. |downloads| image:: http://img.shields.io/pypi/dm/pytest-mock.png
  :target: https://pypi.python.org/pypi/pytest-mock

.. |ci| image:: http://img.shields.io/travis/pytest-dev/pytest-mock.png
  :target: https://travis-ci.org/pytest-dev/pytest-mock

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/pid1t7iuwhkm9eh6/branch/master?svg=true
  :target: https://ci.appveyor.com/project/pytestbot/pytest-mock

.. |coverage| image:: http://img.shields.io/coveralls/pytest-dev/pytest-mock.png
  :target: https://coveralls.io/r/pytest-dev/pytest-mock

.. |python| image:: https://img.shields.io/pypi/pyversions/pytest-mock.svg
  :target: https://pypi.python.org/pypi/pytest-mock/

Usage
=====

The ``mocker`` fixture has the same API as
`mock.patch <http://www.voidspace.org.uk/python/mock/patch.html#patch-decorators>`_,
supporting the same arguments:

.. code-block:: python

    def test_foo(mocker):
        # all valid calls
        mocker.patch('os.remove')
        mocker.patch.object(os, 'listdir', autospec=True)
        mocked_isfile = mocker.patch('os.path.isfile')

The supported methods are:

* ``mocker.patch``: see http://www.voidspace.org.uk/python/mock/patch.html#patch.
* ``mocker.patch.object``: see http://www.voidspace.org.uk/python/mock/patch.html#patch-object.
* ``mocker.patch.multiple``: see http://www.voidspace.org.uk/python/mock/patch.html#patch-multiple.
* ``mocker.patch.dict``: see http://www.voidspace.org.uk/python/mock/patch.html#patch-dict.
* ``mocker.stopall()``: stops all active patches up to this point.
* ``mocker.resetall()``: calls ``reset_mock()`` in all mocked objects up to this point.

Some objects from the ``mock`` module are accessible directly from ``mocker`` for convenience:

* `Mock <https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock>`_
* `MagicMock <https://docs.python.org/3/library/unittest.mock.html#unittest.mock.MagicMock>`_
* `PropertyMock <https://docs.python.org/3/library/unittest.mock.html#unittest.mock.PropertyMock>`_
* `ANY <https://docs.python.org/3/library/unittest.mock.html#any>`_
* `call <https://docs.python.org/3/library/unittest.mock.html#call>`_ *(Version 1.1)*
* `sentinel <https://docs.python.org/3/library/unittest.mock.html#sentinel>`_ *(Version 1.2)*
* `mock_open <https://docs.python.org/3/library/unittest.mock.html#mock-open>`_


Spy
---

The spy acts exactly like the original method in all cases, except it allows use of `mock`
features with it, like retrieving call count. It also works for class and static methods.


.. code-block:: python

    def test_spy(mocker):
        class Foo(object):
            def bar(self):
                return 42

        foo = Foo()
        mocker.spy(foo, 'bar')
        assert foo.bar() == 42
        assert foo.bar.call_count == 1

Stub
----


The stub is a mock object that accepts any arguments and is useful to test callbacks, for instance.
May be passed a name to be used by the constructed stub object in its repr (useful for debugging).

.. code-block:: python

    def test_stub(mocker):
        def foo(on_something):
            on_something('foo', 'bar')

        stub = mocker.stub(name='on_something_stub')

        foo(stub)
        stub.assert_called_once_with('foo', 'bar')


Improved reporting of mock call assertion errors
------------------------------------------------


This plugin monkeypatches the mock library to improve pytest output for failures
of mock call assertions like ``Mock.assert_called_with()`` by hiding internal traceback
entries from the ``mock`` module.

It also adds introspection information on differing call arguments when
calling the helper methods. This features catches `AssertionError` raised in
the method, and uses py.test's own `advanced assertions`_ to return a better
diff::


            m = mocker.patch.object(DS, 'create_char')
            DS().create_char('Raistlin', class_='mag', gift=12)
    >       m.assert_called_once_with('Raistlin', class_='mage', gift=12)
    E       assert {'class_': 'mag', 'gift': 12} == {'class_': 'mage', 'gift': 12}
    E         Omitting 1 identical items, use -v to show
    E         Differing items:
    E         {'class_': 'mag'} != {'class_': 'mage'}
    E         Use -v to get the full diff


This is useful when asserting mock calls with many/nested arguments and trying
to quickly see the difference.

This feature is probably safe, but if you encounter any problems it can be disabled in
your ``pytest.ini`` file:

.. code-block:: ini

    [pytest]
    mock_traceback_monkeypatch = false

Note that this feature is automatically disabled with the ``--tb=native`` option. The underlying
mechanism used to suppress traceback entries from ``mock`` module does not work with that option
anyway plus it generates confusing messages on Python 3.5 due to exception chaining

.. _advanced assertions: https://pytest.org/latest/assert.html


Requirements
============

* Python 2.6+, Python 3.3+
* pytest
* mock (for Python 2)


Install
=======

Install using `pip <http://pip-installer.org/>`_:

.. code-block:: console

    $ pip install pytest-mock

Changelog
=========

Please consult the `changelog page`_.

.. _changelog page: https://github.com/pytest-dev/pytest-mock/blob/master/CHANGELOG.rst

Why bother with a plugin?
=========================

There are a number of different ``patch`` usages in the standard ``mock`` API,
but IMHO they don't scale very well when you have more than one or two
patches to apply.

It may lead to an excessive nesting of ``with`` statements, breaking the flow
of the test:

.. code-block:: python

    import mock

    def test_unix_fs():
        with mock.patch('os.remove'):
            UnixFS.rm('file')
            os.remove.assert_called_once_with('file')

            with mock.patch('os.listdir'):
                assert UnixFS.ls('dir') == expected
                # ...

        with mock.patch('shutil.copy'):
            UnixFS.cp('src', 'dst')
            # ...


One can use ``patch`` as a decorator to improve the flow of the test:

.. code-block:: python

    @mock.patch('os.remove')
    @mock.patch('os.listdir')
    @mock.patch('shutil.copy')
    def test_unix_fs(mocked_copy, mocked_listdir, mocked_remove):
        UnixFS.rm('file')
        os.remove.assert_called_once_with('file')

        assert UnixFS.ls('dir') == expected
        # ...

        UnixFS.cp('src', 'dst')
        # ...

But this poses a few disadvantages:

- test functions must receive the mock objects as parameter, even if you don't plan to
  access them directly; also, order depends on the order of the decorated ``patch``
  functions;
- receiving the mocks as parameters doesn't mix nicely with pytest's approach of
  naming fixtures as parameters, or ``pytest.mark.parametrize``;
- you can't easily undo the mocking during the test execution;


**Note**

Although mocker's API is intentionally the same as ``mock.patch``'s, its uses as context managers and function decorators are **not** supported. The purpose of this plugin is to make the use of context managers and function decorators for mocking unnecessary. Indeed, trying to use the functionality in ``mocker`` in this manner can lead to non-intuitive errors:

.. code-block:: python

    def test_context_manager(mocker):
        a = A()
        with mocker.patch.object(a, 'doIt', return_value=True, autospec=True):
            assert a.doIt() == True

.. code-block:: console

    ================================== FAILURES ===================================
    ____________________________ test_context_manager _____________________________
    in test_context_manager
        with mocker.patch.object(a, 'doIt', return_value=True, autospec=True):
    E   AttributeError: __exit__


License
=======

Distributed under the terms of the `MIT`_ license.

.. _MIT: https://github.com/pytest-dev/pytest-mock/blob/master/LICENSE
