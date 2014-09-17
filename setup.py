import sys

from setuptools import setup


dependencies = ['pytest>=2.4']
if sys.version_info < (3, 3):
    dependencies.append('mock')

setup(
    name='pytest-mock',
    version='0.4.0',
    entry_points={
        'pytest11': ['pytest-mock = pytest_mock'],
    },
    py_modules=['pytest_mock'],
    platforms='any',
    install_requires=dependencies,
    url='https://github.com/nicoddemus/pytest-mock/',
    license='LGPL',
    author='Bruno Oliveira',
    author_email='nicoddemus@gmail.com',
    description='Thin-wrapper around the mock package for easier use with py.test',
    long_description=open('README.rst').read(),
    keywords="pytest mock",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Testing',
    ]
)
