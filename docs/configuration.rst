=============
Configuration
=============

Use standalone "mock" package
-----------------------------

Python 3 users might want to use a newest version of the ``mock`` package as published on PyPI
than the one that comes with the Python distribution.

.. code-block:: ini

    [pytest]
    mock_use_standalone_module = true

This will force the plugin to import ``mock`` instead of the ``unittest.mock`` module bundled with
Python 3.4+.



Improved reporting of mock call assertion errors
------------------------------------------------

This plugin monkeypatches the mock library to improve pytest output for failures
of mock call assertions like ``Mock.assert_called_with()`` by hiding internal traceback
entries from the ``mock`` module.

It also adds introspection information on differing call arguments when
``assert_called_with``, ``assert_called_once_with``, ``assert_awaited_with``,
``assert_awaited_once_with``, ``assert_has_calls`` or ``assert_has_awaits`` fail
because of the arguments of the calls. This feature catches the `AssertionError`
raised in the method, and uses pytest's own `advanced assertions`_ to return a
better diff::

    mocker = <pytest_mock.plugin.MockerFixture object at 0x000001D7EBD26270>

        def test(mocker):
            m = mocker.Mock()
            m('fo')
    >       m.assert_called_once_with('', bar=4)
    E       AssertionError: expected call not found.
    E       Expected: mock('', bar=4)
    E         Actual: mock('fo')
    E
    E       pytest introspection follows:
    E
    E       Args:
    E       assert ('fo',) == ('',)
    E
    E         At index 0 diff: 'fo' != ''
    E         Use -v to get more diff
    E       Kwargs:
    E       assert {} == {'bar': 4}
    E
    E         Right contains 1 more item:
    E         {'bar': 4}
    E         Use -v to get more diff

    test_foo.py:4: AssertionError

This is useful when asserting mock calls with many/nested arguments and trying
to quickly see the difference.

The other assertions, such as ``assert_called_once``, ``assert_not_called`` or
``assert_any_call``, fail because of how many times the mock was called, or
because none of its calls matches, so there is no single call to compare with the
expected arguments: the mock's own message, which lists the calls, is shown
instead.

The introspection requires pytest's assertion rewriting, so it is not shown with
``--assert=plain``.

This feature is probably safe, but if you encounter any problems it can be disabled in
your ``pytest.ini`` file:

.. code-block:: ini

    [pytest]
    mock_traceback_monkeypatch = false

Note that this feature is automatically disabled with the ``--tb=native`` option. The underlying
mechanism used to suppress traceback entries from ``mock`` module does not work with that option
anyway plus it generates confusing messages on Python 3.5 due to exception chaining

.. _advanced assertions: https://docs.pytest.org/en/stable/assert.html
