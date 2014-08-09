from __future__ import unicode_literals

import pytest

from gtest import GTestError, GTestFacade


@pytest.fixture
def gtest():
    return r'x:\pytest-cpp\test_gtest.exe'


@pytest.fixture
def other_executable():
    return r'ipconfig.exe'


@pytest.fixture
def facade():
    return GTestFacade()


def test_list_tests(facade, gtest):
    obtained = facade.list_tests(gtest)
    assert obtained == [
        'FooTest.test_success',
        'FooTest.test_failure',
        'FooTest.test_error',
    ]


def test_is_gtest(facade, gtest, other_executable, tmpdir):
    assert facade.is_test_suite(gtest)
    assert not facade.is_test_suite(other_executable)
    tmpdir.ensure('foo.txt')
    assert not facade.is_test_suite(str(tmpdir.join('foo.txt')))


def test_success(facade, gtest):
    assert facade.run_test(gtest, 'FooTest.test_success') is None


def test_failure(facade, gtest):
    with pytest.raises(GTestError) as e:
        facade.run_test(gtest, 'FooTest.test_failure')
    assert 'Expected: 2 * 3' in str(e.value)


def test_error(facade, gtest):
    with pytest.raises(GTestError) as e:
        facade.run_test(gtest, 'FooTest.test_error')
    assert '"unexpected exception"' in str(e.value)