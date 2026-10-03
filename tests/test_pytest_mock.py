import os
import platform
import re
import sys
import warnings
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Iterable
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from pytest_mock import MockerFixture
from pytest_mock import PytestMockWarning
from pytest_mock import SpyType

pytest_plugins = "pytester"


# could not make some of the tests work on PyPy, patches are welcome!
skip_pypy = pytest.mark.skipif(
    platform.python_implementation() == "PyPy", reason="could not make it work on pypy"
)


# Python 3.11.7 changed the output formatting, https://github.com/python/cpython/issues/111019
NEWEST_FORMATTING = sys.version_info >= (3, 11, 7)


def syspath_insert_workaround(request: pytest.FixtureRequest, testdir: Any) -> None:
    if pytest.__version__.split(".")[0] == "6":
        # Avoid testdir.syspathinsert() which requires pkg_resources (setuptools) in
        # pytest 6.2.5; insert directly instead (#169).
        sys.path.insert(0, str(testdir.tmpdir))
        request.addfinalizer(lambda: sys.path.remove(str(testdir.tmpdir)))
    else:
        testdir.syspathinsert()


@pytest.fixture
def needs_assert_rewrite(pytestconfig):
    """
    Fixture which skips requesting test if assertion rewrite is disabled (#102)

    Making this a fixture to avoid accessing pytest's config in the global context.
    """
    option = pytestconfig.getoption("assertmode")
    if option != "rewrite":
        pytest.skip(
            "this test needs assertion rewrite to work but current option "
            f'is "{option}"'
        )


class UnixFS:
    """
    Wrapper to os functions to simulate a Unix file system, used for testing
    the mock fixture.
    """

    @classmethod
    def rm(cls, filename):
        os.remove(filename)

    @classmethod
    def ls(cls, path):
        return os.listdir(path)


class AutospecTarget:
    """
    Class that is used for testing create_autospec with child mocks
    """

    def run(self) -> str:
        return "not mocked"


@contextmanager
def assert_traceback() -> Generator[None, None, None]:
    """
    Assert that this file is at the top of the filtered traceback
    """
    try:
        yield
    except AssertionError as e:
        assert e.__traceback__.tb_frame.f_code.co_filename == __file__  # type:ignore
    else:
        raise AssertionError("DID NOT RAISE")


class TestPatch:
    """Patching with ``mocker.patch`` and its variants."""

    @pytest.fixture
    def check_unix_fs_mocked(
        self, tmpdir: Any, mocker: MockerFixture
    ) -> Callable[[Any, Any], None]:
        """
        performs a standard test in a UnixFS, assuming that both `os.remove` and
        `os.listdir` have been mocked previously.
        """

        def check(mocked_rm, mocked_ls):
            assert mocked_rm is os.remove
            assert mocked_ls is os.listdir

            file_name = tmpdir / "foo.txt"
            file_name.ensure()

            UnixFS.rm(str(file_name))
            mocked_rm.assert_called_once_with(str(file_name))
            assert os.path.isfile(str(file_name))

            mocked_ls.return_value = ["bar.txt"]
            assert UnixFS.ls(str(tmpdir)) == ["bar.txt"]
            mocked_ls.assert_called_once_with(str(tmpdir))

            mocker.stopall()

            assert UnixFS.ls(str(tmpdir)) == ["foo.txt"]
            UnixFS.rm(str(file_name))
            assert not os.path.isfile(str(file_name))

        return check

    @staticmethod
    def mock_using_patch_object(mocker: MockerFixture) -> tuple[MagicMock, MagicMock]:
        return mocker.patch.object(os, "remove"), mocker.patch.object(os, "listdir")

    @staticmethod
    def mock_using_patch(mocker: MockerFixture) -> tuple[MagicMock, MagicMock]:
        return mocker.patch("os.remove"), mocker.patch("os.listdir")

    @staticmethod
    def mock_using_patch_multiple(
        mocker: MockerFixture,
    ) -> tuple[MagicMock, MagicMock]:
        r = mocker.patch.multiple("os", remove=mocker.DEFAULT, listdir=mocker.DEFAULT)
        return r["remove"], r["listdir"]

    @pytest.mark.parametrize(
        "mock_fs",
        [mock_using_patch_object, mock_using_patch, mock_using_patch_multiple],
    )
    def test_patches(
        self,
        mock_fs: Any,
        mocker: MockerFixture,
        check_unix_fs_mocked: Callable[[Any, Any], None],
    ) -> None:
        """
        Installs mocks into `os` functions and performs a standard testing of
        mock functionality. We parametrize different mock methods to ensure
        all (intended, at least) mock API is covered.
        """
        # mock it twice on purpose to ensure we unmock it correctly later
        mock_fs(mocker)
        mocked_rm, mocked_ls = mock_fs(mocker)
        check_unix_fs_mocked(mocked_rm, mocked_ls)
        mocker.resetall()
        mocker.stopall()

    def test_dict(self, mocker: MockerFixture) -> None:
        """
        Testing
        :param mock:
        """
        x = {"original": 1}
        mocker.patch.dict(x, values=[("new", 10)], clear=True)
        assert x == {"new": 10}
        mocker.stopall()
        assert x == {"original": 1}

    def test_method_parameter_name(self, mocker: MockerFixture) -> None:
        """Test that our internal code uses uncommon names when wrapping other
        "mock" methods to avoid conflicts with user code (#31).
        """

        class Request:
            @classmethod
            def request(cls, method, args):
                pass

        m = mocker.patch.object(Request, "request")
        Request.request(method="get", args={"type": "application/json"})
        m.assert_called_once_with(method="get", args={"type": "application/json"})


