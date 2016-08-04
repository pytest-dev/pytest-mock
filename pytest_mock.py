from pprint import pformat
import inspect

import pytest
import py

try:
    import mock as mock_module
except ImportError:
    import unittest.mock as mock_module

version = '1.2'


class MockFixture(object):
    """
    Fixture that provides the same interface to functions in the mock module,
    ensuring that they are uninstalled at the end of each test.
    """

    Mock = mock_module.Mock
    MagicMock = mock_module.MagicMock
    PropertyMock = mock_module.PropertyMock
    call = mock_module.call
    ANY = mock_module.ANY
    sentinel = mock_module.sentinel

    def __init__(self):
        self._patches = []  # list of mock._patch objects
        self._mocks = []  # list of MagicMock objects
        self.patch = self._Patcher(self._patches, self._mocks)

    def resetall(self):
        """
        Call reset_mock() on all patchers started by this fixture.
        """
        for m in self._mocks:
            m.reset_mock()

    def stopall(self):
        """
        Stop all patchers started by this fixture. Can be safely called multiple
        times.
        """
        for p in reversed(self._patches):
            p.stop()
        self._patches[:] = []
        self._mocks[:] = []

    def spy(self, obj, name):
        """
        Creates a spy of method. It will run method normally, but it is now
        possible to use `mock` call features with it, like call count.

        :param object obj: An object.
        :param unicode name: A method in object.
        :rtype: mock.MagicMock
        :return: Spy object.
        """
        method = getattr(obj, name)

        autospec = inspect.ismethod(method) or inspect.isfunction(method)
        # Can't use autospec classmethod or staticmethod objects
        # see: https://bugs.python.org/issue23078
        if inspect.isclass(obj):
            # Bypass class descriptor:
            # http://stackoverflow.com/questions/14187973/python3-check-if-method-is-static
            try:
                value = obj.__getattribute__(obj, name)
            except AttributeError:
                pass
            else:
                if isinstance(value, (classmethod, staticmethod)):
                    autospec = False

        result = self.patch.object(obj, name, side_effect=method,
                                   autospec=autospec)
        return result

    def stub(self, name=None):
        """
        Creates a stub method. It accepts any arguments. Ideal to register to
        callbacks in tests.

        :param name: the constructed stub's name as used in repr
        :rtype: mock.MagicMock
        :return: Stub object.
        """
        return mock_module.MagicMock(spec=lambda *args, **kwargs: None, name=name)

    class _Patcher(object):
        """
        Object to provide the same interface as mock.patch, mock.patch.object,
        etc. We need this indirection to keep the same API of the mock package.
        """

        def __init__(self, patches, mocks):
            self._patches = patches
            self._mocks = mocks

        def _start_patch(self, mock_func, *args, **kwargs):
            """Patches something by calling the given function from the mock
            module, registering the patch to stop it later and returns the
            mock object resulting from the mock call.
            """
            p = mock_func(*args, **kwargs)
            mocked = p.start()
            self._patches.append(p)
            self._mocks.append(mocked)
            return mocked

        def object(self, *args, **kwargs):
            """API to mock.patch.object"""
            return self._start_patch(mock_module.patch.object, *args, **kwargs)

        def multiple(self, *args, **kwargs):
            """API to mock.patch.multiple"""
            return self._start_patch(mock_module.patch.multiple, *args,
                                     **kwargs)

        def dict(self, *args, **kwargs):
            """API to mock.patch.dict"""
            return self._start_patch(mock_module.patch.dict, *args, **kwargs)

        def __call__(self, *args, **kwargs):
            """API to mock.patch"""
            return self._start_patch(mock_module.patch, *args, **kwargs)


@pytest.yield_fixture
def mocker():
    """
    return an object that has the same interface to the `mock` module, but
    takes care of automatically undoing all patches after each test method.
    """
    result = MockFixture()
    yield result
    result.stopall()


@pytest.fixture
def mock(mocker):
    """
    Same as "mocker", but kept only for backward compatibility.
    """
    import warnings
    warnings.warn('"mock" fixture has been deprecated, use "mocker" instead',
                  DeprecationWarning)
    return mocker


_mock_module_patches = []
_mock_module_originals = {}


DETAILED_ASSERTION = """{original!s}

... pytest introspection follows:
{detailed!s}
"""
FULL_ANY_CALLS_DIFF = "assert {call} in {calls_list}"


