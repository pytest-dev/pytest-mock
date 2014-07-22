# simple pytest wrapper so we can execute it using "coverage run"
import tox, sys
sys.exit(tox.cmdline())
