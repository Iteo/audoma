#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.core.management import call_command
from django.test.utils import get_runner


if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "drf_example.settings"
    django.setup()
    call_command("migrate")
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    tests_to_run = ["audoma_api"]
    try:
        tests_to_run = [sys.argv[1]]
    except IndexError:
        pass
    failures = test_runner.run_tests((tests_to_run))
    sys.exit(bool(failures))
