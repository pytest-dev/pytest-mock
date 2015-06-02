===========
pytest-mock
===========

This plugin installs a ``mocker`` fixture which is a thin-wrapper around the patching API
provided by the excellent `mock <http://pypi.python.org/pypi/mock>`_ package,
but with the benefit of not having to worry about undoing patches at the end
of a test:

.. code-block:: python

 
    def test_unix_fs(mocker):
        mocker.patch('os.remove')
        UnixFS.rm('file')
        os.remove.assert_called_once_with('file')
        

.. Using PNG badges because PyPI doesn't support SVG

|python| |version| |downloads| |ci| |coverage|

.. |version| image:: http://img.shields.io/pypi/v/pytest-mock.png
  :target: https://pypi.python.org/pypi/pytest-mock
  
.. |downloads| image:: http://img.shields.io/pypi/dm/pytest-mock.png
  :target: https://pypi.python.org/pypi/pytest-mock

.. |ci| image:: http://img.shields.io/travis/pytest-dev/pytest-mock.png
  :target: https://travis-ci.org/pytest-dev/pytest-mock

.. |coverage| image:: http://img.shields.io/coveralls/pytest-dev/pytest-mock.png
  :target: https://coveralls.io/r/pytest-dev/pytest-mock

.. |python| image:: https://pypip.in/py_versions/pytest-mock/badge.png
  :target: https://pypi.python.org/pypi/pytest-mock/
  :alt: Supported Python versions


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
* ``mocker.stopall()``: stops all active patches at this point.

You can also access ``Mock`` and ``MagicMock`` directly using from ``mocker``
fixture:

.. code-block:: python

    def test_feature(mocker):
        ret = [mocker.Mock(return_value=True), mocker.Mock(return_value=True)]
        mocker.patch('mylib.func', side_effect=ret)

*New in version 0.5*

Spy
---

*New in version 0.6*

The spy acts exactly like the original method in all cases, except it allows use of `mock`
features with it, like retrieving call count.

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

*New in version 0.6*

The stub is a mock object that accepts any arguments and is useful to test callbacks, for instance.

.. code-block:: python

    def test_stub(mocker):
        def foo(on_something):
            on_something('foo', 'bar')

        stub = mocker.stub()

        foo(stub)
        stub.assert_called_once_with('foo', 'bar')

Note
----

Prior to version ``0.4.0``, the ``mocker`` fixture was named ``mock``.
This was changed because naming the fixture ``mock`` conflicts with the
actual ``mock`` module, which made using it awkward when access to both the
module and the plugin were required within a test.

The old fixture ``mock`` still works, but its use is discouraged and will be
removed in version ``1.0``.

Requirements
============

* Python 2.6+, Python 3.2+
* pytest
* mock (for Python < 3.3)


Install
=======

Install using `pip <http://pip-installer.org/>`_:

.. code-block:: console
    
    $ pip install pytest-mock

Changelog
=========

Please consult `releases <https://github.com/pytest-dev/pytest-mock/releases>`_.
        
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
