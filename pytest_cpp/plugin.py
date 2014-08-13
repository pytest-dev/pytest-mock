import pytest

from pytest_cpp.error import CppFailure, CppFailureRepr

from pytest_cpp.gtest import GTestFacade


def pytest_collect_file(parent, path):
    if path.basename.startswith('test_'):
        if GTestFacade.is_test_suite(str(path)):
            return CppFile(path, parent, GTestFacade())


class CppFile(pytest.File):
    def __init__(self, path, parent, facade):
        pytest.File.__init__(self, path, parent)
        self.facade = facade

    def collect(self):
        for test_id in self.facade.list_tests(str(self.fspath)):
            yield CppItem(test_id, self, self.facade)


class CppItem(pytest.Item):
    def __init__(self, name, collector, facade):
        pytest.Item.__init__(self, name, collector)
        self.facade = facade

    def runtest(self):
        self.facade.run_test(str(self.fspath), self.name)

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, CppFailure):
            return CppFailureRepr(excinfo.value)

    def reportinfo(self):
        return self.fspath, 0, self.name



