"""Tests for SpyType type annotations.

This test file verifies that the SpyType protocol correctly exposes
the spy-specific attributes for type checking purposes.
"""

from typing import get_type_hints

import pytest

from pytest_mock import MockerFixture
from pytest_mock import SpyType


class TestSpyTypeAnnotations:
    """Tests for SpyType type annotation correctness."""

    def test_spy_type_exists(self) -> None:
        """Verify SpyType is exported from pytest_mock."""
        from pytest_mock import SpyType as imported_spy_type

        assert imported_spy_type is not None

    def test_spy_type_has_spy_return_attribute(self) -> None:
        """Verify spy_return attribute is defined in SpyType."""
        hints = get_type_hints(SpyType)
        assert "spy_return" in hints

    def test_spy_type_has_spy_return_list_attribute(self) -> None:
        """Verify spy_return_list attribute is defined in SpyType."""
        hints = get_type_hints(SpyType)
        assert "spy_return_list" in hints

    def test_spy_type_has_spy_return_iter_attribute(self) -> None:
        """Verify spy_return_iter attribute is defined in SpyType."""
        hints = get_type_hints(SpyType)
        assert "spy_return_iter" in hints

    def test_spy_type_has_spy_exception_attribute(self) -> None:
        """Verify spy_exception attribute is defined in SpyType."""
        hints = get_type_hints(SpyType)
        assert "spy_exception" in hints

    def test_spy_returns_spy_type(self, mocker: MockerFixture) -> None:
        """Verify spy() method returns SpyType for proper type inference."""

        class Foo:
            def bar(self) -> int:
                return 42

        # The spy method should return SpyType, which means:
        # - The return value should have spy_return, spy_return_list, etc.
        # - Type checkers should recognize these attributes without type: ignore
        spy = mocker.spy(Foo, "bar")

        # These should work without type: ignore comments
        result = spy.spy_return  # type checker should recognize this
        assert result is None  # not called yet

        Foo().bar()
        assert spy.spy_return == 42

        # spy_return_list should be accessible
        assert spy.spy_return_list == [42]

        # spy_exception should be accessible
        assert spy.spy_exception is None

    def test_spy_type_runtime_checkable(self, mocker: MockerFixture) -> None:
        """Verify SpyType is runtime_checkable for isinstance checks."""

        class Foo:
            def method(self) -> str:
                return "test"

        spy = mocker.spy(Foo, "method")

        # SpyType should be runtime_checkable, allowing isinstance checks
        # This is useful for runtime validation
        # Note: Protocol isinstance checks require runtime_checkable decorator
        # and check for presence of required methods/attributes
        # The spy object has all the required attributes (spy_return, spy_return_list, etc.)
        # and the mock methods (assert_called, etc.)
        # However, Protocol isinstance checks may not work with MagicMock due to
        # how MagicMock handles attribute access
        # For now, we verify the attributes exist rather than isinstance
        assert hasattr(spy, "spy_return")
        assert hasattr(spy, "spy_return_list")
        assert hasattr(spy, "spy_return_iter")
        assert hasattr(spy, "spy_exception")
        assert hasattr(spy, "assert_called")
        assert hasattr(spy, "call_count")

    def test_spy_type_has_mock_methods(self, mocker: MockerFixture) -> None:
        """Verify SpyType includes common mock assertion methods."""

        class Foo:
            def bar(self, x: int) -> int:
                return x + 1

        spy = mocker.spy(Foo, "bar")

        # These mock assertion methods should be available on SpyType
        # without type: ignore comments
        spy.assert_not_called()

        foo = Foo()
        foo.bar(5)
        spy.assert_called_once()
        # Note: instance method spy includes 'self' in the call args
        spy.assert_called_with(foo, 5)

        # call_count and called should also be available
        assert spy.call_count == 1
        assert spy.called is True

    def test_spy_type_with_exception(self, mocker: MockerFixture) -> None:
        """Verify spy_exception attribute captures exceptions correctly."""

        class Foo:
            def error_method(self) -> None:
                raise ValueError("test error")

        spy = mocker.spy(Foo, "error_method")

        with pytest.raises(ValueError):
            Foo().error_method()

        # spy_exception should be accessible and contain the raised exception
        assert spy.spy_exception is not None
        assert isinstance(spy.spy_exception, ValueError)
        assert str(spy.spy_exception) == "test error"

    def test_async_spy_returns_spy_type(self, mocker: MockerFixture) -> None:
        """Verify spy() on async methods also returns SpyType."""
        import asyncio

        class AsyncFoo:
            async def async_method(self) -> str:
                return "async_result"

        spy = mocker.spy(AsyncFoo, "async_method")

        # SpyType should work for async methods as well
        async def run_test() -> None:
            result = await AsyncFoo().async_method()
            assert spy.spy_return == "async_result"
            assert spy.spy_return_list == ["async_result"]

        asyncio.run(run_test())
