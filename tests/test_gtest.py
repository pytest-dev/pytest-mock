import os
import shutil
import sys

import pytest
from pytest_cpp.error import CppFailure, CppFailureRepr

from pytest_cpp.gtest import GTestError, GTestFacade


pytest_plugins = 'pytester'

@pytest.fixture
def gtest_executable(testdir):
    name = 'gtest'
    if sys.platform.startswith('win'):
        name += '.exe'
    source = os.path.join(os.path.dirname(__file__), name)
    dest = testdir.tmpdir.join('test_' + name)
    shutil.copy(str(source), str(dest))
    return str(dest)


@pytest.fixture
def other_executable():
    return r'ipconfig.exe'


@pytest.fixture
def facade():
    return GTestFacade()


@pytest.fixture
def dummy_failure():

    class DummyFailure(CppFailure):

        def __init__(self):
            self.lines = []
            self.file_reference = 'unknown', 0

        def get_lines(self):
            return self.lines

        def get_file_reference(self):
            return self.file_reference

    return DummyFailure()


def test_list_tests(facade, gtest_executable):
    obtained = facade.list_tests(gtest_executable)
    assert obtained == [
        'FooTest.test_success',
        'FooTest.test_failure',
        'FooTest.test_error',
        'FooTest.DISABLED_test_disabled',
    ]


def test_is_gtest(facade, gtest_executable, other_executable, tmpdir):
    assert facade.is_test_suite(gtest_executable)
    assert not facade.is_test_suite(other_executable)
    tmpdir.ensure('foo.txt')
    assert not facade.is_test_suite(str(tmpdir.join('foo.txt')))


def test_success(facade, gtest_executable):
    assert facade.run_test(gtest_executable, 'FooTest.test_success') is None


def test_failure(facade, gtest_executable):
    with pytest.raises(GTestError) as e:
        facade.run_test(gtest_executable, 'FooTest.test_failure')
    assert 'Expected: 2 * 3' in str(e.value)


def test_error(facade, gtest_executable):
    with pytest.raises(GTestError) as e:
        facade.run_test(gtest_executable, 'FooTest.test_error')
    assert '"unexpected exception"' in str(e.value)


def test_disabled(facade, gtest_executable):
    with pytest.raises(pytest.skip.Exception):
        facade.run_test(gtest_executable, 'FooTest.DISABLED_test_disabled')


@pytest.mark.usefixtures('gtest_executable')
def test_run(testdir):
    result = testdir.runpytest('-v')
    result.stdout.fnmatch_lines([
        '*test_success PASSED*',
        '*test_failure FAILED*',
        '*test_error FAILED*',
        '*test_disabled SKIPPED*',
    ])


def test_cpp_failure_repr(dummy_failure):
    dummy_failure.lines = [('error message', {'red'})]
    dummy_failure.file_reference = 'test_suite', 20
    failure_repr = CppFailureRepr(dummy_failure)
    assert str(failure_repr) == 'error message\ntest_suite:20: C++ failure'

