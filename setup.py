from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

name = 'audoma'
description = 'API Automatic Documentation Maker - YASG/SPECTACULAR wrapper'


with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name=name,
    version='1.0.0',
    packages=find_packages(''),
    install_requires=required
)