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
            source = os.path.join(os.path.dirname(__file__), exe_name(name))
            dest = testdir.tmpdir.join(exe_name(new_name))
            shutil.copy(str(source), str(dest))
            return str(dest)

    return Suites()


def exe_name(name):
    if sys.platform.startswith('win'):
        name += '.exe'
    return name


def assert_outcomes(result, expected_outcomes):
    __tracebackhide__ = True
    obtained = []
    for test_id, _ in expected_outcomes:
        rep = result.matchreport(test_id, "pytest_runtest_logreport")
        obtained.append((test_id, rep.outcome))
    assert expected_outcomes == obtained


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
    failures = facade.run_test(suites.get('gtest'), 'FooTest.test_failure')
    assert len(failures) == 2
    colors = ('red', 'bold')
    assert failures[0].get_lines() == [
        ('Value of: 5', colors),
        ('Expected: 2 * 3', colors),
        ('Which is: 6', colors),
    ]
    assert failures[0].get_file_reference() == ('gtest.cpp', 17)

    assert failures[1].get_lines() == [
        ('Value of: 15', colors),
        ('Expected: 2 * 6', colors),
        ('Which is: 12', colors),
    ]
    assert failures[1].get_file_reference() == ('gtest.cpp', 18)


def test_google_error(suites):
    facade = GoogleTestFacade()
    failures = facade.run_test(suites.get('gtest'), 'FooTest.test_error')
    assert len(failures) == 1
    colors = ('red', 'bold')
    assert failures[0].get_lines() == [
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
    result = testdir.inline_run('-v', suites.get('gtest', 'test_gtest'))
    assert_outcomes(result, [
        ('FooTest.test_success', 'passed'),
        ('FooTest.test_failure', 'failed'),
        ('FooTest.test_error', 'failed'),
        ('FooTest.DISABLED_test_disabled', 'skipped'),
    ])


def test_boost_run(testdir, suites):
    all_names = ['boost_success', 'boost_error', 'boost_failure']
    all_files = [suites.get(n, 'test_' + n) for n in all_names]
    result = testdir.inline_run('-v', *all_files)
    assert_outcomes(result, [
        ('test_boost_success', 'passed'),
        ('test_boost_error', 'failed'),
        ('test_boost_failure', 'failed'),
    ])


def test_cpp_failure_repr(dummy_failure):
    dummy_failure.lines = [('error message', {'red'})]
    dummy_failure.file_reference = 'test_suite', 20
    failure_repr = CppFailureRepr([dummy_failure])
    assert str(failure_repr) == 'error message\ntest_suite:20: C++ failure'


def test_cpp_files_option(testdir, suites):
    suites.get('boost_success')
    suites.get('gtest')
    
    result = testdir.inline_run('--collect-only')
    reps = result.getreports()
    assert len(reps) == 1
    assert reps[0].result == []

    testdir.makeini('''
        [pytest]
        cpp_files = gtest* boost*
    ''')
    result = testdir.inline_run('--collect-only')
    assert len(result.matchreport(exe_name('boost_success')).result) == 1
    assert len(result.matchreport(exe_name('gtest')).result) == 4


