from pathlib import Path

import nox


DEPS = ("coverage", "mock", "pytest-asyncio")


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11"])
def tests(session):
    session.install(".", *DEPS)
    site_packages = Path(session.virtualenv.location, "Lib/site-packages")
    assert site_packages.is_dir(), f"{site_packages} does not exist"
    session.run(
        "coverage",
        "run",
        "--append",
        f"--source={site_packages}/pytest_mock",
        "-m",
        "pytest",
        "tests",
    )


@nox.session(python=["3.11"])
def tests_norewrite(session):
    session.install(".", *DEPS)
    session.run("pytest", "tests", "--assert=plain")


@nox.session
def docs(session):
    session.install(".", "-r", "docs/requirements.txt")
    session.run(
        "sphinx-build",
        "-W",
        "--keep-going",
        "-b",
        "html",
        "docs",
        "docs/_build/html",
        *session.posargs,
    )
