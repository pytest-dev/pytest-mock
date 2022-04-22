=======
Remarks
=======

Type annotations
----------------

``pytest-mock`` is fully type annotated, letting users use static type checkers to
test their code.

The ``mocker`` fixture returns ``pytest_mock.MockerFixture`` which can be used
to annotate test functions:

.. code-block:: python

    from pytest_mock import MockerFixture

    def test_foo(mocker: MockerFixture) -> None:
        ...

The type annotations have been checked with ``mypy``, which is the only
type checker supported at the moment; other type-checkers might work
but are not currently tested.


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

An alternative is to use ``contextlib.ExitStack`` to stack the context managers in a single level of indentation
to improve the flow of the test:

.. code-block:: python

    import contextlib
    import mock

    def test_unix_fs():
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch('os.remove'))
            UnixFS.rm('file')
            os.remove.assert_called_once_with('file')

            stack.enter_context(mock.patch('os.listdir'))
            assert UnixFS.ls('dir') == expected
            # ...

            stack.enter_context(mock.patch('shutil.copy'))
            UnixFS.cp('src', 'dst')
            # ...

But this is arguably a little more complex than using ``pytest-mock``.

Usage as context manager
------------------------

Although mocker's API is intentionally the same as ``mock.patch``'s, its use
as context manager and function decorator is **not** supported through the
fixture:

.. code-block:: python

    def test_context_manager(mocker):
        a = A()
        with mocker.patch.object(a, 'doIt', return_value=True, autospec=True):  # DO NOT DO THIS
            assert a.doIt() == True

The purpose of this plugin is to make the use of context managers and
function decorators for mocking unnecessary, so it will emit a warning when used as such.

If you really intend to mock a context manager, ``mocker.patch.context_manager`` exists
which won't issue the above warning.