class TestMockerAttributes:
    """Mock helpers re-exported as ``mocker`` attributes."""

    @pytest.mark.parametrize(
        "name",
        [
            "ANY",
            "call",
            "MagicMock",
            "Mock",
            "mock_open",
            "NonCallableMagicMock",
            "NonCallableMock",
            "PropertyMock",
            "sentinel",
            "seal",
        ],
    )
    def test_aliases(self, name: str, pytestconfig: Any) -> None:
        from pytest_mock._util import get_mock_module

        mock_module = get_mock_module(pytestconfig)

        mocker = MockerFixture(pytestconfig)
        assert getattr(mocker, name) is getattr(mock_module, name)


class TestResetAll:
    """``mocker.resetall``."""

    def test_basic(self, mocker: MockerFixture) -> None:
        listdir = mocker.patch("os.listdir", return_value="foo")
        open = mocker.patch("os.open", side_effect=["bar", "baz"])

        mocked_object = mocker.create_autospec(AutospecTarget)
        mocked_object.run.return_value = "mocked"

        assert listdir("/tmp") == "foo"
        assert open("/tmp/foo.txt") == "bar"
        assert mocked_object.run() == "mocked"
        listdir.assert_called_once_with("/tmp")
        open.assert_called_once_with("/tmp/foo.txt")
        mocked_object.run.assert_called_once()

        mocker.resetall()

        assert not listdir.called
        assert not open.called
        assert not mocked_object.called
        assert listdir.return_value == "foo"
        assert list(open.side_effect) == ["baz"]
        assert mocked_object.run.return_value == "mocked"

        mocker.resetall(return_value=True, side_effect=True)

        assert isinstance(listdir.return_value, mocker.Mock)
        assert open.side_effect is None

        assert mocked_object.run.return_value != "mocked"

    def test_non_callable_mock(self, mocker: MockerFixture) -> None:
        """``resetall`` must honour its arguments for non-callable mocks too (#389)."""
        mocked_object = mocker.create_autospec(AutospecTarget, instance=True)
        assert not isinstance(mocked_object, mocker.Mock)
        mocked_object.run.return_value = "mocked"
        mocked_object.run.side_effect = ValueError

        mocker.resetall(return_value=True, side_effect=True)

        assert mocked_object.run.return_value != "mocked"
        assert mocked_object.run.side_effect is None

    def test_patch_dict(self, mocker: MockerFixture) -> None:
        """
        We can call resetall after patching a dict.
        :param mock:
        """
        x = {"original": 1}
        mocker.patch.dict(x, values=[("new", 10)], clear=True)
        assert x == {"new": 10}
        mocker.resetall()
        assert x == {"new": 10}


class TestMockerStub:
    def test_call(self, mocker: MockerFixture) -> None:
        stub = mocker.stub()
        stub("foo", "bar")
        stub.assert_called_once_with("foo", "bar")

    def test_repr_with_no_name(self, mocker: MockerFixture) -> None:
        stub = mocker.stub()
        assert "name" not in repr(stub)

    def test_repr_with_name(self, mocker: MockerFixture) -> None:
        test_name = "funny walk"
        stub = mocker.stub(name=test_name)
        assert f"name={test_name!r}" in repr(stub)

    def __test_failure_message(self, mocker: MockerFixture, **kwargs: Any) -> None:
        expected_name = kwargs.get("name") or "mock"
        if NEWEST_FORMATTING:
            msg = "expected call not found.\nExpected: {0}()\n  Actual: not called."
        else:
            msg = "expected call not found.\nExpected: {0}()\nActual: not called."
        expected_message = msg.format(expected_name)
        stub = mocker.stub(**kwargs)
        with pytest.raises(AssertionError, match=re.escape(expected_message)):
            stub.assert_called_with()

    def test_failure_message_with_no_name(self, mocker: MagicMock) -> None:
        self.__test_failure_message(mocker)

    @pytest.mark.parametrize("name", (None, "", "f", "The Castle of aaarrrrggh"))
    def test_failure_message_with_name(self, mocker: MagicMock, name: str) -> None:
        self.__test_failure_message(mocker, name=name)

    def test_async_stub_type(self, mocker: MockerFixture) -> None:
        assert isinstance(mocker.async_stub(), AsyncMock)


