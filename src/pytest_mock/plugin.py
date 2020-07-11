import asyncio
import functools
import inspect

import pytest

from ._version import version

__version__ = version


def _get_mock_module(config):
    """
    Import and return the actual "mock" module. By default this is
    "unittest.mock", but the user can force to always use "mock" using
    the mock_use_standalone_module ini option.
    """
    if not hasattr(_get_mock_module, "_module"):
        use_standalone_module = parse_ini_boolean(
            config.getini("mock_use_standalone_module")
        )
        if use_standalone_module:
            import mock

            _get_mock_module._module = mock
        else:
            import unittest.mock

            _get_mock_module._module = unittest.mock

    return _get_mock_module._module


class MockFixture:
    """
    Fixture that provides the same interface to functions in the mock module,
    ensuring that they are uninstalled at the end of each test.
    """

    def __init__(self, config):
        self._patches = []  # list of mock._patch objects
        self._mocks = []  # list of MagicMock objects
        self.mock_module = mock_module = _get_mock_module(config)
        self.patch = self._Patcher(self._patches, self._mocks, mock_module)
        # aliases for convenience
        self.Mock = mock_module.Mock
        self.MagicMock = mock_module.MagicMock
        self.NonCallableMock = mock_module.NonCallableMock
        self.PropertyMock = mock_module.PropertyMock
        if hasattr(mock_module, "AsyncMock"):
            self.AsyncMock = mock_module.AsyncMock
        self.call = mock_module.call
        self.ANY = mock_module.ANY
        self.DEFAULT = mock_module.DEFAULT
        self.create_autospec = mock_module.create_autospec
        self.sentinel = mock_module.sentinel
        self.mock_open = mock_module.mock_open

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

        def wrapper(*args, **kwargs):
            spy_obj.spy_return = None
            spy_obj.spy_exception = None
            try:
                r = method(*args, **kwargs)
            except Exception as e:
                spy_obj.spy_exception = e
                raise
            else:
                spy_obj.spy_return = r
            return r

        async def async_wrapper(*args, **kwargs):
            spy_obj.spy_return = None
            spy_obj.spy_exception = None
            try:
                r = await method(*args, **kwargs)
            except Exception as e:
                spy_obj.spy_exception = e
                raise
            else:
                spy_obj.spy_return = r
            return r

        if asyncio.iscoroutinefunction(method):
            wrapped = functools.update_wrapper(async_wrapper, method)
        else:
            wrapped = functools.update_wrapper(wrapper, method)

        spy_obj = self.patch.object(obj, name, side_effect=wrapped, autospec=autospec)
        spy_obj.spy_return = None
        spy_obj.spy_exception = None
        return spy_obj

    def stub(self, name=None):
        """
        Creates a stub method. It accepts any arguments. Ideal to register to
        callbacks in tests.

        :param name: the constructed stub's name as used in repr
        :rtype: mock.MagicMock
        :return: Stub object.
        """
        return self.mock_module.MagicMock(spec=lambda *args, **kwargs: None, name=name)

    class _Patcher:
        """
        Object to provide the same interface as mock.patch, mock.patch.object,
        etc. We need this indirection to keep the same API of the mock package.
        """

        def __init__(self, patches, mocks, mock_module):
            self._patches = patches
            self._mocks = mocks
            self.mock_module = mock_module

        def _start_patch(self, mock_func, *args, **kwargs):
            """Patches something by calling the given function from the mock
            module, registering the patch to stop it later and returns the
            mock object resulting from the mock call.
            """
            p = mock_func(*args, **kwargs)
            mocked = p.start()
            self._patches.append(p)
            if hasattr(mocked, "reset_mock"):
                self._mocks.append(mocked)
                # check if `mocked` is actually a mock object, as depending on autospec or target
                # parameters `mocked` can be anything
                if hasattr(mocked, "__enter__"):
                    mocked.__enter__.side_effect = ValueError(
                        "Using mocker in a with context is not supported. "
                        "https://github.com/pytest-dev/pytest-mock#note-about-usage-as-context-manager"
                    )
            return mocked

        def object(self, *args, **kwargs):
            """API to mock.patch.object"""
            return self._start_patch(self.mock_module.patch.object, *args, **kwargs)

        def multiple(self, *args, **kwargs):
            """API to mock.patch.multiple"""
            return self._start_patch(self.mock_module.patch.multiple, *args, **kwargs)

        def dict(self, *args, **kwargs):
            """API to mock.patch.dict"""
            return self._start_patch(self.mock_module.patch.dict, *args, **kwargs)

        def __call__(self, *args, **kwargs):
            """API to mock.patch"""
            return self._start_patch(self.mock_module.patch, *args, **kwargs)


def _mocker(pytestconfig):
    """
    return an object that has the same interface to the `mock` module, but
    takes care of automatically undoing all patches after each test method.
    """
    result = MockFixture(pytestconfig)
    yield result
    result.stopall()


mocker = pytest.yield_fixture()(_mocker)  # default scope is function
class_mocker = pytest.yield_fixture(scope="class")(_mocker)
module_mocker = pytest.yield_fixture(scope="module")(_mocker)
package_mocker = pytest.yield_fixture(scope="package")(_mocker)
session_mocker = pytest.yield_fixture(scope="session")(_mocker)


_mock_module_patches = []
_mock_module_originals = {}


