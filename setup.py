import pathlib

import pkg_resources
from setuptools import (
    find_packages,
    setup,
)


here = pathlib.Path(__file__).parent.resolve()

name = "audoma"
description = "API Automatic Documentation Maker - DRF-SPECTACULAR wrapper"
long_description = (here / "README.md").read_text()


def get_reqiuired_packages():
    with open(here / "requirements.txt") as f:
        required = f.read().splitlines()
    try:
        django_version = pkg_resources.get_distribution("django").version
    except pkg_resources.DistributionNotFound:
        django_version = None
    if django_version and django_version < "3.1":
        required.append("django-jsonfield")
    return required


python_versions = ("3.7", "3.8", "3.9")
django_versions = ("2.2", "3.0", "3.1", "3.2", "4.0")

python_classifiers = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
] + ["Programming Language :: Python :: {}".format(v) for v in python_versions]

django_classifiers = [
    "Framework :: Django",
] + ["Framework :: Django :: {}".format(v) for v in django_versions]


setup(
    name=name,
    version="0.4.6",
    packages=find_packages(),
    install_requires=get_reqiuired_packages(),
    description=description,
    long_description_content_type="text/markdown",
    long_description=long_description,
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