class TestSpy:
    """``mocker.spy``."""

    @staticmethod
    def assert_spy_has_no_return(spy: SpyType) -> None:
        assert spy.spy_return is None
        assert spy.spy_return_iter is None
        assert spy.spy_return_list == []

    def test_instance_method(self, mocker: MockerFixture) -> None:
        class Foo:
            def bar(self, arg):
                return arg * 2

        foo = Foo()
        other = Foo()
        spy = mocker.spy(foo, "bar")
        assert foo.bar(arg=10) == 20
        assert other.bar(arg=10) == 20
        foo.bar.assert_called_once_with(arg=10)  # type:ignore[attr-defined]
        assert foo.bar.spy_return == 20  # type:ignore[attr-defined]
        assert foo.bar.spy_return_iter is None  # type:ignore[attr-defined]
        assert foo.bar.spy_return_list == [20]  # type:ignore[attr-defined]
        spy.assert_called_once_with(arg=10)
        assert spy.spy_return == 20
        assert foo.bar(arg=11) == 22
        assert foo.bar(arg=12) == 24
        assert spy.spy_return == 24
        assert spy.spy_return_iter is None
        assert spy.spy_return_list == [20, 22, 24]

    def test_type(self, mocker: MockerFixture) -> None:
        class Foo:
            def bar(self) -> str:
                return "ok"

        foo = Foo()
        spy: SpyType = mocker.spy(foo, "bar")

        self.assert_spy_has_no_return(spy)
        assert spy.spy_exception is None
        spy.assert_not_called()

        assert foo.bar() == "ok"
        assert spy.spy_return == "ok"
        assert spy.spy_return_list == ["ok"]

    # Ref: https://docs.python.org/3/library/exceptions.html#exception-hierarchy
    @pytest.mark.parametrize(
        "exc_cls",
        (
            BaseException,
            Exception,
            GeneratorExit,  # BaseException
            KeyboardInterrupt,  # BaseException
            RuntimeError,  # regular Exception
            SystemExit,  # BaseException
        ),
    )
    def test_instance_method_exception(
        self,
        exc_cls: type[BaseException],
        mocker: MockerFixture,
    ) -> None:
        class Foo:
            def bar(self, arg):
                raise exc_cls(f"Error with {arg}")

        foo = Foo()
        spy = mocker.spy(foo, "bar")

        expected_calls = []
        for i, v in enumerate([10, 20]):
            with pytest.raises(exc_cls, match=f"Error with {v}"):
                foo.bar(arg=v)

            expected_calls.append(mocker.call(arg=v))
            assert foo.bar.call_args_list == expected_calls  # type:ignore[attr-defined]
            assert str(spy.spy_exception) == f"Error with {v}"

    def test_instance_class_static_method_autospec_true(
        self, mocker: MockerFixture
    ) -> None:
        class Foo:
            def bar(self, arg):
                return arg * 2

            @classmethod
            def baz(cls, arg):
                return arg * 2

            @staticmethod
            def qux(arg):
                return arg * 2

        foo = Foo()
        instance_method_spy = mocker.spy(foo, "bar")
        with pytest.raises(
            AttributeError,
            match="'function' object has no attribute 'fake_assert_method'",
        ):
            instance_method_spy.fake_assert_method(arg=5)

        class_method_spy = mocker.spy(Foo, "baz")
        with pytest.raises(
            AttributeError, match="Mock object has no attribute 'fake_assert_method'"
        ):
            class_method_spy.fake_assert_method(arg=5)

        static_method_spy = mocker.spy(Foo, "qux")
        with pytest.raises(
            AttributeError, match="Mock object has no attribute 'fake_assert_method'"
        ):
            static_method_spy.fake_assert_method(arg=5)

    def test_reset(self, mocker: MockerFixture) -> None:
        class Foo:
            def bar(self, x):
                if x == 0:
                    raise ValueError("invalid x")
                return x * 3

        spy = mocker.spy(Foo, "bar")
        self.assert_spy_has_no_return(spy)
        assert spy.spy_exception is None

        Foo().bar(10)
        assert spy.spy_return == 30
        assert spy.spy_return_iter is None
        assert spy.spy_return_list == [30]
        assert spy.spy_exception is None

        # Testing spy can still be reset (#237).
        mocker.resetall()

        with pytest.raises(ValueError):
            Foo().bar(0)
        self.assert_spy_has_no_return(spy)
        assert str(spy.spy_exception) == "invalid x"

        Foo().bar(15)
        assert spy.spy_return == 45
        assert spy.spy_return_iter is None
        assert spy.spy_return_list == [45]
        assert spy.spy_exception is None

    def test_callable_like(
        self, testdir: Any, mocker: MockerFixture, request: pytest.FixtureRequest
    ) -> None:
        testdir.makepyfile(
            uut="""
            class CallLike(object):
                def __call__(self, x):
                    return x * 2

            call_like = CallLike()
        """
        )
        syspath_insert_workaround(request, testdir)

        uut = __import__("uut")

        spy = mocker.spy(uut, "call_like")
        uut.call_like(10)
        spy.assert_called_once_with(10)
        assert spy.spy_return == 20
        assert spy.spy_return_iter is None
        assert spy.spy_return_list == [20]

    @pytest.mark.asyncio
    async def test_instance_async_method(self, mocker: MockerFixture) -> None:
        class Foo:
            async def bar(self, arg):
                return arg * 2

        foo = Foo()
        spy = mocker.spy(foo, "bar")

        result = await foo.bar(10)

        spy.assert_called_once_with(10)
        assert result == 20

    @skip_pypy
    class TestOnClass:
        """Spies installed on a class rather than on an instance."""

        def test_instance_method(self, mocker: MockerFixture) -> None:
            class Foo:
                def bar(self, arg):
                    return arg * 2

            spy = mocker.spy(Foo, "bar")
            foo = Foo()
            other = Foo()
            assert foo.bar(arg=10) == 20
            assert other.bar(arg=10) == 20
            calls = [mocker.call(foo, arg=10), mocker.call(other, arg=10)]
            assert spy.call_args_list == calls

        def test_instance_method_subclass(self, mocker: MockerFixture) -> None:
            class Base:
                def bar(self, arg):
                    return arg * 2

            class Foo(Base):
                pass

            spy = mocker.spy(Foo, "bar")
            foo = Foo()
            other = Foo()
            assert foo.bar(arg=10) == 20
            assert other.bar(arg=10) == 20
            calls = [mocker.call(foo, arg=10), mocker.call(other, arg=10)]
            assert spy.call_args_list == calls
            assert spy.spy_return == 20
            assert spy.spy_return_iter is None
            assert spy.spy_return_list == [20, 20]

        def test_class_method(self, mocker: MockerFixture) -> None:
            class Foo:
                @classmethod
                def bar(cls, arg):
                    return arg * 2

            spy = mocker.spy(Foo, "bar")
            assert Foo.bar(arg=10) == 20
            Foo.bar.assert_called_once_with(arg=10)  # type:ignore[attr-defined]
            assert Foo.bar.spy_return == 20  # type:ignore[attr-defined]
            assert Foo.bar.spy_return_iter is None  # type:ignore[attr-defined]
            assert Foo.bar.spy_return_list == [20]  # type:ignore[attr-defined]
            spy.assert_called_once_with(arg=10)
            assert spy.spy_return == 20
            assert spy.spy_return_iter is None
            assert spy.spy_return_list == [20]

        def test_class_method_subclass(self, mocker: MockerFixture) -> None:
            class Base:
                @classmethod
                def bar(self, arg):
                    return arg * 2

            class Foo(Base):
                pass

            spy = mocker.spy(Foo, "bar")
            assert Foo.bar(arg=10) == 20
            Foo.bar.assert_called_once_with(arg=10)  # type:ignore[attr-defined]
            assert Foo.bar.spy_return == 20  # type:ignore[attr-defined]
            assert Foo.bar.spy_return_iter is None  # type:ignore[attr-defined]
            assert Foo.bar.spy_return_list == [20]  # type:ignore[attr-defined]
            spy.assert_called_once_with(arg=10)
            assert spy.spy_return == 20
            assert spy.spy_return_iter is None
            assert spy.spy_return_list == [20]

        def test_class_method_with_metaclass(self, mocker: MockerFixture) -> None:
            class MetaFoo(type):
                pass

            class Foo:
                __metaclass__ = MetaFoo

                @classmethod
                def bar(cls, arg):
                    return arg * 2

            spy = mocker.spy(Foo, "bar")
            assert Foo.bar(arg=10) == 20
            Foo.bar.assert_called_once_with(arg=10)  # type:ignore[attr-defined]
            assert Foo.bar.spy_return == 20  # type:ignore[attr-defined]
            assert Foo.bar.spy_return_iter is None  # type:ignore[attr-defined]
            assert Foo.bar.spy_return_list == [20]  # type:ignore[attr-defined]
            spy.assert_called_once_with(arg=10)
            assert spy.spy_return == 20
            assert spy.spy_return_iter is None
            assert spy.spy_return_list == [20]

        def test_static_method(self, mocker: MockerFixture) -> None:
            class Foo:
                @staticmethod
                def bar(arg):
                    return arg * 2

            spy = mocker.spy(Foo, "bar")
            assert Foo.bar(arg=10) == 20
            Foo.bar.assert_called_once_with(arg=10)  # type:ignore[attr-defined]
            assert Foo.bar.spy_return == 20  # type:ignore[attr-defined]
            assert Foo.bar.spy_return_iter is None  # type:ignore[attr-defined]
            assert Foo.bar.spy_return_list == [20]  # type:ignore[attr-defined]
            spy.assert_called_once_with(arg=10)
            assert spy.spy_return == 20
            assert spy.spy_return_iter is None
            assert spy.spy_return_list == [20]

        def test_static_method_subclass(self, mocker: MockerFixture) -> None:
            class Base:
                @staticmethod
                def bar(arg):
                    return arg * 2

            class Foo(Base):
                pass

            spy = mocker.spy(Foo, "bar")
            assert Foo.bar(arg=10) == 20
            Foo.bar.assert_called_once_with(arg=10)  # type:ignore[attr-defined]
            assert Foo.bar.spy_return == 20  # type:ignore[attr-defined]
            assert Foo.bar.spy_return_iter is None  # type:ignore[attr-defined]
            assert Foo.bar.spy_return_list == [20]  # type:ignore[attr-defined]
            spy.assert_called_once_with(arg=10)
            assert spy.spy_return == 20
            assert spy.spy_return_iter is None
            assert spy.spy_return_list == [20]


