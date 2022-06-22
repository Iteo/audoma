# audoma - API Automatic Documentation Maker


[![Audoma test](https://github.com/Iteo/audoma/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/Iteo/audoma/actions/workflows/test.yml)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

The main goal of this project is to make Django Rest Framework documentation easier and more automatic.
Audoma is an extension of [drf-spectacular](https://github.com/tfranzel/drf-spectacular).
Main goals of this project are:
* Make documentation more accurate, make schema include more information about views.
* Include some external library solutions as default, and document them properly.
* Make code and documentation more consistent, and avoid situations when documentation differs from code.
* Extend basic rest-framework functionalities

Getting Started
----------------

[Installation and configuration](https://audoma.readthedocs.io/en/latest/installation.html)


Features
---------
* More explicit documentation of permissions and filters/search fields.
* More ways of defining serializer_class on viewset.
* Native documentation of MoneyField, PhoneField.
* Possibility to define examples on the serializer field.
* New decorator `@audoma_action` for more consistent documentation, modifying action behavior.
* Modified `@extend_schema_field` decorator behavior, now it's updating field info, not overriding it.
* Added Bulk create/delete/update serializer mixins.


Running example application
----------------------------
You can easily test audoma functionalities with our example application.
This can be done easily by using `docker` and `docker-compose`.

You simply have to:
* clone the repository
* enter cloned project root folder
* got to `docker/`
* run `docker-compose up example_app`

Now the example application should be running under `http://localhost:8000`.
If you want to visit example documentation you should visit `/redoc` or `/swagger-ui`.

If you want to modify the example application you'll find its content inside `/audoma_examples` folder.


Development
------------
Project has defined code style and pre-commit hooks for effortless code formatting.

To setup pre-commit hooks inside repo run:
```
    $ pip install -r requirements_dev.txt
    $ pre-commit install
```
From now on your commits will fail if your changes break code conventions of the project.

To format project and apply all code style conventions run:
```
    $ ./autoformat.sh
```
This command can be triggered automatically by IDE on file save or on file change.
