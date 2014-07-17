import sys

import pytest


if sys.version_info >= (3, 3):
    import unittest.mock as mock_module
else:
    import mock as mock_module


class MockFixture(object):
    """
    Fixture that provides the same interface to functions in the mock module,
    ensuring that they are uninstalled at the end of each test.
    """

    def __init__(self):
        self._patches = []  # list of mock._patch objects
        self.patch = self._Patcher(self._patches)

    def stopall(self):
        """
        Stop all patchers started by this fixture. Can be safely called multiple
        times.
        """
        for p in self._patches:
            p.stop()
        self._patches[:] = []

    class _Patcher(object):
        """
        Object to provide the same interface as mock.patch, mock.patch.object,
        etc. We need this indirection to keep the same API of the mock package.
        """

        def __init__(self, patches):
            self._patches = patches

        def _start_patch(self, mock_func, *args, **kwargs):
            """Patches something by calling the given function from the mock
            module, registering the patch to stop it later and returns the
            mock object resulting from the mock call.
            """
            p = mock_func(*args, **kwargs)
            mocked = p.start()
            self._patches.append(p)
            return mocked

        def object(self, *args, **kwargs):
            """API to mock.patch.object"""
            return self._start_patch(mock_module.patch.object, *args, **kwargs)


        def multiple(self, *args, **kwargs):
            """API to mock.patch.multiple"""
            return self._start_patch(mock_module.patch.multiple, *args,
                                     **kwargs)


        def __call__(self, *args, **kwargs):
            """API to mock.patch"""
            return self._start_patch(mock_module.patch, *args, **kwargs)


@pytest.yield_fixture
def mock():
    """
    return an object that has the same interface to the `mock` module, but
    takes care of automatically undoing all patches after each test method.
    """
    result = MockFixture()
    yield result
    result.stopall()