class TestSpyReturnIter:
    """``spy_return_iter``, enabled with ``duplicate_iterators=True``."""

    @pytest.mark.parametrize("iterator", [(i for i in range(3)), iter([0, 1, 2])])
    def test_duplicates_iterator_when_enabled(
        self, mocker: MockerFixture, iterator: Iterator[int]
    ) -> None:
        class Foo:
            def bar(self) -> Iterator[int]:
                return iterator

        foo = Foo()
        spy = mocker.spy(foo, "bar", duplicate_iterators=True)
        result = list(foo.bar())

        assert result == [0, 1, 2]
        assert spy.spy_return is not None
        assert spy.spy_return_iter is not None
        assert list(spy.spy_return_iter) == result

        [return_value] = spy.spy_return_list
        assert isinstance(return_value, Iterator)

    @pytest.mark.parametrize("iterator", [(i for i in range(3)), iter([0, 1, 2])])
    def test_is_not_set_when_disabled(
        self, mocker: MockerFixture, iterator: Iterator[int]
    ) -> None:
        class Foo:
            def bar(self) -> Iterator[int]:
                return iterator

        foo = Foo()
        spy = mocker.spy(foo, "bar", duplicate_iterators=False)
        result = list(foo.bar())

        assert result == [0, 1, 2]
        assert spy.spy_return is not None
        assert spy.spy_return_iter is None
        [return_value] = spy.spy_return_list
        assert isinstance(return_value, Iterator)

    @pytest.mark.parametrize("iterable", [(0, 1, 2), [0, 1, 2], range(3)])
    def test_ignores_plain_iterable(
        self, mocker: MockerFixture, iterable: Iterable[int]
    ) -> None:
        class Foo:
            def bar(self) -> Iterable[int]:
                return iterable

        foo = Foo()
        spy = mocker.spy(foo, "bar", duplicate_iterators=True)
        result = foo.bar()

        assert result == iterable
        assert spy.spy_return == result
        assert spy.spy_return_iter is None
        assert spy.spy_return_list == [result]

    def test_resets(self, mocker: MockerFixture) -> None:
        class Foo:
            iterables: Any = [  # noqa:RUF012
                (i for i in range(3)),
                99,
            ]

            def bar(self) -> Any:
                return self.iterables.pop(0)

        foo = Foo()
        spy = mocker.spy(foo, "bar", duplicate_iterators=True)
        result_iterator = list(foo.bar())

        assert result_iterator == [0, 1, 2]
        assert spy.spy_return_iter is not None
        assert list(spy.spy_return_iter) == result_iterator

        assert foo.bar() == 99
        assert spy.spy_return_iter is None

    @pytest.mark.asyncio
    async def test_async_duplicates_iterator_when_enabled(
        self,
        mocker: MockerFixture,
    ) -> None:
        class Foo:
            async def bar(self) -> Iterator[int]:
                return iter([0, 1, 2])

        foo = Foo()
        spy = mocker.spy(foo, "bar", duplicate_iterators=True)
        result = await foo.bar()

        assert list(result) == [0, 1, 2]
        assert spy.spy_return is not None
        assert spy.spy_return_iter is not None
        assert list(spy.spy_return_iter) == [0, 1, 2]

        [return_value] = spy.spy_return_list
        assert isinstance(return_value, Iterator)