def pytest_assertrepr_compare(config, op, left, right):
    patch_enabled = config.getini('mock_traceback_monkeypatch')
    if not patch_enabled:
        return

    if hasattr(mock_module, 'mock'):
        call_class = mock_module.mock._Call
        call_list_class = mock_module.mock._CallList
    else:
        call_class = mock_module._Call
        call_list_class = mock_module._CallList

    verbose = config.getoption('verbose')
    u = py.builtin._totext

    def safe_unpack_args(call):
        try:
            args, kwargs = call
        except ValueError:
            name, args, kwargs = call
        return args, kwargs

    def get_summary():
        width = 80 - 15 - len(op) - 2  # 15 chars indentation, 1 space around op
        left_repr = py.io.saferepr(left, maxsize=int(width / 2))
        right_repr = py.io.saferepr(right, maxsize=width - len(left_repr))

        def ecu(s):
            try:
                return u(s, 'utf-8', 'replace')
            except TypeError:
                return s
        return u('%s %s %s') % (ecu(left_repr), op, ecu(right_repr))

    summary = get_summary()
    if not verbose:
        return [summary, u('Use -v to get the full diff')]

    from _pytest.assertion.util import assertrepr_compare
    if isinstance(left, call_class) and isinstance(right, call_class) and op == '==':
        largs, lkwargs = safe_unpack_args(left)
        rargs, rkwargs = safe_unpack_args(right)
        explanation = ['Full diff:']

        arg_expl = assertrepr_compare(config, op, largs, rargs)
        if arg_expl:
            explanation += ['positional arguments differ;'] + arg_expl
        kwarg_expl = assertrepr_compare(config, op, lkwargs, rkwargs)
        if kwarg_expl:
            explanation += ['keyword arguments differ;'] + kwarg_expl

        return [summary] + explanation

    if (isinstance(left, tuple) and
            isinstance(right, call_list_class) and op == "in"):
        return [
            summary, u('Full diff:'),
            FULL_ANY_CALLS_DIFF.format(call=left, calls_list=pformat(right))
        ]


def assert_wrapper(__wrapped_mock_method__, *args, **kwargs):
    __tracebackhide__ = True
    try:
        __wrapped_mock_method__(*args, **kwargs)
    except AssertionError as e:
        __mock_self = args[0]  # the mock instance
        assert_call = mock_module.call(*args[1:], **kwargs)
        if __mock_self.call_args is not None:
            try:
                if __wrapped_mock_method__.__name__ == 'assert_any_call':
                    assert assert_call in __mock_self.call_args_list
                else:
                    # compare tuples for deep pytest iterable diff
                    assert assert_call == __mock_self.call_args
            except AssertionError as diff:
                # raise a new detailed exception, appending to existing
                msg = DETAILED_ASSERTION.format(original=e, detailed=diff)
                raise AssertionError(msg.encode().decode('unicode_escape'))
        raise e


def wrap_assert_not_called(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_not_called"],
                   *args, **kwargs)


def wrap_assert_called_with(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_called_with"],
                   *args, **kwargs)


def wrap_assert_called_once_with(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_called_once_with"],
                   *args, **kwargs)


def wrap_assert_has_calls(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_has_calls"],
                   *args, **kwargs)


def wrap_assert_any_call(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_any_call"],
                   *args, **kwargs)


def wrap_assert_methods(config):
    """
    Wrap assert methods of mock module so we can hide their traceback and
    add introspection information to specified argument asserts.
    """
    # Make sure we only do this once
    if _mock_module_originals:
        return

    wrappers = {
        'assert_not_called': wrap_assert_not_called,
        'assert_called_with': wrap_assert_called_with,
        'assert_called_once_with': wrap_assert_called_once_with,
        'assert_has_calls': wrap_assert_has_calls,
        'assert_any_call': wrap_assert_any_call,
    }
    for method, wrapper in wrappers.items():
        try:
            original = getattr(mock_module.NonCallableMock, method)
        except AttributeError:
            continue
        _mock_module_originals[method] = original
        patcher = mock_module.patch.object(
            mock_module.NonCallableMock, method, wrapper)
        patcher.start()
        _mock_module_patches.append(patcher)

    if hasattr(config, 'add_cleanup'):
        add_cleanup = config.add_cleanup
    else:
        # pytest 2.7 compatibility
        add_cleanup = config._cleanup.append
    add_cleanup(unwrap_assert_methods)


def unwrap_assert_methods():
    for patcher in _mock_module_patches:
        patcher.stop()
    _mock_module_patches[:] = []
    _mock_module_originals.clear()


def pytest_addoption(parser):
    parser.addini('mock_traceback_monkeypatch',
                  'Monkeypatch the mock library to improve reporting of the '
                  'assert_called_... methods',
                  default=True)


def parse_ini_boolean(value):
    if value in (True, False):
        return value
    try:
        return {'true': True, 'false': False}[value.lower()]
    except KeyError:
        raise ValueError('unknown string for bool: %r' % value)


def pytest_configure(config):
    tb = config.getoption('--tb')
    if parse_ini_boolean(config.getini('mock_traceback_monkeypatch')) and tb != 'native':
        wrap_assert_methods(config)
