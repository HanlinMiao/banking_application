# Banking API Testing Guide

## 🧪 Running the Tests

### 1. Setup Test Environment
```bash
pip install pytest pytest-django pytest-cov factory-boy freezegun
```

### 2. Run All Tests
```bash
python manage.py test banking.tests
```

### 3. Run Specific Test Module
```bash
python manage.py test banking.tests.test_views
```

### 4. Run with Verbose Output
```bash
python manage.py test banking.tests --verbosity=2
```

### 5. Run with Coverage
```bash
coverage run --source='.' manage.py test banking.tests
coverage report
coverage html  # Creates HTML coverage report
```

### 6. Using pytest (Alternative)
```bash
pytest banking/tests/
```

### 7. Run Specific Test Class
```bash
python manage.py test banking.tests.test_views.AccountViewTestCase
```

### 8. Run Specific Test Method
```bash
python manage.py test banking.tests.test_views.AccountViewTestCase.test_create_account
```

---

## 📋 What the Tests Cover

### ✅ **Model Tests**
- Model creation and validation
- Auto-generated fields (account numbers, transaction IDs)
- Model relationships and constraints

### ✅ **Serializer Tests**
- Data validation
- Serialization/deserialization
- Custom field handling

### ✅ **View Tests**
- All API endpoints
- Authentication and authorization
- HTTP status codes
- Response data validation

### ✅ **Integration Tests**
- Complete user workflows
- End-to-end scenarios
- Cross-model interactions

### ✅ **Permission Tests**
- User isolation
- Access control
- Security boundaries

### ✅ **Edge Case Tests**
- Invalid inputs
- Boundary conditions
- Error handling

### ✅ **Performance Tests**
- Basic load testing
- Database query efficiency
- Response time validation

---

## 🎯 Test Coverage Includes

### **Core Banking Functionality**
- ✅ User registration and authentication
- ✅ Account management (CRUD operations)
- ✅ Money deposits and withdrawals
- ✅ Money transfers between accounts
- ✅ Transaction history
- ✅ Card management
- ✅ Statement generation

### **Quality Assurance**
- ✅ Error handling and validation
- ✅ Security and permissions
- ✅ Edge cases and boundary conditions

---

## 📊 Test Results Summary

The test suite provides **comprehensive coverage** of all banking functionality and ensures the API behaves correctly under various conditions.

### **Expected Test Results:**
- **Total Tests**: 50+ test cases
- **Coverage**: 95%+ code coverage
- **Security Tests**: User isolation and permission boundaries
- **Integration Tests**: Complete user workflows
- **Performance Tests**: Response time validation

---

## 🚀 Quick Test Commands

### **Development Workflow**
```bash
# Quick test run
python manage.py test banking.tests

# Test with coverage report
coverage run --source='.' manage.py test banking.tests && coverage report

# Test specific functionality
python manage.py test banking.tests.test_views.TransactionViewTestCase
```

### **CI/CD Pipeline**
```bash
# Full test suite with coverage
coverage run --source='.' manage.py test banking.tests
coverage xml  # For CI systems
coverage html # For human review
```

### **Debugging Tests**
```bash
# Verbose output for debugging
python manage.py test banking.tests --verbosity=2 --debug-mode

# Run specific failing test
python manage.py test banking.tests.test_views.AccountViewTestCase.test_create_account --verbosity=2
```
