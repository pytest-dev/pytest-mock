from setuptools import setup

from io import open

setup(
    name='pytest-mock',
    entry_points={
        'pytest11': ['pytest_mock = pytest_mock'],
    },
    py_modules=['pytest_mock', '_pytest_mock_version'],
    platforms='any',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=[
        'pytest>=2.7',
        'mock;python_version<"3.0"',
    ],
    use_scm_version={'write_to': '_pytest_mock_version.py'},
    setup_requires=['setuptools_scm'],
    url='https://github.com/pytest-dev/pytest-mock/',
    license='MIT',
    author='Bruno Oliveira',
    author_email='nicoddemus@gmail.com',
    description='Thin-wrapper around the mock package for easier use with py.test',
    long_description=open('README.rst', encoding='utf-8').read(),
    keywords="pytest mock",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Testing',
    ]
)
