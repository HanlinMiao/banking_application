# RUNNING THE TESTS

1. Setup test environment:
   pip install pytest pytest-django pytest-cov factory-boy freezegun

2. Run all tests:
   python manage.py test banking.tests

3. Run specific test module:
   python manage.py test banking.tests.test_views

4. Run with verbose output:
   python manage.py test banking.tests --verbosity=2

5. Run with coverage:
   coverage run --source='.' manage.py test banking.tests
   coverage report
   coverage html  # Creates HTML coverage report

6. Using pytest (alternative):
   pytest banking/tests/

7. Run specific test class:
   python manage.py test banking.tests.test_views.AccountViewTestCase

8. Run specific test method:
   python manage.py test banking.tests.test_views.AccountViewTestCase.test_create_account

# WHAT THE TESTS COVER:

✅ Model Tests:
   - Model creation and validation
   - Auto-generated fields (account numbers, transaction IDs)
   - Model relationships and constraints

✅ Serializer Tests:
   - Data validation
   - Serialization/deserialization
   - Custom field handling

✅ View Tests:
   - All API endpoints
   - Authentication and authorization
   - HTTP status codes
   - Response data validation

✅ Integration Tests:
   - Complete user workflows
   - End-to-end scenarios
   - Cross-model interactions

✅ Permission Tests:
   - User isolation
   - Access control
   - Security boundaries

✅ Edge Case Tests:
   - Invalid inputs
   - Boundary conditions
   - Error handling

✅ Performance Tests:
   - Basic load testing
   - Database query efficiency
   - Response time validation

# TEST COVERAGE INCLUDES:
- User registration and authentication
- Account management (CRUD operations)
- Money deposits and withdrawals
- Money transfers between accounts
- Transaction history
- Card management
- Statement generation
- Error handling and validation
- Security and permissions
- Edge cases and boundary conditions

The test suite provides comprehensive coverage of all banking functionality
and ensures the API behaves correctly under various conditions.
