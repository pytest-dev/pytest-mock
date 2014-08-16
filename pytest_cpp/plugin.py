import pytest

from pytest_cpp.error import CppTestFailure, CppFailureRepr, CppFailureError

from pytest_cpp.google import GoogleTestFacade


def pytest_collect_file(parent, path):
    if path.basename.startswith('test_'):
        if GoogleTestFacade.is_test_suite(str(path)):
            return CppFile(path, parent, GoogleTestFacade())


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
        failures = self.facade.run_test(str(self.fspath), self.name)
        if failures:
            raise CppFailureError(failures)

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, CppFailureError):
            return CppFailureRepr(excinfo.value.failures)

    def reportinfo(self):
        return self.fspath, 0, self.name



