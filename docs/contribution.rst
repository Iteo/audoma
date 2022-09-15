========================
Contributing to audoma
========================

| Audoma as an open source project welcomes any form of contribution.
| Every contribution is important for us, even if it's a small one

| There are different types of contributions

* Documentation fixes, clarifications or improvements
* Creating pull requests
* Creating issues as feature requests or bug reports
* Questions that highlight inconsistencies or workflow issues

Issues
=======

| Please include to each submitted issue:
    * Brief description of the issue
    * Stack trace if there has been an exception raised
    * Code that caused the issue
    * audoma/drf-spectacular/Django/DRF versions

Pull requests
==============
| We also welcome pull requests with fixes or new features.
| We strongly advise you to stick to these rules, during creating pull requests:
    * Test your changes before creating pull requests, your code has to pass the whole test suite to get merged. The best way will be by launching docker tests, included with the project
    * Use linters included in audoma
    * Write your own tests for your changes
    * If your changes are not trivial consider creating an issue first with changes proposal to get some early feedback
    * If you are introducing a new feature, please add an example for this feature in audoma example application

Running unit tests
======================
| To test audoma we are using tox with multiple Django/DRF/python configurations.
| To run tests enter audoma root dir and simply use:
| `docker-compose -f docker/docker-compose.yml up tests`
| This will run the whole testing process.

Example application
====================
| Audoma has included an example Django/DRF application to demonstrate its possibilities.
| Every supported feature should have its representation in an example application

| To star an example application, from the root folder,
| simply run `docker-compose -f docker/docker-compose.yml up example_app`.

| As mentioned above the example application should illustrate every feature of audoma.
| If you are going to introduce a new feature it would be nice of you
| to include an example of this feature in the example application, this should
| make it easier to keep the project consistent.
