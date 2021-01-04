from pytest_mock.plugin import *

MockFixture = MockerFixture  # backward-compatibility only (#204)

__all__ = [
    "MockerFixture",
    "MockFixture",
    "PytestMockWarning",
    "pytest_addoption",
    "pytest_configure",
    "session_mocker",
    "package_mocker",
    "module_mocker",
    "class_mocker",
    "mocker",
]
