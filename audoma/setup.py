import os
import re
import shutil
import sys

from setuptools import setup


name = 'audoma'
package = 'audoma'
description = 'API Automatic Documentation Maker - YASG/SPECTACULAR wrapper'

with open('requirements.txt') as fh:
    requirements = [r for r in fh.read().split('\n') if not r.startswith('#')]