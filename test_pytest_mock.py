import os

import pytest


pytest_plugins = 'pytester'


class UnixFS(object):
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


@pytest.fixture
def check_unix_fs_mocked(tmpdir, mocker):
    """
    performs a standard test in a UnixFS, assuming that both `os.remove` and
    `os.listdir` have been mocked previously.
    """

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

        mocker.stopall()

        assert UnixFS.ls(str(tmpdir)) == ['foo.txt']
        UnixFS.rm(str(file_name))
        assert not os.path.isfile(str(file_name))

    return check


def mock_using_patch_object(mocker):
    return mocker.patch.object(os, 'remove'), mocker.patch.object(os, 'listdir')


def mock_using_patch(mocker):
    return mocker.patch('os.remove'), mocker.patch('os.listdir')


def mock_using_patch_multiple(mocker):
    from pytest_mock import mock_module

    r = mocker.patch.multiple('os', remove=mock_module.DEFAULT,
                              listdir=mock_module.DEFAULT)
    return r['remove'], r['listdir']


@pytest.mark.parametrize('mock_fs', [mock_using_patch_object, mock_using_patch,
                                     mock_using_patch_multiple],
)
def test_mock_patches(mock_fs, mocker, check_unix_fs_mocked):
    """
    Installs mocks into `os` functions and performs a standard testing of
    mock functionality. We parametrize different mock methods to ensure
    all (intended, at least) mock API is covered.
    """
    # mock it twice on purpose to ensure we unmock it correctly later
    mock_fs(mocker)
    mocked_rm, mocked_ls = mock_fs(mocker)
    check_unix_fs_mocked(mocked_rm, mocked_ls)


def test_mock_patch_dict(mocker):
    """
    Testing
    :param mock:
    """
    x = {'original': 1}
    mocker.patch.dict(x, values=[('new', 10)], clear=True)
    assert x == {'new': 10}
    mocker.stopall()
    assert x == {'original': 1}


def test_mock_fixture_is_deprecated(testdir):
    """
    Test that a warning emitted when using deprecated "mock" fixture.
    """
    testdir.makepyfile('''
        import warnings
        import os
        warnings.simplefilter('always')

        def test_foo(mock, tmpdir):
            mock.patch('os.listdir', return_value=['mocked'])
            assert os.listdir(str(tmpdir)) == ['mocked']
            mock.stopall()
            assert os.listdir(str(tmpdir)) == []
    ''')
    result = testdir.runpytest('-s')
    result.stderr.fnmatch_lines(['*"mock" fixture has been deprecated*'])


def test_deprecated_mock(mock, tmpdir):
    """
    Use backward-compatibility-only mock fixture to ensure complete coverage.
    """
    mock.patch('os.listdir', return_value=['mocked'])
    assert os.listdir(str(tmpdir)) == ['mocked']
    mock.stopall()
    assert os.listdir(str(tmpdir)) == []


def test_mocker_has_magic_mock_class_as_attribute_for_instantiation():
    from pytest_mock import mock_module, MockFixture

    mocker = MockFixture()
    assert isinstance(mocker.MagicMock(), mock_module.MagicMock)


def test_mocker_has_mock_class_as_attribute_for_instantiation():
    from pytest_mock import mock_module, MockFixture

    mocker = MockFixture()
    assert isinstance(mocker.Mock(), mock_module.Mock)


def test_mocker_stub(mocker):
    def foo(on_something):
        on_something('foo', 'bar')

    stub = mocker.stub()

    foo(stub)
    stub.assert_called_once_with('foo', 'bar')


def test_instance_method_spy(mocker):
    class Foo(object):

        def bar(self, arg):
            return arg * 2

    foo = Foo()
    other = Foo()
    spy = mocker.spy(foo, 'bar')
    assert foo.bar(arg=10) == 20
    assert other.bar(arg=10) == 20
    foo.bar.assert_called_once_with(arg=10)
    spy.assert_called_once_with(arg=10)


def test_instance_method_by_class_spy(mocker):
    from pytest_mock import mock_module

    class Foo(object):

        def bar(self, arg):
            return arg * 2

    spy = mocker.spy(Foo, 'bar')
    foo = Foo()
    other = Foo()
    assert foo.bar(arg=10) == 20
    assert other.bar(arg=10) == 20
    calls = [mock_module.call(foo, arg=10), mock_module.call(other, arg=10)]
    assert spy.call_args_list == calls


def test_class_method_spy(mocker):
    class Foo(object):

        @classmethod
        def bar(cls, arg):
            return arg * 2

    spy = mocker.spy(Foo, 'bar')
    assert Foo.bar(arg=10) == 20
    Foo.bar.assert_called_once_with(arg=10)
    spy.assert_called_once_with(arg=10)


def test_class_method_with_metaclass_spy(mocker):
    class MetaFoo(type):
        pass

    class Foo(object):

        __metaclass__ = MetaFoo

        @classmethod
        def bar(cls, arg):
            return arg * 2

    spy = mocker.spy(Foo, 'bar')
    assert Foo.bar(arg=10) == 20
    Foo.bar.assert_called_once_with(arg=10)
    spy.assert_called_once_with(arg=10)


def test_static_method_spy(mocker):
    class Foo(object):

        @staticmethod
        def bar(arg):
            return arg * 2

    spy = mocker.spy(Foo, 'bar')
    assert Foo.bar(arg=10) == 20
    Foo.bar.assert_called_once_with(arg=10)
    spy.assert_called_once_with(arg=10)