class TestAssertWrappers:
    """
    Mock assertion methods are wrapped to hide pytest-mock frames from tracebacks.
    """

    def test_not_called(self, mocker: MockerFixture) -> None:
        stub = mocker.stub()
        stub.assert_not_called()
        stub()
        with assert_traceback():
            stub.assert_not_called()

    def test_called_with(self, mocker: MockerFixture) -> None:
        stub = mocker.stub()
        stub("foo")
        stub.assert_called_with("foo")
        with assert_traceback():
            stub.assert_called_with("bar")

    def test_called_once_with(self, mocker: MockerFixture) -> None:
        stub = mocker.stub()
        stub("foo")
        stub.assert_called_once_with("foo")
        stub("foo")
        with assert_traceback():
            stub.assert_called_once_with("foo")

    def test_called_once(self, mocker: MockerFixture) -> None:
        stub = mocker.stub()
        if not hasattr(stub, "assert_called_once"):
            pytest.skip("assert_called_once not available")
        stub("foo")
        stub.assert_called_once()
        stub("foo")
        with assert_traceback():
            stub.assert_called_once()

    def test_called(self, mocker: MockerFixture) -> None:
        stub = mocker.stub()
        if not hasattr(stub, "assert_called"):
            pytest.skip("assert_called_once not available")
        with assert_traceback():
            stub.assert_called()
        stub("foo")
        stub.assert_called()
        stub("foo")
        stub.assert_called()

    def test_any_call(self, mocker: MockerFixture) -> None:
        stub = mocker.stub()
        stub("foo")
        stub("foo")
        stub.assert_any_call("foo")
        with assert_traceback():
            stub.assert_any_call("bar")

    def test_called_with_unicode_arguments(self, mocker: MockerFixture) -> None:
        """Test bug in assert_call_with called with non-ascii unicode string (#91)"""
        stub = mocker.stub()
        stub(b"l\xc3\xb6k".decode("UTF-8"))

        with pytest.raises(AssertionError):
            stub.assert_called_with("lak")

    def test_missing_introspection(self, testdir: Any) -> None:
        testdir.makepyfile(
            """
            def test_foo(mocker):
                mock = mocker.Mock()
                mock('foo')
                mock('test')
                mock.assert_called_once_with('test')
        """
        )
        result = testdir.runpytest()
        assert "pytest introspection follows:" not in result.stdout.str()


class TestAssertHasCalls:
    """``assert_has_calls``, including the shapes accepted as expected calls."""

    def test_basic(self, mocker: MockerFixture) -> None:
        stub = mocker.stub()
        stub("foo")
        stub.assert_has_calls([mocker.call("foo")])
        with assert_traceback():
            stub.assert_has_calls([mocker.call("bar")])

    def test_multiple_calls(self, mocker: MockerFixture) -> None:
        stub = mocker.stub()
        stub("foo")
        stub("bar")
        stub("baz")
        stub.assert_has_calls(
            [mocker.call("foo"), mocker.call("bar"), mocker.call("baz")]
        )
        with assert_traceback():
            stub.assert_has_calls(
                [
                    mocker.call("foo"),
                    mocker.call("bar"),
                    mocker.call("baz"),
                    mocker.call("bat"),
                ]
            )
        with assert_traceback():
            stub.assert_has_calls(
                [mocker.call("foo"), mocker.call("baz"), mocker.call("bar")]
            )

    def test_multiple_calls_subset(self, mocker: MockerFixture) -> None:
        stub = mocker.stub()
        stub("foo")
        stub("bar")
        stub("baz")
        stub.assert_has_calls([mocker.call("bar"), mocker.call("baz")])
        with assert_traceback():
            stub.assert_has_calls([mocker.call("foo"), mocker.call("baz")])
        with assert_traceback():
            stub.assert_has_calls(
                [mocker.call("foo"), mocker.call("bar"), mocker.call("bat")]
            )
        with assert_traceback():
            stub.assert_has_calls([mocker.call("baz"), mocker.call("bar")])

    def test_multiple_calls_any_order(self, mocker: MockerFixture) -> None:
        stub = mocker.stub()
        stub("foo")
        stub("bar")
        stub("baz")
        stub.assert_has_calls(
            [mocker.call("foo"), mocker.call("baz"), mocker.call("bar")], any_order=True
        )
        with assert_traceback():
            stub.assert_has_calls(
                [
                    mocker.call("foo"),
                    mocker.call("baz"),
                    mocker.call("bar"),
                    mocker.call("bat"),
                ],
                any_order=True,
            )

    def test_multiple_calls_any_order_subset(
        self,
        mocker: MockerFixture,
    ) -> None:
        stub = mocker.stub()
        stub("foo")
        stub("bar")
        stub("baz")
        stub.assert_has_calls([mocker.call("baz"), mocker.call("foo")], any_order=True)
        with assert_traceback():
            stub.assert_has_calls(
                [mocker.call("baz"), mocker.call("foo"), mocker.call("bat")],
                any_order=True,
            )

    def test_no_calls(
        self,
        mocker: MockerFixture,
    ) -> None:
        stub = mocker.stub()
        stub.assert_has_calls([])
        with assert_traceback():
            stub.assert_has_calls([mocker.call("foo")])

    @pytest.mark.usefixtures("needs_assert_rewrite")
    def test_two_tuple_calls(self, mocker: MockerFixture) -> None:
        """Expected calls given as ``(args, kwargs)`` pairs, such as the entries of
        another mock's ``call_args_list``, must raise ``AssertionError`` on mismatch."""
        expected = mocker.stub()
        expected("foo", key="expected")
        stub = mocker.stub()
        stub("foo", key="actual")

        with pytest.raises(AssertionError) as exc_info:
            stub.assert_has_calls(expected.call_args_list)
        introspection = str(exc_info.value).split("pytest introspection follows:")[1]
        assert "'expected'" in introspection
        assert "'actual'" in introspection

    @pytest.mark.parametrize(
        "expected_call",
        [
            pytest.param(((2,),), id="args-only"),
            pytest.param(({"a": 2},), id="kwargs-only"),
        ],
    )
    def test_one_tuple_calls(
        self, mocker: MockerFixture, expected_call: tuple[Any, ...]
    ) -> None:
        """Expected calls given as ``(args,)`` or ``(kwargs,)`` must raise
        ``AssertionError`` on mismatch."""
        stub = mocker.MagicMock()
        stub(1)
        with pytest.raises(AssertionError, match="Calls not found"):
            stub.assert_has_calls([expected_call])

    @pytest.mark.usefixtures("needs_assert_rewrite")
    def test_named_two_tuple_calls(self, mocker: MockerFixture) -> None:
        """Expected calls given as ``(name, args)`` must be introspected using
        ``args``, not the name."""
        stub = mocker.MagicMock()
        stub("actual")
        with pytest.raises(AssertionError) as exc_info:
            stub.assert_has_calls([("", ("expected",))])
        introspection = str(exc_info.value).split("pytest introspection follows:")[1]
        assert "'expected'" in introspection
        assert "Kwargs" not in introspection

    @pytest.mark.usefixtures("needs_assert_rewrite")
    def test_named_kwargs_two_tuple_calls(self, mocker: MockerFixture) -> None:
        """Expected calls given as ``(name, kwargs)`` must be introspected using
        ``kwargs``, not the name."""
        stub = mocker.MagicMock()
        stub(key="actual")
        with pytest.raises(AssertionError) as exc_info:
            stub.assert_has_calls([("", {"key": "expected"})])
        introspection = str(exc_info.value).split("pytest introspection follows:")[1]
        assert "'expected'" in introspection
        assert "Args" not in introspection


