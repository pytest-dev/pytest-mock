=====
Usage
=====

The ``mocker`` fixture has the same API as
`mock.patch <https://docs.python.org/3/library/unittest.mock.html#patch>`_,
supporting the same arguments:

.. code-block:: python

    def test_foo(mocker):
        # all valid calls
        mocker.patch('os.remove')
        mocker.patch.object(os, 'listdir', autospec=True)
        mocked_isfile = mocker.patch('os.path.isfile')

The supported methods are:

* `mocker.patch <https://docs.python.org/3/library/unittest.mock.html#patch>`_
* `mocker.patch.object <https://docs.python.org/3/library/unittest.mock.html#patch-object>`_
* `mocker.patch.multiple <https://docs.python.org/3/library/unittest.mock.html#patch-multiple>`_
* `mocker.patch.dict <https://docs.python.org/3/library/unittest.mock.html#patch-dict>`_
* `mocker.stopall <https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch.stopall>`_
* `mocker.stop <https://docs.python.org/3/library/unittest.mock.html#patch-methods-start-and-stop>`_
* ``mocker.resetall()``: calls `reset_mock() <https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.reset_mock>`_ in all mocked objects up to this point.

Also, as a convenience, these names from the ``mock`` module are accessible directly from ``mocker``:

* `Mock <https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock>`_
* `MagicMock <https://docs.python.org/3/library/unittest.mock.html#unittest.mock.MagicMock>`_
* `PropertyMock <https://docs.python.org/3/library/unittest.mock.html#unittest.mock.PropertyMock>`_
* `ANY <https://docs.python.org/3/library/unittest.mock.html#any>`_
* `DEFAULT <https://docs.python.org/3/library/unittest.mock.html#default>`_
* `call <https://docs.python.org/3/library/unittest.mock.html#call>`_
* `sentinel <https://docs.python.org/3/library/unittest.mock.html#sentinel>`_
* `mock_open <https://docs.python.org/3/library/unittest.mock.html#mock-open>`_
* `seal <https://docs.python.org/3/library/unittest.mock.html#unittest.mock.seal>`_

It is also possible to use mocking functionality from fixtures of other scopes using
the appropriate fixture:

* ``class_mocker``
* ``module_mocker``
* ``package_mocker``
* ``session_mocker``


Spy
---

The ``mocker.spy`` object acts exactly like the original method in all cases, except the spy
also tracks function/method calls, return values and exceptions raised.

.. code-block:: python

    def test_spy_method(mocker):
        class Foo(object):
            def bar(self, v):
                return v * 2

        foo = Foo()
        spy = mocker.spy(foo, 'bar')
        assert foo.bar(21) == 42

        spy.assert_called_once_with(21)
        assert spy.spy_return == 42

    def test_spy_function(mocker):
        # mymodule declares `myfunction` which just returns 42
        import mymodule

        spy = mocker.spy(mymodule, "myfunction")
        assert mymodule.myfunction() == 42
        assert spy.call_count == 1
        assert spy.spy_return == 42

The object returned by ``mocker.spy`` is a ``MagicMock`` object, so all standard checking functions
are available (like ``assert_called_once_with`` or ``call_count`` in the examples above).

In addition, spy objects contain two extra attributes:

* ``spy_return``: contains the returned value of the spied function.
* ``spy_exception``: contain the last exception value raised by the spied function/method when
  it was last called, or ``None`` if no exception was raised.

Besides functions and normal methods, ``mocker.spy`` also works for class and static methods.

As of version 3.0.0, ``mocker.spy`` also works with ``async def`` functions.

.. note::

    In versions earlier than ``2.0``, the attributes were called ``return_value`` and
    ``side_effect`` respectively, but due to incompatibilities with ``unittest.mock``
    they had to be renamed (see `#175`_ for details).

    .. _#175: https://github.com/pytest-dev/pytest-mock/issues/175

As of version 3.10, spying can be also selectively stopped.

.. code-block:: python

    def test_with_unspy(mocker):
        class Foo:
            def bar(self):
                return 42

        spy = mocker.spy(Foo, "bar")
        foo = Foo()
        assert foo.bar() == 42
        assert spy.call_count == 1
        mocker.stop(spy)
        assert foo.bar() == 42
        assert spy.call_count == 1


``mocker.stop()`` can also be used by ``mocker.patch`` calls.


Stub
----

The stub is a mock object that accepts any arguments and is useful to test callbacks.
It may receive an optional name that is shown in its ``repr``, useful for debugging.

.. code-block:: python

    def test_stub(mocker):
        def foo(on_something):
            on_something('foo', 'bar')

        stub = mocker.stub(name='on_something_stub')

        foo(stub)
        stub.assert_called_once_with('foo', 'bar')

.. seealso::

    ``async_stub`` method, which actually the same as ``stub`` but makes async stub.
