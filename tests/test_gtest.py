import os
import shutil
import sys

import pytest

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


def test_list_tests(facade, gtest_executable):
    obtained = facade.list_tests(gtest_executable)
    assert obtained == [
        'FooTest.test_success',
        'FooTest.test_failure',
        'FooTest.test_error',
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


@pytest.mark.usefixtures('gtest_executable')
def test_run(testdir):
    result = testdir.runpytest('-v')
    result.stdout.fnmatch_lines([
        '*test_success PASSED*',
        '*test_failure FAILED*',
        '*test_error FAILED*',
    ])