import os
import shutil
import sys

import pytest
from pytest_cpp.boost import BoostTestFacade
from pytest_cpp.error import CppTestFailure, CppFailureRepr
from pytest_cpp.google import GoogleTestFacade


pytest_plugins = 'pytester'

@pytest.fixture
def suites(testdir):

    class Suites:

        def get(self, name, new_name=None):
            if not new_name:
                new_name = name
            if sys.platform.startswith('win'):
                name += '.exe'
                new_name += '.exe'
            source = os.path.join(os.path.dirname(__file__), name)
            dest = testdir.tmpdir.join(new_name)
            shutil.copy(str(source), str(dest))
            return str(dest)

    return Suites()



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


@pytest.mark.parametrize('facade, name, expected', [
    (GoogleTestFacade(), 'gtest', [
        'FooTest.test_success',
        'FooTest.test_failure',
        'FooTest.test_error',
        'FooTest.DISABLED_test_disabled'
    ]),
    (BoostTestFacade(), 'boost_success', ['boost_success']),
    (BoostTestFacade(), 'boost_error', ['boost_error']),
])
def test_list_tests(facade, name, expected, suites):
    obtained = facade.list_tests(suites.get(name))
    assert obtained == expected


@pytest.mark.parametrize('facade, name, other_name', [
    (GoogleTestFacade(), 'gtest', 'boost_success'),
    (BoostTestFacade(), 'boost_success', 'gtest'),
])
def test_is_test_suite(facade, name, other_name, suites, tmpdir):
    assert facade.is_test_suite(suites.get(name))
    assert not facade.is_test_suite(suites.get(other_name))
    tmpdir.ensure('foo.txt')
    assert not facade.is_test_suite(str(tmpdir.join('foo.txt')))


@pytest.mark.parametrize('facade, name, test_id', [
    (GoogleTestFacade(), 'gtest', 'FooTest.test_success'),
    (BoostTestFacade(), 'boost_success', '<unused>'),
])
def test_success(facade, name, test_id, suites):
    assert facade.run_test(suites.get(name), test_id) is None


def test_google_failure(suites):
    facade = GoogleTestFacade()
    failure = facade.run_test(suites.get('gtest'), 'FooTest.test_failure')
    colors = ('red', 'bold')
    assert failure.get_lines() == [
        ('Value of: 5', colors),
        ('Expected: 2 * 3', colors),
        ('Which is: 6', colors),
    ]

    assert failure.get_file_reference() == ('gtest.cpp', 17)


def test_google_error(suites):
    facade = GoogleTestFacade()
    failure = facade.run_test(suites.get('gtest'), 'FooTest.test_error')
    colors = ('red', 'bold')
    assert failure.get_lines() == [
        ('unknown file', colors),
        ('C++ exception with description "unexpected exception"'
            ' thrown in the test body.', colors)]


def test_google_disabled(suites):
    facade = GoogleTestFacade()
    with pytest.raises(pytest.skip.Exception):
        facade.run_test(suites.get('gtest'), 'FooTest.DISABLED_test_disabled')


def test_boost_failure(suites):
    facade = BoostTestFacade()
    failures = facade.run_test(suites.get('boost_failure'), '<unused>')
    assert len(failures) == 2

    fail1, fail2 = failures
    colors = ('red', 'bold')
    assert fail1.get_lines() == [('check 2 * 3 == 5 failed', colors)]
    assert fail1.get_file_reference() == ("boost_failure.cpp", 8)

    assert fail2.get_lines() == [('check 2 - 1 == 0 failed', colors)]
    assert fail2.get_file_reference() == ("boost_failure.cpp", 14)


def test_boost_error(suites):
    facade = BoostTestFacade()
    failures = facade.run_test(suites.get('boost_error'), '<unused>')
    assert len(failures) == 2

    fail1, fail2 = failures
    colors = ('red', 'bold')
    assert fail1.get_lines() == [
        ('std::runtime_error: unexpected exception', colors)]
    assert fail1.get_file_reference() == ("unknown location", 0)

    assert fail2.get_lines() == [
        ('std::runtime_error: another unexpected exception', colors)]
    assert fail2.get_file_reference() == ("unknown location", 0)


def test_google_run(testdir, suites):
    result = testdir.runpytest('-v', suites.get('gtest', 'test_gtest'))
    result.stdout.fnmatch_lines([
        '*test_success PASSED*',
        '*test_failure FAILED*',
        '*test_error FAILED*',
        '*test_disabled SKIPPED*',
    ])


def test_boost_run(testdir, suites):
    all_names = ['boost_success', 'boost_error', 'boost_failure']
    all_files = [suites.get(n, 'test_' + n) for n in all_names]
    result = testdir.runpytest('-v', *all_files)
    result.stdout.fnmatch_lines([
        '*boost_success PASSED*',
        '*boost_error FAILED*',
        '*boost_failure FAILED*',
    ])


def test_cpp_failure_repr(dummy_failure):
    dummy_failure.lines = [('error message', {'red'})]
    dummy_failure.file_reference = 'test_suite', 20
    failure_repr = CppFailureRepr([dummy_failure])
    assert str(failure_repr) == 'error message\ntest_suite:20: C++ failure'


def test_cpp_files_option(testdir, suites):
    testdir.makeini('''
        [pytest]
        cpp_files = gtest* boost*
    ''')
    suites.get('boost_success')
    suites.get('gtest')
    result = testdir.runpytest('--collect-only')
    result.stdout.fnmatch_lines([
        "*<CppItem 'boost_success'>*",
        "*<CppItem 'FooTest.test_success'>*",
    ])

