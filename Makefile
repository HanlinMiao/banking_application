.PHONY: test test-verbose test-coverage test-specific clean

test:
	python manage.py test banking.tests

test-verbose:
	python manage.py test banking.tests --verbosity=2

test-coverage:
	coverage run --source='.' manage.py test banking.tests
	coverage report
	coverage html

test-specific:
	python manage.py test banking.tests.test_views

test-models:
	python manage.py test banking.tests.test_models

test-permissions:
	python manage.py test banking.tests.test_permissions

test-integration:
	python manage.py test banking.tests.test_integration

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf htmlcov/
	rm -f .coverage

# Run all tests with coverage
test-all: test-coverage
