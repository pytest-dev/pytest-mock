import pytest


class MockFixture(object):
    def __init__(self):
        self._patches = []
        self.patch = self._Patcher(self._patches)

    def stopall(self):
        for p in self._patches:
            p.stop()
        self._patches[:] = []

    class _Patcher(object):
        def __init__(self, patches):
            self._patches = patches

        def object(self, *args, **kwargs):
            import mock

            p = mock.patch.object(*args, **kwargs)
            mocked = p.start()
            self._patches.append(p)
            return mocked


        def multiple(self, *args, **kwargs):
            import mock

            p = mock.patch.multiple(*args, **kwargs)
            mocked = p.start()
            self._patches.append(p)
            return mocked


        def __call__(self, *args, **kwargs):
            import mock

            p = mock.patch(*args, **kwargs)
            mocked = p.start()
            self._patches.append(p)
            return mocked


@pytest.yield_fixture
def mock():
    result = MockFixture()
    yield result
    result.stopall()