@pytest.mark.usefixtures("needs_assert_rewrite")
class TestAsyncAssertions:
    """Assertions on ``AsyncMock`` introspect awaits, not calls."""

    @pytest.mark.parametrize(
        "assertion",
        ["assert_awaited_with", "assert_awaited_once_with", "assert_any_await"],
    )
    @pytest.mark.asyncio
    async def test_uses_await_arguments(
        self, mocker: MockerFixture, assertion: str
    ) -> None:
        stub = mocker.AsyncMock()
        await stub("awaited", source="awaited")
        stub("called", source="called").close()

        getattr(stub, assertion)("awaited", source="awaited")
        with pytest.raises(AssertionError) as exc_info:
            getattr(stub, assertion)("wrong", source="wrong")
        introspection = str(exc_info.value).split("pytest introspection follows:")[1]
        assert "'awaited'" in introspection
        assert "'called'" not in introspection

        with pytest.raises(AssertionError) as exc_info:
            stub.assert_called_with("wrong", source="wrong")
        introspection = str(exc_info.value).split("pytest introspection follows:")[1]
        assert "'called'" in introspection
        assert "'awaited'" not in introspection

    def test_without_await(self, mocker: MockerFixture) -> None:
        stub = mocker.AsyncMock()
        stub("called").close()
        with pytest.raises(AssertionError) as exc_info:
            stub.assert_awaited_with("expected")
        assert "pytest introspection follows:" not in str(exc_info.value)


@pytest.mark.usefixtures("needs_assert_rewrite")
class TestIntrospection:
    """pytest's assertion introspection added to failed mock assertions."""

    @staticmethod
    @contextmanager
    def assert_argument_introspection(
        left: Any, right: Any
    ) -> Generator[None, None, None]:
        """
        Assert detailed argument introspection is used
        """
        try:
            yield
        except AssertionError as e:
            version = tuple(int(x) for x in pytest.__version__.split(".")[:3])

            if version[:2] < (9, 1):
                from _pytest.assertion.util import _compare_eq_iterable  # type:ignore
            else:
                from _pytest.assertion._compare_sequence import (  # type:ignore
                    _compare_eq_iterable,
                )

            # NOTE: we assert with either verbose or not, depending on how our own
            #       test was run by examining sys.argv
            verbose = any(a.startswith("-v") for a in sys.argv)
            if version[0] < 8:
                expected = "\n  ".join(_compare_eq_iterable(left, right, verbose))  # type:ignore
            else:
                expected = "\n  ".join(
                    _compare_eq_iterable(left, right, lambda t, *_, **__: t, verbose)  # type:ignore
                )
            assert expected in str(e)
        else:
            raise AssertionError("DID NOT RAISE")

    def test_called_args(self, mocker: MockerFixture) -> None:
        stub = mocker.stub()

        complex_args = ("a", 1, {"test"})
        wrong_args = ("b", 2, {"jest"})

        stub(*complex_args)
        stub.assert_called_with(*complex_args)
        stub.assert_called_once_with(*complex_args)

        with self.assert_argument_introspection(complex_args, wrong_args):
            stub.assert_called_with(*wrong_args)
            stub.assert_called_once_with(*wrong_args)

    def test_called_kwargs(self, mocker: MockerFixture) -> None:
        stub = mocker.stub()

        complex_kwargs = {"foo": {"bar": 1, "baz": "spam"}}
        wrong_kwargs = {"foo": {"goo": 1, "baz": "bran"}}

        stub(**complex_kwargs)
        stub.assert_called_with(**complex_kwargs)
        stub.assert_called_once_with(**complex_kwargs)

        with self.assert_argument_introspection(complex_kwargs, wrong_kwargs):
            stub.assert_called_with(**wrong_kwargs)
            stub.assert_called_once_with(**wrong_kwargs)

    def test_detailed(self, testdir: Any) -> None:
        """Check that the "mock_use_standalone" is being used."""
        testdir.makeini(
            """
            [pytest]
            asyncio_mode=auto
            """
        )
        testdir.makepyfile(
            """
            def test(mocker):
                m = mocker.Mock()
                m('fo')
                m.assert_called_once_with('', bar=4)
        """
        )
        result = testdir.runpytest("-s")
        expected_lines = [
            "*AssertionError: expected call not found.",
            "*Expected: mock('', bar=4)",
            "*Actual: mock('fo')",
        ]
        expected_lines += [
            "*pytest introspection follows:*",
            "*Args:",
            "*assert ('fo',) == ('',)",
            "*At index 0 diff: 'fo' != ''*",
            "*Use -v to*",
            "*Kwargs:*",
            "*assert {} == {'bar': 4}*",
            "*Right contains* more item*",
            "*{'bar': 4}*",
            "*Use -v to*",
        ]
        result.stdout.fnmatch_lines(expected_lines)

    def test_detailed_async(self, testdir: Any) -> None:
        """Check that the "mock_use_standalone" is being used."""
        testdir.makeini(
            """
            [pytest]
            asyncio_mode=auto
            """
        )
        testdir.makepyfile(
            """
            import pytest

            async def test(mocker):
                m = mocker.AsyncMock()
                await m('fo')
                m.assert_awaited_once_with('', bar=4)
        """
        )
        result = testdir.runpytest("-s")
        expected_lines = [
            "*AssertionError: expected await not found.",
            "*Expected: mock('', bar=4)",
            "*Actual: mock('fo')",
            "*pytest introspection follows:*",
            "*Args:",
            "*assert ('fo',) == ('',)",
            "*At index 0 diff: 'fo' != ''*",
            "*Use -v to*",
            "*Kwargs:*",
            "*assert {} == {'bar': 4}*",
            "*Right contains* more item*",
            "*{'bar': 4}*",
            "*Use -v to*",
        ]
        result.stdout.fnmatch_lines(expected_lines)


