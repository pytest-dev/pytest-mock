# wrapper script around py.test so coverage can run py.test from inside tox
import sys
import pytest
sys.exit(pytest.main())