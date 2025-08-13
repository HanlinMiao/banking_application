#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'banking_service.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    # Run specific test modules
    if len(sys.argv) > 1:
        test_labels = sys.argv[1:]
    else:
        test_labels = [
            'banking.tests.test_models',
            'banking.tests.test_serializers',
            'banking.tests.test_views',
            'banking.tests.test_integration',
            'banking.tests.test_permissions',
            'banking.tests.test_edge_cases',
            'banking.tests.test_performance'
        ]

    failures = test_runner.run_tests(test_labels)

    if failures:
        sys.exit(bool(failures))
