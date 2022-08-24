========================
Contributing to audoma
========================

| Audoma as an open source projects welcoms any form of contribution.
| Every contribution is important for us, even if it's a small one

| There are different types of contributions

* Documentation fixes, clarfications or improvements
* Creating pull requests
* Creating issues as feature requests or bug reports
* Questions that highlight inconsistencies or workflow issues

Issues
=======

| Please include to each submitted issue:

    * Brief description of the issue
    * Stack trace if there has been exception raised
    * Code which caused the issue
    * audoma/drf-spectacular/Django/DRF versions

Pull requests
==============
| We also welcome pull requests with fixes or new features.
| We strongly advice to stick to this rules, during creating pull request:

    * Test your changes before creating pull requests, your code
        has to pass the whole test suite to get merged.
        Best way will be by launching docker tests, included with project
    * Use linters included in audoma
    * Write your own tests for your changes
    * If your changes are not trivial consider create an issue first with changes proposal to get
        some early feedback
    * If you are introducing new feature, please add an example for
        this feature in audoma example application


Running unit tests
======================
| To test audoma we are using tox with multiple Django/DRF/python configurations.
| To run tests enter audoma root dir and simply use:
| `docker-compose -f docker/docker-compose.yml up tests`
| This will run the whole testing process.


Example application
====================

| Audoma has included example Django an DRF application to demonstrate its possibilities.
| Every supported feature should have its representation in example application

| To star an example application, from the root folder,
| simply run `docker-compose -f docker/docker-compose.yml up example_app`.

| As mentioned above the example application should ilustrate the every feature of audoma.
| If you are going to introduce new feature it would be really nice of you
| to include example of this feature in example application, this should
| make it easier to keep project consistent.
