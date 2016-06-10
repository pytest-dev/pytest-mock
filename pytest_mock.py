import inspect
import sys

import pytest

try:
    import mock as mock_module
except ImportError:
    import unittest.mock as mock_module

version = '1.1'


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


def assert_wrapper(__wrapped_mock_method__, *args, **kwargs):
    __tracebackhide__ = True
    try:
        __wrapped_mock_method__(*args, **kwargs)
    except AssertionError as e:
        __mock_self = args[0]
        if __mock_self.call_args is not None:
            actual_args, actual_kwargs = __mock_self.call_args
            assert actual_args == args[1:]
            assert actual_kwargs == kwargs
        raise AssertionError(*e.args)


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
