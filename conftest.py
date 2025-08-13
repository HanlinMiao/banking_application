import pytest
from django.test import override_settings

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Grant database access to all tests.
    """
    pass

@override_settings(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
)
class DatabaseTestCase:
    """Base test case with in-memory database"""
    pass
