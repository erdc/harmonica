#!/usr/bin/env python
import versioneer
from setuptools import setup

# Don't proceed with 'unknown' in version
version_dict = versioneer.get_versions()
if version_dict['error']:
    raise RuntimeError(version_dict["error"])

install_requires = [
    'argparse',
    'pytides',
    'netCDF4',
    'numpy',
    'pandas',
    'xarray',
]

extras_require = {
    'build' : [
        'setuptools',
    ],
    'tests' : [],
}

extras_require['all'] = sorted(set(sum(extras_require.values(), [])))

entry_points = [
    'harmonica = harmonica.cli.main:main',
    'harmonica-constituents = harmonica.cli.main_constituents:main',
    'harmonica-deconstruct = harmonica.cli.main_deconstruct:main',
    'harmonica-reconstruct = harmonica.cli.main_reconstruct:main',
    'harmonica-resources = harmonica.cli.main_resources:main',
]

setup(
    name='harmonica',
    version=version_dict['version'],
    cmdclass=versioneer.get_cmdclass(),
    description="Worldwide amplitude, phase, and speed for standard tidal constituents and tidal time series " \
        "reconstruction and deconstruction.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Kevin Winters",
    author_email='Kevin.D.Winters@erdc.dren.mil',
    maintainer="ERS Environmental Simulation",
    url='https://github.com/erdc/harmonica',
    packages=['harmonica', 'harmonica.cli'],
    #scripts=[],
    entry_points={
        'console_scripts': entry_points
    },
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=extras_require['tests'],
    keywords='harmonica',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering'
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires="!=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*"
)
