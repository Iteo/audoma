import pathlib

from setuptools import (
    find_packages,
    setup,
)


here = pathlib.Path(__file__).parent.resolve()

name = "audoma"
description = "API Automatic Documentation Maker - DRF-SPECTACULAR wrapper"


with open(here / "requirements.txt") as f:
    required = f.read().splitlines()


python_versions = ("3.7", "3.8", "3.9")
django_versions = ("2.2", "3.0", "3.1", "3.2")

python_classifiers = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
] + ["Programming Language :: Python :: {}".format(v) for v in python_versions]

django_classifiers = [
    "Framework :: Django",
] + ["Framework :: Django :: {}".format(v) for v in django_versions]


setup(
    name=name,
    version="1.1.0",
    packages=find_packages(),
    install_requires=required,
    description=description,
    author="ITEO",
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Environment :: Web Environment",
        "Topic :: Documentation",
        "Topic :: Software Development :: Code Generators",
    ]
    + python_classifiers
    + django_classifiers,
)
