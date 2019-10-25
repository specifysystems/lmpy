# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='lmpy',
    version='1.0.0',
    description='Package of commonly used and shared Lifemapper objects',
    long_description=readme,
    author='Lifemapper Team',
    author_email='cjgrady@ku.edu',
    url='https://github.com/lifemapper/lmpy',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'dendropy>=4.0.0',
        'matplotlib',
        'numpy>=1.11.0',
        'scipy>=1.0.0']
)
