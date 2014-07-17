from setuptools import setup


setup(
    name='pytest-mock',
    version='0.1.0',
    entry_points={
        'pytest11': ['pytest-mock = pytest_mock'],
    },
    modules=['pytest_mock'],
    install_requires=['pytest>=2.3.4', 'mock'],
    url='https://github.com/nicoddemus/pytest-mock/',
    license='LGPL',
    author='Bruno Oliveira',
    author_email='nicoddemus@gmail.com',
    description='Use mock package easily within py.test',
    keywords="pytest mock",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Testing',
    ]
)
