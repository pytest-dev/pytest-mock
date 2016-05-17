import re

from setuptools import setup

with open('pytest_mock.py') as f:
    m = re.search("version = '(.*)'", f.read())
    assert m is not None
    version = m.group(1)

setup(
    name='pytest-mock',
    version=version,
    entry_points={
        'pytest11': ['pytest_mock = pytest_mock'],
    },
    py_modules=['pytest_mock'],
    platforms='any',
    install_requires=[
        'pytest>=2.7',
    ],
    extras_require={
        ':python_version=="2.6" or python_version=="2.7" or python_version=="3.2"': ['mock'],
    },
    url='https://github.com/pytest-dev/pytest-mock/',
    license='LGPL',
    author='Bruno Oliveira',
    author_email='nicoddemus@gmail.com',
    description='Thin-wrapper around the mock package for easier use with py.test',
    long_description=open('README.rst').read(),
    keywords="pytest mock",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Testing',
    ]
)
