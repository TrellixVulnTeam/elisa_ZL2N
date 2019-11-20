"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
from version import get_version


here = path.dirname(__file__)

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='elisa',
    src_root='src',
    version=get_version(),

    description='Eclipsing Binary Modeling Software',
    long_description='For more information visit https://github.com/mikecokina/elisa/',

    # The project's main homepage.
    url='https://github.com/mikecokina/elisa',

    # Author details
    author='Michal Cokina, Miroslav Fedurco',
    author_email='mikecokina@gmail.com, mirofedurco@gmail.com',

    # Choose your license
    license='GPLv2',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Astronomy',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='eclipsing binaries astronomy analysis analytics physic',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(where='src', exclude=["single_system"]),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'astropy==2.0.2',
        'cycler==0.10.0',
        'matplotlib==2.1.0',
        'numpy==1.16.2',
        'pandas==0.24.0',
        'py==1.4.34',
        'pyparsing==2.2.0',
        'pypex==0.1.0',
        'pytest==3.2.3',
        'python-dateutil==2.6.1',
        'pytz==2017.2',
        'scipy==1.0.0',
        'six==1.11.0'
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': [],
        'test': ['coverage'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'elisa': [
            'passband/*',
            'conf/*',
            'schema_registry/*'
        ],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
        ],
    },
)
