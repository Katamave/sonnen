from setuptools import setup, find_packages
import os


def read_file(file_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, file_path), encoding='utf-8') as fr:
        return fr.read()


def get_version(file_path):
    for line in read_file(file_path).splitlines():
        if line.startswith('__version__'):
            delimiter = '"' if '"' in line else "'"
            return line.split(delimiter)[1]
    else:
        raise RuntimeError('__version__ not found!')


with open(file='LICENSE') as file:
    program_license = file.read()


setup(
    name='SonnenManager',
    version=get_version('sonnen_manager/__init__.py'),
    packages=find_packages(exclude='tests'),
    license=program_license,
    entry_points={"console_scripts": ["sonnen=sonnen_manager.__main__:main"]}
)
