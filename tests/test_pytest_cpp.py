import os
import shutil
import sys

import pytest
from pytest_cpp.error import CppTestFailure, CppFailureRepr

from pytest_cpp.google import GoogleTestFailure, GoogleTestFacade


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
    return GoogleTestFacade()


@pytest.fixture
def dummy_failure():

    class DummyTestFailure(CppTestFailure):

        def __init__(self):
            self.lines = []
            self.file_reference = 'unknown', 0

        def get_lines(self):
            return self.lines

        def get_file_reference(self):
            return self.file_reference

    return DummyTestFailure()


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
    failure = facade.run_test(gtest_executable, 'FooTest.test_failure')
    colors = ('red', 'bold')
    assert failure.get_lines() == [
        ('Value of: 5', colors),
        ('Expected: 2 * 3', colors),
        ('Which is: 6', colors),
    ]

    assert 'gtest.cpp' in failure.get_file_reference()[0]
    assert failure.get_file_reference()[1] == 17


def test_error(facade, gtest_executable):
    failure = facade.run_test(gtest_executable, 'FooTest.test_error')
    colors = ('red', 'bold')
    assert failure.get_lines() == [
        ('unknown file', colors),
        ('C++ exception with description "unexpected exception"'
            ' thrown in the test body.', colors)]


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
    failure_repr = CppFailureRepr([dummy_failure])
    assert str(failure_repr) == 'error message\ntest_suite:20: C++ failure'