class TestConfiguration:
    """Ini options and command-line flags that change pytest-mock's behavior."""

    def test_monkeypatch_ini(self, testdir: Any, mocker: MockerFixture) -> None:
        # Make sure the following function actually tests something
        stub = mocker.stub()
        assert stub.assert_called_with.__module__ != stub.__module__

        testdir.makepyfile(
            """
            def test_foo(mocker):
                stub = mocker.stub()
                assert stub.assert_called_with.__module__ == stub.__module__
        """
        )
        testdir.makeini(
            """
            [pytest]
            mock_traceback_monkeypatch = false
        """
        )
        result = testdir.runpytest_subprocess()
        assert result.ret == 0

    def test_parse_ini_boolean(self) -> None:
        from pytest_mock._util import parse_ini_boolean

        assert parse_ini_boolean("True") is True
        assert parse_ini_boolean("false") is False
        with pytest.raises(ValueError):
            parse_ini_boolean("foo")

    def test_monkeypatch_native(self, testdir: Any) -> None:
        """Automatically disable monkeypatching when --tb=native."""
        testdir.makepyfile(
            """
            def test_foo(mocker):
                stub = mocker.stub()
                stub(1, greet='hello')
                stub.assert_called_once_with(1, greet='hey')
        """
        )
        result = testdir.runpytest_subprocess("--tb=native")
        assert result.ret == 1
        assert "During handling of the above exception" not in result.stdout.str()
        assert "Differing items:" not in result.stdout.str()
        traceback_lines = [
            x
            for x in result.stdout.str().splitlines()
            if "Traceback (most recent call last)" in x
        ]
        assert (
            len(traceback_lines) == 1
        )  # make sure there are no duplicated tracebacks (#44)

    def test_monkeypatch_no_terminal(self, testdir: Any) -> None:
        """Don't crash without 'terminal' plugin."""
        testdir.makepyfile(
            """
            def test_foo(mocker):
                stub = mocker.stub()
                stub(1, greet='hello')
                stub.assert_called_once_with(1, greet='hey')
            """
        )
        result = testdir.runpytest_subprocess("-p", "no:terminal", "-s")
        assert result.ret == 1
        assert result.stdout.lines == []

    def test_standalone_mock(self, testdir: Any) -> None:
        """Check that the "mock_use_standalone" is being used."""
        pytest.importorskip("mock")

        testdir.makepyfile(
            """
            import mock

            def test_foo(mocker):
                assert mock.MagicMock is mocker.MagicMock
        """
        )
        testdir.makeini(
            """
            [pytest]
            mock_use_standalone_module = true
        """
        )
        result = testdir.runpytest_subprocess()
        assert result.ret == 0


class TestStop:
    """``mocker.stop`` and ``mocker.stopall``."""

    def test_plain_stopall(self, testdir: Any) -> None:
        """patch.stopall() in a test should not cause an error during unconfigure (#137)"""
        testdir.makeini(
            """
            [pytest]
            asyncio_mode=auto
            """
        )
        testdir.makepyfile(
            """
            import random

            def get_random_number():
                return random.randint(0, 100)

            def test_get_random_number(mocker):
                patcher = mocker.mock_module.patch("random.randint", lambda x, y: 5)
                patcher.start()
                assert get_random_number() == 5
                mocker.mock_module.patch.stopall()
        """
        )
        result = testdir.runpytest_subprocess()
        result.stdout.fnmatch_lines("* 1 passed in *")
        assert "RuntimeError" not in result.stderr.str()

    def test_patch(self, mocker):
        class UnSpy:
            def foo(self):
                return 42

        m = mocker.patch.object(UnSpy, "foo", return_value=0)
        assert UnSpy().foo() == 0
        mocker.stop(m)
        assert UnSpy().foo() == 42

        with pytest.raises(ValueError):
            mocker.stop(m)

    def test_instance_patch(self, mocker):
        class UnSpy:
            def foo(self):
                return 42

        m = mocker.patch.object(UnSpy, "foo", return_value=0)
        un_spy = UnSpy()
        assert un_spy.foo() == 0
        mocker.stop(m)
        assert un_spy.foo() == 42

    def test_spy(self, mocker):
        class UnSpy:
            def foo(self):
                return 42

        spy = mocker.spy(UnSpy, "foo")
        assert UnSpy().foo() == 42
        assert spy.call_count == 1
        mocker.stop(spy)
        assert UnSpy().foo() == 42
        assert spy.call_count == 1

    def test_instance_spy(self, mocker):
        class UnSpy:
            def foo(self):
                return 42

        spy = mocker.spy(UnSpy, "foo")
        un_spy = UnSpy()
        assert un_spy.foo() == 42
        assert spy.call_count == 1
        mocker.stop(spy)
        assert un_spy.foo() == 42
        assert spy.call_count == 1

    def test_multiple_patches(self, mocker: MockerFixture) -> None:
        """Regression for #420."""

        class Class1:
            @staticmethod
            def get():
                return 1

        class Class2:
            @staticmethod
            def get():
                return 2

        def handle_get():
            return 3

        mocker.patch.object(Class1, "get", handle_get)
        mocker.patch.object(Class2, "get", handle_get)

        mocker.stopall()

        assert Class1.get() == 1
        assert Class2.get() == 2


