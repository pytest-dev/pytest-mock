# simple pytest wrapper so we can execute it using "coverage run"
import pytest, sys
sys.exit(pytest.main())
