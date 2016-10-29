import re

from setuptools import setup


setup(
    name='pytest-mock',
    entry_points={
        'pytest11': ['pytest_mock = pytest_mock'],
    },
    py_modules=['pytest_mock', '_pytest_mock_version'],
    platforms='any',
    install_requires=[
        'pytest>=2.7',
    ],
    extras_require={
        ':python_version=="2.6" or python_version=="2.7"': ['mock'],
    },
    use_scm_version={'write_to': '_pytest_mock_version.py'},
    setup_requires=['setuptools_scm'],
    url='https://github.com/pytest-dev/pytest-mock/',
    license='MIT',
    author='Bruno Oliveira',
    author_email='nicoddemus@gmail.com',
    description='Thin-wrapper around the mock package for easier use with py.test',
    long_description=open('README.rst').read(),
    keywords="pytest mock",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Testing',
    ]
)
