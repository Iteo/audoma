from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

name = 'audoma'
description = 'API Automatic Documentation Maker - YASG/SPECTACULAR wrapper'


setup(
    name=name,
    version='1.0.0',
    packages=find_packages('audoma')
)