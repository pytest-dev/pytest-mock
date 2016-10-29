import os
import platform
import sys
from contextlib import contextmanager

import py.code

import pytest

pytest_plugins = 'pytester'

# could not make some of the tests work on PyPy, patches are welcome!
skip_pypy = pytest.mark.skipif(platform.python_implementation() == 'PyPy',
                               reason='could not make work on pypy')


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


@pytest.mark.parametrize('name', ['MagicMock', 'PropertyMock', 'Mock', 'call', 'ANY', 'sentinel', 'mock_open'])
def test_mocker_aliases(name):
    from pytest_mock import mock_module, MockFixture

    mocker = MockFixture()
    assert getattr(mocker, name) is getattr(mock_module, name)


def test_mocker_resetall(mocker):
    listdir = mocker.patch('os.listdir')
    open = mocker.patch('os.open')

    listdir("/tmp")
    open("/tmp/foo.txt")
    listdir.assert_called_once_with("/tmp")
    open.assert_called_once_with("/tmp/foo.txt")

    mocker.resetall()

    assert not listdir.called
    assert not open.called


class TestMockerStub:
    def test_call(self, mocker):
        stub = mocker.stub()
        stub('foo', 'bar')
        stub.assert_called_once_with('foo', 'bar')

    def test_repr_with_no_name(self, mocker):
        stub = mocker.stub()
        assert not 'name' in repr(stub)

    def test_repr_with_name(self, mocker):
        test_name = 'funny walk'
        stub = mocker.stub(name=test_name)
        assert "name={0!r}".format(test_name) in repr(stub)

    def __test_failure_message(self, mocker, **kwargs):
        expected_name = kwargs.get('name') or 'mock'
        expected_message = 'Expected call: {0}()\nNot called'.format(expected_name)
        stub = mocker.stub(**kwargs)
        with pytest.raises(AssertionError) as exc_info:
            stub.assert_called_with()
        assert str(exc_info.value) == expected_message

    def test_failure_message_with_no_name(self, mocker):
        self.__test_failure_message(mocker)

    @pytest.mark.parametrize('name', (None, '', 'f', 'The Castle of aaarrrrggh'))
    def test_failure_message_with_name(self, mocker, name):
        self.__test_failure_message(mocker, name=name)


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


@skip_pypy
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


@skip_pypy
def test_instance_method_by_subclass_spy(mocker):
    from pytest_mock import mock_module

    class Base(object):

        def bar(self, arg):
            return arg * 2

    class Foo(Base):
        pass

    spy = mocker.spy(Foo, 'bar')
    foo = Foo()
    other = Foo()
    assert foo.bar(arg=10) == 20
    assert other.bar(arg=10) == 20
    calls = [mock_module.call(foo, arg=10), mock_module.call(other, arg=10)]
    assert spy.call_args_list == calls


@skip_pypy
def test_class_method_spy(mocker):
    class Foo(object):

        @classmethod
        def bar(cls, arg):
            return arg * 2

    spy = mocker.spy(Foo, 'bar')
    assert Foo.bar(arg=10) == 20
    Foo.bar.assert_called_once_with(arg=10)
    spy.assert_called_once_with(arg=10)


@skip_pypy
@pytest.mark.xfail(sys.version_info[0] == 2, reason='does not work on Python 2')
def test_class_method_subclass_spy(mocker):
    class Base(object):

        @classmethod
        def bar(self, arg):
            return arg * 2

    class Foo(Base):
        pass

    spy = mocker.spy(Foo, 'bar')
    assert Foo.bar(arg=10) == 20
    Foo.bar.assert_called_once_with(arg=10)
    spy.assert_called_once_with(arg=10)


@skip_pypy
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


@skip_pypy
def test_static_method_spy(mocker):
    class Foo(object):

        @staticmethod
        def bar(arg):
            return arg * 2

    spy = mocker.spy(Foo, 'bar')
    assert Foo.bar(arg=10) == 20
    Foo.bar.assert_called_once_with(arg=10)
    spy.assert_called_once_with(arg=10)


@skip_pypy
@pytest.mark.xfail(sys.version_info[0] == 2, reason='does not work on Python 2')
def test_static_method_subclass_spy(mocker):
    class Base(object):

        @staticmethod
        def bar(arg):
            return arg * 2

    class Foo(Base):
        pass

    spy = mocker.spy(Foo, 'bar')
    assert Foo.bar(arg=10) == 20
    Foo.bar.assert_called_once_with(arg=10)
    spy.assert_called_once_with(arg=10)


@contextmanager
def assert_traceback():
    """
    Assert that this file is at the top of the filtered traceback
    """
    try:
        yield
    except AssertionError:
        traceback = py.code.ExceptionInfo().traceback
        crashentry = traceback.getcrashentry()
        assert crashentry.path == __file__
    else:
        raise AssertionError("DID NOT RAISE")


