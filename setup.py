from setuptools import setup


setup(
    name="pytest-cpp",
    version='0.1.0',
    packages=['pytest_cpp'],
    entry_points={
        'pytest11': ['cpp = pytest_cpp.plugin'],
    },
    install_requires=['pytest', 'colorama'],

    # metadata for upload to PyPI
    author="Bruno Oliveira",
    author_email="nicoddemus@gmail.com",
    description="Use pytest's runner to discover and execute C++ tests",
    long_description=open('README.rst').read(),
    license="MIT",
    keywords="pytest test unittest",
    url="http://github.com/nicoddemus/pytest-cpp",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: C++',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
    ],
)
