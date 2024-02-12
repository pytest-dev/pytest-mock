from setuptools import find_packages
from setuptools import setup

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    platforms="any",
    package_data={
        "pytest_mock": ["py.typed"],
    },
    use_scm_version={"write_to": "src/pytest_mock/_version.py"},
)