@contextmanager
def assert_argument_introspection(left, right):
    """
    Assert detailed argument introspection is used
    """
    try:
        yield
    except AssertionError as e:
        # this may be a bit too assuming, but seems nicer then hard-coding
        import _pytest.assertion.util as util
        # NOTE: we assert with either verbose or not, depending on how our own
        #       test was run by examining sys.argv
        verbose = any(a.startswith('-v') for a in sys.argv)
        expected = '\n  '.join(util._compare_eq_iterable(left, right, verbose))
        assert expected in str(e)
    else:
        raise AssertionError("DID NOT RAISE")


@pytest.mark.skipif(sys.version_info[:2] in [(3, 3), (3, 4)],
                    reason="assert_not_called not available in python 3.3 and 3.4")
def test_assert_not_called_wrapper(mocker):
    stub = mocker.stub()
    stub.assert_not_called()
    stub()
    with assert_traceback():
        stub.assert_not_called()


def test_assert_called_with_wrapper(mocker):
    stub = mocker.stub()
    stub("foo")
    stub.assert_called_with("foo")
    with assert_traceback():
        stub.assert_called_with("bar")


def test_assert_called_once_with_wrapper(mocker):
    stub = mocker.stub()
    stub("foo")
    stub.assert_called_once_with("foo")
    stub("foo")
    with assert_traceback():
        stub.assert_called_once_with("foo")


def test_assert_called_args_with_introspection(mocker):
    stub = mocker.stub()

    complex_args = ('a', 1, set(['test']))
    wrong_args = ('b', 2, set(['jest']))

    stub(*complex_args)
    stub.assert_called_with(*complex_args)
    stub.assert_called_once_with(*complex_args)

    with assert_argument_introspection(complex_args, wrong_args):
        stub.assert_called_with(*wrong_args)
        stub.assert_called_once_with(*wrong_args)


def test_assert_called_kwargs_with_introspection(mocker):
    stub = mocker.stub()

    complex_kwargs = dict(foo={'bar': 1, 'baz': 'spam'})
    wrong_kwargs = dict(foo={'goo': 1, 'baz': 'bran'})

    stub(**complex_kwargs)
    stub.assert_called_with(**complex_kwargs)
    stub.assert_called_once_with(**complex_kwargs)

    with assert_argument_introspection(complex_kwargs, wrong_kwargs):
        stub.assert_called_with(**wrong_kwargs)
        stub.assert_called_once_with(**wrong_kwargs)


def test_assert_any_call_wrapper(mocker):
    stub = mocker.stub()
    stub("foo")
    stub("foo")
    stub.assert_any_call("foo")
    with assert_traceback():
        stub.assert_any_call("bar")


def test_assert_has_calls(mocker):
    from pytest_mock import mock_module
    stub = mocker.stub()
    stub("foo")
    stub.assert_has_calls([mock_module.call("foo")])
    with assert_traceback():
        stub.assert_has_calls([mock_module.call("bar")])


def test_monkeypatch_ini(mocker, testdir):
    # Make sure the following function actually tests something
    stub = mocker.stub()
    assert stub.assert_called_with.__module__ != stub.__module__

    testdir.makepyfile("""
        import py.code
        def test_foo(mocker):
            stub = mocker.stub()
            assert stub.assert_called_with.__module__ == stub.__module__
    """)
    testdir.makeini("""
        [pytest]
        mock_traceback_monkeypatch = false
    """)
    if hasattr(testdir, 'runpytest_subprocess'):
        result = testdir.runpytest_subprocess()
    else:
        # pytest 2.7.X
        result = testdir.runpytest()
    assert result.ret == 0


def test_parse_ini_boolean():
    import pytest_mock
    assert pytest_mock.parse_ini_boolean('True') is True
    assert pytest_mock.parse_ini_boolean('false') is False
    with pytest.raises(ValueError):
        pytest_mock.parse_ini_boolean('foo')


def test_patched_method_parameter_name(mocker):
    """Test that our internal code uses uncommon names when wrapping other
    "mock" methods to avoid conflicts with user code (#31).
    """

    class Request:
        @classmethod
        def request(cls, method, args):
            pass

    m = mocker.patch.object(Request, 'request')
    Request.request(method='get', args={'type': 'application/json'})
    m.assert_called_once_with(method='get', args={'type': 'application/json'})


def test_monkeypatch_native(testdir):
    """Automatically disable monkeypatching when --tb=native.
    """
    testdir.makepyfile("""
        def test_foo(mocker):
            stub = mocker.stub()
            stub(1, greet='hello')
            stub.assert_called_once_with(1, greet='hey')
    """)
    if hasattr(testdir, 'runpytest_subprocess'):
        result = testdir.runpytest_subprocess('--tb=native')
    else:
        # pytest 2.7.X
        result = testdir.runpytest('--tb=native')
    assert result.ret == 1
    assert 'During handling of the above exception' not in result.stdout.str()
    assert 'Differing items:' not in result.stdout.str()
    traceback_lines = [x for x in result.stdout.str().splitlines()
                       if 'Traceback (most recent call last)' in x]
    assert len(traceback_lines) == 1  # make sure there are no duplicated tracebacks (#44)
