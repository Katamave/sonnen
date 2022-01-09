from setuptools import setup, find_packages

with open(file='LICENSE') as file:
    program_license = file.read()

setup(name='SonnenManager',
      version='0.1.1',
      packages=find_packages(exclude='tests'),
      license=program_license)
