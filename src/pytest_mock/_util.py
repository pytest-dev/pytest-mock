_mock_module = None


def get_mock_module(config):
    """
    Import and return the actual "mock" module. By default this is
    "unittest.mock", but the user can force to always use "mock" using
    the mock_use_standalone_module ini option.
    """
    global _mock_module
    if _mock_module is None:
        use_standalone_module = parse_ini_boolean(
            config.getini("mock_use_standalone_module")
        )
        if use_standalone_module:
            import mock  # noqa

            _mock_module = mock
        else:
            import unittest.mock

            _mock_module = unittest.mock

    return _mock_module


#: Spellings pytest itself accepts for an ini boolean, see ``_pytest.config._strtobool``.
_TRUTHY = frozenset({"y", "yes", "t", "true", "on", "1"})
_FALSY = frozenset({"n", "no", "f", "false", "off", "0"})


def parse_ini_boolean(value: bool | str) -> bool:
    if isinstance(value, bool):
        return value
    normalized = value.strip().lower()
    if normalized in _TRUTHY:
        return True
    if normalized in _FALSY:
        return False
    raise ValueError(f"unknown string for bool: {value!r}")
