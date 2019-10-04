from io import open

from setuptools import setup, find_packages

setup(
    name="pytest-mock",
    entry_points={"pytest11": ["pytest_mock = pytest_mock"]},
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    platforms="any",
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=["pytest>=2.7", 'mock;python_version<"3.0"'],
    use_scm_version={"write_to": "src/pytest_mock/_version.py"},
    setup_requires=["setuptools_scm"],
    url="https://github.com/pytest-dev/pytest-mock/",
    license="MIT",
    author="Bruno Oliveira",
    author_email="nicoddemus@gmail.com",
    description="Thin-wrapper around the mock package for easier use with py.test",
    long_description=open("README.rst", encoding="utf-8").read(),
    keywords="pytest mock",
    extras_require={"dev": ["pre-commit", "tox"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Testing",
    ],
)
