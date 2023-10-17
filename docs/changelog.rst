==========
Changelog
==========

0.6.3
======

Added Features
---------------
* `DocumentedTypedChoiceField` now supports default Django choices


0.6.2
======

Added Features
---------------
* It is now possible to use `collectors_many`, `results_many` in `audoma_action`
* `ChoiceField` is now accepting choices as flat iterable
* `many` param in `audoma_action` has been marked as deprecated


0.6.1
=====
* Fixed dependencies issues


0.6.0
======

Major Changes
-------------

* audoma_action now only excepts subclasses of `APIException` and Django's `Http404` and `PermissionDenied` all other `Exceptions` will be raised normally
* It is now possible to create bulk endpoints using `DefaultRouter` class, #NOTE: You have to import the `DefaultRouter` from `audoma.drf.routers`
* Added custom `SerializerMethodField` which allows to pass `field` and to make it writable :ref:`Read More`<>
* Added support for all PostgreSQL fields, those are now automatically mapped for `ModelSerializer`
* Modified example generation, examples should be more accurate now
* Added possibility to define custom headers returned for each method :# TODO - ref

Bugfixes
--------
* Fixed `audoma_action` not using `ignore_view_collectors` argument
* Fixed not working partial update in `audoma_action`