def assert_wrapper(__wrapped_mock_method__, *args, **kwargs):
    __tracebackhide__ = True
    try:
        __wrapped_mock_method__(*args, **kwargs)
        return
    except AssertionError as e:
        if getattr(e, "_mock_introspection_applied", 0):
            msg = str(e)
        else:
            __mock_self = args[0]
            msg = str(e)
            if __mock_self.call_args is not None:
                actual_args, actual_kwargs = __mock_self.call_args
                introspection = ""
                try:
                    assert actual_args == args[1:]
                except AssertionError as e:
                    introspection += "\nArgs:\n" + str(e)
                try:
                    assert actual_kwargs == kwargs
                except AssertionError as e:
                    introspection += "\nKwargs:\n" + str(e)

                if introspection:
                    msg += "\n\npytest introspection follows:\n" + introspection
    e = AssertionError(msg)
    e._mock_introspection_applied = True
    raise e


def wrap_assert_not_called(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_not_called"], *args, **kwargs)


def wrap_assert_called_with(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_called_with"], *args, **kwargs)


def wrap_assert_called_once(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_called_once"], *args, **kwargs)


def wrap_assert_called_once_with(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_called_once_with"], *args, **kwargs)


def wrap_assert_has_calls(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_has_calls"], *args, **kwargs)


def wrap_assert_any_call(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_any_call"], *args, **kwargs)


def wrap_assert_called(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_called"], *args, **kwargs)


def wrap_assert_not_awaited(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_not_awaited"], *args, **kwargs)


def wrap_assert_awaited_with(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_awaited_with"], *args, **kwargs)


def wrap_assert_awaited_once(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_awaited_once"], *args, **kwargs)


def wrap_assert_awaited_once_with(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_awaited_once_with"], *args, **kwargs)


def wrap_assert_has_awaits(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_has_awaits"], *args, **kwargs)


def wrap_assert_any_await(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_any_await"], *args, **kwargs)


def wrap_assert_awaited(*args, **kwargs):
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_awaited"], *args, **kwargs)


def wrap_assert_methods(config):
    """
    Wrap assert methods of mock module so we can hide their traceback and
    add introspection information to specified argument asserts.
    """
    # Make sure we only do this once
    if _mock_module_originals:
        return

    mock_module = _get_mock_module(config)

    wrappers = {
        "assert_called": wrap_assert_called,
        "assert_called_once": wrap_assert_called_once,
        "assert_called_with": wrap_assert_called_with,
        "assert_called_once_with": wrap_assert_called_once_with,
        "assert_any_call": wrap_assert_any_call,
        "assert_has_calls": wrap_assert_has_calls,
        "assert_not_called": wrap_assert_not_called,
    }
    for method, wrapper in wrappers.items():
        try:
            original = getattr(mock_module.NonCallableMock, method)
        except AttributeError:  # pragma: no cover
            continue
        _mock_module_originals[method] = original
        patcher = mock_module.patch.object(mock_module.NonCallableMock, method, wrapper)
        patcher.start()
        _mock_module_patches.append(patcher)

    if hasattr(mock_module, "AsyncMock"):
        async_wrappers = {
            "assert_awaited": wrap_assert_awaited,
            "assert_awaited_once": wrap_assert_awaited_once,
            "assert_awaited_with": wrap_assert_awaited_with,
            "assert_awaited_once_with": wrap_assert_awaited_once_with,
            "assert_any_await": wrap_assert_any_await,
            "assert_has_awaits": wrap_assert_has_awaits,
            "assert_not_awaited": wrap_assert_not_awaited,
        }
        for method, wrapper in async_wrappers.items():
            try:
                original = getattr(mock_module.AsyncMock, method)
            except AttributeError:  # pragma: no cover
                continue
            _mock_module_originals[method] = original
            patcher = mock_module.patch.object(mock_module.AsyncMock, method, wrapper)
            patcher.start()
            _mock_module_patches.append(patcher)

    if hasattr(config, "add_cleanup"):
        add_cleanup = config.add_cleanup
    else:
        # pytest 2.7 compatibility
        add_cleanup = config._cleanup.append
    add_cleanup(unwrap_assert_methods)


def unwrap_assert_methods():
    for patcher in _mock_module_patches:
        try:
            patcher.stop()
        except RuntimeError as e:
            # a patcher might have been stopped by user code (#137)
            # so we need to catch this error here and ignore it;
            # unfortunately there's no public API to check if a patch
            # has been started, so catching the error it is
            if str(e) == "stop called on unstarted patcher":
                pass
            else:
                raise
    _mock_module_patches[:] = []
    _mock_module_originals.clear()


def pytest_addoption(parser):
    parser.addini(
        "mock_traceback_monkeypatch",
        "Monkeypatch the mock library to improve reporting of the "
        "assert_called_... methods",
        default=True,
    )
    parser.addini(
        "mock_use_standalone_module",
        'Use standalone "mock" (from PyPI) instead of builtin "unittest.mock" '
        "on Python 3",
        default=False,
    )


def parse_ini_boolean(value):
    if value in (True, False):
        return value
    try:
        return {"true": True, "false": False}[value.lower()]
    except KeyError:
        raise ValueError("unknown string for bool: %r" % value)


def pytest_configure(config):
    tb = config.getoption("--tb", default="auto")
    if (
        parse_ini_boolean(config.getini("mock_traceback_monkeypatch"))
        and tb != "native"
    ):
        wrap_assert_methods(config)
