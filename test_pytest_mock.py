import os

import pytest


class MockFixture(object):

    def __init__(self):
        self._patches = []
        self.patch = self._PatchWrapper(self._patches)

    def stopall(self):
        for p in self._patches:
            p.stop()
        self._patches[:] = []

    class _PatchWrapper(object):

        def __init__(self, patches):
            self._patches = patches

        def object(self, *args, **kwargs):
            import mock
            p = mock.patch.object(*args, **kwargs)
            mocked = p.start()
            self._patches.append(p)
            return mocked


@pytest.yield_fixture
def mock():
    result = MockFixture()
    yield result
    result.stopall()


class UnixFS(object):

    @classmethod
    def rm(cls, filename):
        os.remove(filename)

    @classmethod
    def ls(cls, path):
        return os.listdir(path)


def test_fixture(mock, tmpdir):
    mock.patch.object(os, 'remove')
    (tmpdir / 'foo.txt').ensure()
    UnixFS.rm(tmpdir / 'foo.txt')
    os.remove.assert_called_once_with(tmpdir / 'foo.txt')
    assert os.path.isfile(str(tmpdir / 'foo.txt'))
    mock.stopall()
    UnixFS.rm(str(tmpdir / 'foo.txt'))
    assert not os.path.isfile(str(tmpdir / 'foo.txt'))