import os

import pytest

class UnixFS(object):
    @classmethod
    def rm(cls, filename):
        os.remove(filename)

    @classmethod
    def ls(cls, path):
        return os.listdir(path)


@pytest.fixture
def check_unix_fs_mocked(tmpdir, mock):
    def check(mocked_rm, mocked_ls):
        assert mocked_rm is os.remove
        assert mocked_ls is os.listdir

        file_name = tmpdir / 'foo.txt'
        file_name.ensure()

        UnixFS.rm(str(file_name))
        mocked_rm.assert_called_once_with(str(file_name))
        assert os.path.isfile(str(file_name))

        mocked_ls.return_value = ['bar.txt']
        assert UnixFS.ls(str(tmpdir)) == ['bar.txt']
        mocked_ls.assert_called_once_with(str(tmpdir))

        mock.stopall()

        assert UnixFS.ls(str(tmpdir)) == ['foo.txt']
        UnixFS.rm(str(file_name))
        assert not os.path.isfile(str(file_name))

    return check


def mock_using_patch_object(mock):
    return mock.patch.object(os, 'remove'), mock.patch.object(os, 'listdir')


def mock_using_patch(mock):
    return mock.patch('os.remove'), mock.patch('os.listdir')


def mock_using_patch_multiple(mock):
    from mock import DEFAULT

    r = mock.patch.multiple('os', remove=DEFAULT, listdir=DEFAULT)
    return r['remove'], r['listdir']


@pytest.mark.parametrize('mock_fs', [mock_using_patch_object, mock_using_patch,
                                     mock_using_patch_multiple],
)
def test_fixture(mock_fs, mock, check_unix_fs_mocked):
    mocked_rm, mocked_ls = mock_fs(mock)
    check_unix_fs_mocked(mocked_rm, mocked_ls)
