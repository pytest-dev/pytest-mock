import builtins
import unittest.mock
from typing import cast, overload, Generator, Mapping, Iterable, Tuple, TypeVar
from typing import Any
from typing import Callable
from typing import Dict
from typing import List

from typing import Optional
from typing import Union


import asyncio
import functools
import inspect

import pytest

_T = TypeVar("_T")


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
            _get_mock_module._module = unittest.mock

    return _get_mock_module._module


class MockerFixture:
    """
    Fixture that provides the same interface to functions in the mock module,
    ensuring that they are uninstalled at the end of each test.
    """

    def __init__(self, config: Any) -> None:
        self._patches = []  # type: List[Any]
        self._mocks = []  # type: List[Any]
        self.mock_module = mock_module = _get_mock_module(config)
        self.patch = self._Patcher(
            self._patches, self._mocks, mock_module
        )  # type: MockerFixture._Patcher
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
        if hasattr(mock_module, "seal"):
            self.seal = mock_module.seal

    def resetall(self) -> None:
        """Call reset_mock() on all patchers started by this fixture."""
        for m in self._mocks:
            m.reset_mock()

    def stopall(self) -> None:
        """
        Stop all patchers started by this fixture. Can be safely called multiple
        times.
        """
        for p in reversed(self._patches):
            p.stop()
        self._patches[:] = []
        self._mocks[:] = []

    def spy(self, obj: object, name: str) -> unittest.mock.MagicMock:
        """
        Create a spy of method. It will run method normally, but it is now
        possible to use `mock` call features with it, like call count.

        :param object obj: An object.
        :param unicode name: A method in object.
        :rtype: unittest.mock.MagicMock
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
                value = obj.__getattribute__(obj, name)  # type:ignore
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

    def stub(self, name: Optional[str] = None) -> unittest.mock.MagicMock:
        """
        Create a stub method. It accepts any arguments. Ideal to register to
        callbacks in tests.

        :param name: the constructed stub's name as used in repr
        :rtype: unittest.mock.MagicMock
        :return: Stub object.
        """
        return cast(
            unittest.mock.MagicMock,
            self.mock_module.MagicMock(spec=lambda *args, **kwargs: None, name=name),
        )

    class _Patcher:
        """
        Object to provide the same interface as mock.patch, mock.patch.object,
        etc. We need this indirection to keep the same API of the mock package.
        """

        DEFAULT = object()

        def __init__(self, patches, mocks, mock_module):
            self._patches = patches
            self._mocks = mocks
            self.mock_module = mock_module

        def _start_patch(
            self, mock_func: Any, *args: Any, **kwargs: Any
        ) -> unittest.mock.MagicMock:
            """Patches something by calling the given function from the mock
            module, registering the patch to stop it later and returns the
            mock object resulting from the mock call.
            """
            p = mock_func(*args, **kwargs)
            mocked = p.start()  # type: unittest.mock.MagicMock
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

        def object(
            self,
            target: object,
            attribute: str,
            new: object = DEFAULT,
            spec: Optional[object] = None,
            create: bool = False,
            spec_set: Optional[object] = None,
            autospec: Optional[object] = None,
            new_callable: object = None,
            **kwargs: Any
        ) -> unittest.mock.MagicMock:
            """API to mock.patch.object"""
            if new is self.DEFAULT:
                new = self.mock_module.DEFAULT
            return self._start_patch(
                self.mock_module.patch.object,
                target,
                attribute,
                new=new,
                spec=spec,
                create=create,
                spec_set=spec_set,
                autospec=autospec,
                new_callable=new_callable,
                **kwargs
            )

        def multiple(
            self,
            target: builtins.object,
            spec: Optional[builtins.object] = None,
            create: bool = False,
            spec_set: Optional[builtins.object] = None,
            autospec: Optional[builtins.object] = None,
            new_callable: Optional[builtins.object] = None,
            **kwargs: Any
        ) -> Dict[str, unittest.mock.MagicMock]:
            """API to mock.patch.multiple"""
            return self._start_patch(
                self.mock_module.patch.multiple,
                target,
                spec=spec,
                create=create,
                spec_set=spec_set,
                autospec=autospec,
                new_callable=new_callable,
                **kwargs
            )

        def dict(
            self,
            in_dict: Mapping[Any, Any],
            values: Union[Mapping[Any, Any], Iterable[Tuple[Any, Any]]] = (),
            clear: bool = False,
            **kwargs: Any
        ) -> Any:
            """API to mock.patch.dict"""
            return self._start_patch(
                self.mock_module.patch.dict,
                in_dict,
                values=values,
                clear=clear,
                **kwargs
            )

        @overload
        def __call__(
            self,
            target: str,
            new: None = ...,
            spec: Optional[builtins.object] = ...,
            create: bool = ...,
            spec_set: Optional[builtins.object] = ...,
            autospec: Optional[builtins.object] = ...,
            new_callable: None = ...,
            **kwargs: Any
        ) -> unittest.mock.MagicMock:
            ...

        @overload
        def __call__(
            self,
            target: str,
            new: _T,
            spec: Optional[builtins.object] = ...,
            create: bool = ...,
            spec_set: Optional[builtins.object] = ...,
            autospec: Optional[builtins.object] = ...,
            new_callable: None = ...,
            **kwargs: Any
        ) -> _T:
            ...

        @overload
        def __call__(
            self,
            target: str,
            new: None,
            spec: Optional[builtins.object],
            create: bool,
            spec_set: Optional[builtins.object],
            autospec: Optional[builtins.object],
            new_callable: Callable[[], _T],
            **kwargs: Any
        ) -> _T:
            ...

        @overload
        def __call__(
            self,
            target: str,
            new: None = ...,
            spec: Optional[builtins.object] = ...,
            create: bool = ...,
            spec_set: Optional[builtins.object] = ...,
            autospec: Optional[builtins.object] = ...,
            *,
            new_callable: Callable[[], _T],
            **kwargs: Any
        ) -> _T:
            ...

        def __call__(
            self,
            target: str,
            new: builtins.object = DEFAULT,
            spec: Optional[builtins.object] = None,
            create: bool = False,
            spec_set: Optional[builtins.object] = None,
            autospec: Optional[builtins.object] = None,
            new_callable: Optional[Callable[[], Any]] = None,
            **kwargs: Any
        ) -> Any:
            """API to mock.patch"""
            if new is self.DEFAULT:
                new = self.mock_module.DEFAULT
            return self._start_patch(
                self.mock_module.patch,
                target,
                new=new,
                spec=spec,
                create=create,
                spec_set=spec_set,
                autospec=autospec,
                new_callable=new_callable,
                **kwargs
            )


def _mocker(pytestconfig: Any) -> Generator[MockerFixture, None, None]:
    """
    Return an object that has the same interface to the `mock` module, but
    takes care of automatically undoing all patches after each test method.
    """
    result = MockerFixture(pytestconfig)
    yield result
    result.stopall()


mocker = pytest.fixture()(_mocker)  # default scope is function
class_mocker = pytest.fixture(scope="class")(_mocker)
module_mocker = pytest.fixture(scope="module")(_mocker)
package_mocker = pytest.fixture(scope="package")(_mocker)
session_mocker = pytest.fixture(scope="session")(_mocker)


_mock_module_patches = []  # type: List[Any]
_mock_module_originals = {}  # type: Dict[str, Any]


def assert_wrapper(
    __wrapped_mock_method__: Callable[..., Any], *args: Any, **kwargs: Any
) -> None:
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
                except AssertionError as e_args:
                    introspection += "\nArgs:\n" + str(e_args)
                try:
                    assert actual_kwargs == kwargs
                except AssertionError as e_kwargs:
                    introspection += "\nKwargs:\n" + str(e_kwargs)
                if introspection:
                    msg += "\n\npytest introspection follows:\n" + introspection
        e = AssertionError(msg)
        e._mock_introspection_applied = True  # type:ignore[attr-defined]
        raise e


def wrap_assert_not_called(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_not_called"], *args, **kwargs)


def wrap_assert_called_with(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_called_with"], *args, **kwargs)


def wrap_assert_called_once(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_called_once"], *args, **kwargs)


def wrap_assert_called_once_with(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_called_once_with"], *args, **kwargs)


def wrap_assert_has_calls(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_has_calls"], *args, **kwargs)


def wrap_assert_any_call(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_any_call"], *args, **kwargs)


def wrap_assert_called(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_called"], *args, **kwargs)


def wrap_assert_not_awaited(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_not_awaited"], *args, **kwargs)


def wrap_assert_awaited_with(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_awaited_with"], *args, **kwargs)


def wrap_assert_awaited_once(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_awaited_once"], *args, **kwargs)


def wrap_assert_awaited_once_with(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_awaited_once_with"], *args, **kwargs)


def wrap_assert_has_awaits(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_has_awaits"], *args, **kwargs)


def wrap_assert_any_await(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_any_await"], *args, **kwargs)


def wrap_assert_awaited(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_awaited"], *args, **kwargs)


def wrap_assert_methods(config: Any) -> None:
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

    config.add_cleanup(unwrap_assert_methods)


def unwrap_assert_methods() -> None:
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


def pytest_addoption(parser: Any) -> None:
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


def parse_ini_boolean(value: Union[bool, str]) -> bool:
    if isinstance(value, bool):
        return value
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    raise ValueError("unknown string for bool: %r" % value)


def pytest_configure(config: Any) -> None:
    tb = config.getoption("--tb", default="auto")
    if (
        parse_ini_boolean(config.getini("mock_traceback_monkeypatch"))
        and tb != "native"
    ):
        wrap_assert_methods(config)
