================================
Testing And Example Application
================================

Running example application
==============================
| You can easily test audoma functionalities with our example application.
| From the root folder, go to `docker/` and run `docker-compose up example_app`.
| You can explore the possibilities of audoma documentation maker as it shows all functionalities.

Running unit tests
======================
Go to `docker/` and run
`docker-compose run --rm example_app bash -c "cd audoma_examples/drf_example && python manage.py test"`


Modyfying Example Application
===============================

| Example Application should illustrate every feature which has been introduced into audoma.
| This means that any change made in the audoma code should have its example here.
| This allows a better understanding of audoma features and will allow testing more cautiously.
