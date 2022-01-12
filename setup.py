import codecs

from setuptools import setup, find_packages
import os

with open(file='LICENSE') as file:
    program_license = file.read()


setup(
    name='SonnenManager',
    version='0.1.0',
    packages=find_packages(exclude='tests'),
    license=program_license,
    entry_points={"console_scripts": ["sonnen=sonnen_manager.__main__:main"]}
)
