import os
from setuptools import setup
import sys

requires = ['pyyaml']

# Python 2.6 does not include the argparse module.
try:
    import argparse
except ImportError:
    requires.append('argparse')

# This is quite the hack, but we don't want to import our package from here
# since that's recipe for disaster (it might have some uninstalled
# dependencies, or we might import another already installed version).
distmeta = {}
for line in open(os.path.join('python', '__init__.py')):
    try:
        field, value = (x.strip() for x in line.split('='))
    except ValueError:
        continue
    if field == '__version_info__':
        value = value.strip('[]()')
        value = '.'.join(x.strip(' \'"') for x in value.split(','))
    else:
        value = value.strip('\'"')
    distmeta[field] = value

#try:
#    with open('README.md') as readme:
#        long_description = readme.read()
#except IOError:
long_description = 'See ' + distmeta['__homepage__']

setup(
    name='bin-parser',
    version=distmeta['__version_info__'],
    description='General binary file parser',
    long_description=long_description,
    author=distmeta['__author__'],
    author_email=distmeta['__contact__'],
    url=distmeta['__homepage__'],
    license='MIT License',
    platforms=['any'],
    packages=['bin_parser', 'bin_parser_extras'],
    install_requires=requires,
    package_dir={
        'bin_parser': 'python',
        'bin_parser_extras': 'extras'
    },
    entry_points={
        'console_scripts': [
            'bin_parser = bin_parser.cli:main',
            'compare_yaml = bin_parser_extras.compare_yaml:main'
        ]
    }
)