class TestContextManagerWarnings:
    """Warnings when patches are misused as context managers."""

    def test_patch_object(self, mocker: MockerFixture) -> None:
        class A:
            def doIt(self):
                return False

        a = A()

        expected_warning_msg = (
            "Mocks returned by pytest-mock do not need to be used as context managers. "
            "The mocker fixture automatically undoes mocking at the end of a test. "
            "This warning can be ignored if it was triggered by mocking a context manager. "
            "https://pytest-mock.readthedocs.io/en/latest/usage.html#usage-as-context-manager"
        )

        with (
            pytest.warns(
                PytestMockWarning, match=re.escape(expected_warning_msg)
            ) as warn_record,
            mocker.patch.object(a, "doIt", return_value=True),
        ):
            assert a.doIt() is True

        assert warn_record[0].filename == __file__

    def test_patch(self, mocker: MockerFixture) -> None:
        expected_warning_msg = (
            "Mocks returned by pytest-mock do not need to be used as context managers. "
            "The mocker fixture automatically undoes mocking at the end of a test. "
            "This warning can be ignored if it was triggered by mocking a context manager. "
            "https://pytest-mock.readthedocs.io/en/latest/usage.html#usage-as-context-manager"
        )

        with (
            pytest.warns(
                PytestMockWarning, match=re.escape(expected_warning_msg)
            ) as warn_record,
            mocker.patch("json.loads"),
        ):
            pass

        assert warn_record[0].filename == __file__

    def test_patching_a_context_manager(self, mocker: MockerFixture) -> None:
        """Our message about misusing mocker as a context manager should not affect mocking
        context managers (see #192)"""

        class dummy_module:
            class MyContext:
                def __enter__(self, *args, **kwargs):
                    return 10

                def __exit__(self, *args, **kwargs):
                    pass

        def my_func():
            with dummy_module.MyContext() as v:
                return v

        mocker.patch.object(dummy_module, "MyContext")
        assert isinstance(my_func(), mocker.MagicMock)

    def test_patch_context_manager(self, mocker: MockerFixture) -> None:
        """Test that no warnings are issued when an object patched with
        patch.context_manager is used as a context manager (#221)"""

        class A:
            def doIt(self):
                return False

        a = A()

        with warnings.catch_warnings(record=True) as warn_record:  # noqa:SIM117
            with mocker.patch.context_manager(a, "doIt", return_value=True):
                assert a.doIt() is True

        assert len(warn_record) == 0

    def test_stale_pyc(self, testdir: Any, request: Any) -> None:
        """Ensure we don't trigger an error in case the frame where mocker.patch is being
        used doesn't have a 'context' (#169)"""
        import compileall

        py_fn = testdir.makepyfile(
            c="""
            class C:
                x = 1

            def check(mocker):
                mocker.patch.object(C, "x", 2)
                assert C.x == 2
        """
        )
        syspath_insert_workaround(request, testdir)

        testdir.makepyfile(
            """
            from c import check
            def test_foo(mocker):
                check(mocker)
        """
        )
        result = testdir.runpytest()
        result.assert_outcomes(passed=1)

        assert compileall.compile_file(str(py_fn), legacy=True)

        pyc_fn = str(py_fn) + "c"
        assert os.path.isfile(pyc_fn)

        py_fn.remove()
        result = testdir.runpytest()
        result.assert_outcomes(passed=1)


class TestFixtureScopes:
    """
    The ``class_mocker``, ``module_mocker``, ``package_mocker`` and
    ``session_mocker`` fixtures.
    """

    def test_class(self, testdir: Any) -> None:
        testdir.makeini(
            """
            [pytest]
            asyncio_mode=auto
            """
        )
        testdir.makepyfile(
            """
            import pytest
            import random
            import unittest

            def get_random_number():
                return random.randint(0, 1)

            @pytest.fixture(autouse=True, scope="class")
            def randint_mock(class_mocker):
                return class_mocker.patch("random.randint", lambda x, y: 5)

            class TestGetRandomNumber(unittest.TestCase):
                def test_get_random_number(self):
                    assert get_random_number() == 5
        """
        )
        result = testdir.runpytest_subprocess()
        assert "AssertionError" not in result.stderr.str()
        result.stdout.fnmatch_lines("* 1 passed in *")

    @pytest.mark.parametrize("scope", ["module", "package", "session"])
    def test_scope(self, testdir: Any, scope: str) -> None:
        testdir.makeini(
            """
            [pytest]
            asyncio_mode=auto
            """
        )
        testdir.makepyfile(
            f"""
            import pytest
            import random

            def get_random_number():
                return random.randint(0, 1)

            @pytest.fixture(autouse=True, scope="{scope}")
            def randint_mock({scope}_mocker):
                return {scope}_mocker.patch("random.randint", lambda x, y: 5)

            def test_get_random_number():
                assert get_random_number() == 5
        """
        )
        result = testdir.runpytest_subprocess()
        assert "AssertionError" not in result.stderr.str()
        result.stdout.fnmatch_lines("* 1 passed in *")
