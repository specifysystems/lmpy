# -*- coding: utf-8 -*-
"""Setup module for lmpy."""
from setuptools import setup, find_packages
import versioneer


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='specify-lmpy',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Package of commonly used and shared Lifemapper objects and tools',
    long_description=readme,
    author='Specify Systems Lifemapper Team',
    author_email='cjgrady@ku.edu',
    url='https://github.com/specifysystems/lmpy',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'defusedxml',
        'dendropy>=4.0.0',
        'numpy>=1.11.0',
        'gdal',
        'requests',
        'rtree',
    ],
)
