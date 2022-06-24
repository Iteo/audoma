==============
Installation
==============

Python version
==============
Audoma supports and was tested for the following versions of python:
    * python 3.7
    * python 3.8
    * python 3.9


Dependencies
============
These distributions will be installed automatically when installing audoma (if you don't have them installed already):
    * `Django`_
    * `django-rest-framework`_
    * `drf-spectacular`_
    * `exrex`_ - a regular expression generator
    * `django-phonenumber-field`_ - a phone number field package for django
    * `django-macaddress`_ - a mac address field package for django
    * `phonenumbers`_ - python package for parsing phone numbers - we use it for generating examples of phone numbers
    * `django-filter`_ - django package that allows to filter down a queryset based on a model's fields
    * `django-money`_ - django package that allows to store money and currency values in the database
    * `lorem`_ - generator for random text that looks like Latin.

.. _Django: https://www.djangoproject.com/
.. _django-rest-framework: https://www.django-rest-framework.org/
.. _exrex: https://github.com/asciimoo/exrex
.. _django-phonenumber-field: https://github.com/stefanfoulis/django-phonenumber-field
.. _django-macaddress: https://pypi.org/project/django-macaddress/
.. _phonenumbers: https://pypi.org/project/phonenumbers/
.. _django-filter: https://django-filter.readthedocs.io/en/stable/
.. _drf-spectacular: https://drf-spectacular.readthedocs.io/en/latest/
.. _django-money: https://django-money.readthedocs.io/en/latest/
.. _lorem: https://pypi.org/project/lorem/

Install and configure Audoma
============================

Using `pip`:

.. code :: bash

    $ pip install git+https://github.com/Iteo/audoma.git

After successful installation, set *AudomaAutoSchema* as a default schema for your Django Rest Framework project:

.. code :: python

    REST_FRAMEWORK = {
    # YOUR SETTINGS
    'DEFAULT_SCHEMA_CLASS': 'audoma.drf.openapi.AudomaAutoSchema',
    }


Audoma allows you to add path prefixes that should be included in schema exclusively. All you need to do is
declare a variable `SCHEMA_PATTERN_PREFIX`` in your project's `settings.py` file and add preprocessing function
`preprocess_include_path_format` as preprocessing hook in `SPECTACULAR_SETTINGS dictionary`` as in the example below.


.. code :: python

    SCHEMA_PATTERN_PREFIX = 'api'

    SPECTACULAR_SETTINGS = {
        ...
        'PREPROCESSING_HOOKS': ['audoma.hooks.preprocess_include_path_format'],
        # OTHER SETTINGS
    }
