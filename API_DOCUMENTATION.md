# API_DOCUMENTATION.md

# Banking REST API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

### Token Lifetime
- **Access Token**: 60 minutes
- **Refresh Token**: 24 hours

---

## 🔐 Authentication Endpoints

### User Registration

**POST** `/auth/signup/`

Register a new user and create an account holder profile.

**Request Body:**
```json
{
  "user": {
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  },
  "phone_number": "+1234567890",
  "address": "123 Main Street, City, State, 12345",
  "date_of_birth": "1990-01-15"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "phone_number": "+1234567890",
  "address": "123 Main Street, City, State, 12345",
  "date_of_birth": "1990-01-15"
}
```

### User Login

**POST** `/auth/login/`

Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Token Refresh

**POST** `/auth/refresh/`

Get a new access token using refresh token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 👤 Profile Management

### Get User Profile

**GET** `/profile/`

Get the authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "phone_number": "+1234567890",
  "address": "123 Main Street, City, State, 12345",
  "date_of_birth": "1990-01-15"
}
```

---

## 🏦 Account Management

### List Accounts

**GET** `/accounts/`

Get all accounts belonging to the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "account_number": "ACC1234567890",
      "account_type": "CHECKING",
      "balance": "1500.00",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "account_number": "ACC0987654321",
      "account_type": "SAVINGS",
      "balance": "5000.00",
      "is_active": true,
      "created_at": "2024-01-15T11:00:00Z"
    }
  ]
}
```

### Create Account

**POST** `/accounts/`

Create a new bank account.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "account_type": "CHECKING"
}
```

**Available Account Types:**
- `CHECKING`
- `SAVINGS`
- `BUSINESS`

**Response (201 Created):**
```json
{
  "id": 3,
  "account_number": "ACC5555444433",
  "account_type": "CHECKING",
  "balance": "0.00",
  "is_active": true,
  "created_at": "2024-01-15T12:00:00Z"
}
```

### Get Account Details

**GET** `/accounts/{account_id}/`

Get details of a specific account.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "account_number": "ACC1234567890",
  "account_type": "CHECKING",
  "balance": "1500.00",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Update Account

**PUT** `/accounts/{account_id}/`

Update account information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "account_type": "SAVINGS",
  "is_active": true
}
```

### Delete Account

**DELETE** `/accounts/{account_id}/`

Deactivate an account (soft delete).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

---

## 💰 Transaction Operations

### Deposit Money

**POST** `/accounts/{account_id}/deposit/`

Deposit money into an account.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "amount": 500.00,
  "description": "Salary deposit"
}
```

**Response (200 OK):**
```json
{
  "message": "Deposit successful",
  "new_balance": "2000.00"
}
```

### Withdraw Money

**POST** `/accounts/{account_id}/withdraw/`

Withdraw money from an account.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "amount": 200.00,
  "description": "ATM withdrawal"
}
```

**Response (200 OK):**
```json
{
  "message": "Withdrawal successful",
  "new_balance": "1800.00"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Insufficient funds"
}
```

### Get Transaction History

**GET** `/accounts/{account_id}/transactions/`

Get transaction history for an account.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of transactions per page (default: 20)

**Response (200 OK):**
```json
{
  "count": 15,
  "next": "http://localhost:8000/api/accounts/1/transactions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 5,
      "transaction_id": "TXN9876543210",
      "account": 1,
      "transaction_type": "DEPOSIT",
      "amount": "500.00",
      "description": "Salary deposit",
      "reference_number": "",
      "balance_after": "2000.00",
      "created_at": "2024-01-15T14:30:00Z"
    },
    {
      "id": 4,
      "transaction_id": "TXN1234567890",
      "account": 1,
      "transaction_type": "WITHDRAWAL",
      "amount": "200.00",
      "description": "ATM withdrawal",
      "reference_number": "",
      "balance_after": "1500.00",
      "created_at": "2024-01-15T13:15:00Z"
    }
  ]
}
```

**Transaction Types:**
- `DEPOSIT`: Money deposited into account
- `WITHDRAWAL`: Money withdrawn from account
- `TRANSFER_IN`: Money received from transfer
- `TRANSFER_OUT`: Money sent via transfer

---

## 🔄 Money Transfers

### Create Money Transfer

**POST** `/transfers/`

Transfer money between accounts.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "from_account": 1,
  "to_account": 2,
  "amount": 300.00,
  "description": "Transfer to savings"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "transfer_id": "TRF1234567890",
  "from_account": 1,
  "to_account": 2,
  "from_account_number": "ACC1234567890",
  "to_account_number": "ACC0987654321",
  "amount": "300.00",
  "description": "Transfer to savings",
  "status": "COMPLETED",
  "created_at": "2024-01-15T15:00:00Z",
  "completed_at": "2024-01-15T15:00:01Z"
}
```

### List Transfers

**GET** `/transfers/`

Get transfer history for the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "transfer_id": "TRF1234567890",
      "from_account": 1,
      "to_account": 2,
      "from_account_number": "ACC1234567890",
      "to_account_number": "ACC0987654321",
      "amount": "300.00",
      "description": "Transfer to savings",
      "status": "COMPLETED",
      "created_at": "2024-01-15T15:00:00Z",
      "completed_at": "2024-01-15T15:00:01Z"
    }
  ]
}
```

**Transfer Status:**
- `PENDING`: Transfer initiated but not completed
- `COMPLETED`: Transfer successfully completed
- `FAILED`: Transfer failed due to error

---

## 💳 Card Management

### Create Card

**POST** `/cards/`

Issue a new card for an account.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "account": 1,
  "card_type": "DEBIT",
  "cardholder_name": "John Doe",
  "credit_limit": null
}
```

**Card Types:**
- `DEBIT`: Debit card
- `CREDIT`: Credit card

**Response (201 Created):**
```json
{
  "id": 1,
  "card_number": "4123456789012345",
  "masked_card_number": "****-****-****-2345",
  "card_type": "DEBIT",
  "cardholder_name": "John Doe",
  "expiry_date": "2029-01-15",
  "is_active": true,
  "credit_limit": null,
  "created_at": "2024-01-15T16:00:00Z"
}
```

### List Cards

**GET** `/cards/`

Get all cards belonging to the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "card_number": "4123456789012345",
      "masked_card_number": "****-****-****-2345",
      "card_type": "DEBIT",
      "cardholder_name": "John Doe",
      "expiry_date": "2029-01-15",
      "is_active": true,
      "credit_limit": null,
      "created_at": "2024-01-15T16:00:00Z"
    }
  ]
}
```

### Get Card Details

**GET** `/cards/{card_id}/`

Get details of a specific card.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "card_number": "4123456789012345",
  "masked_card_number": "****-****-****-2345",
  "card_type": "DEBIT",
  "cardholder_name": "John Doe",
  "expiry_date": "2029-01-15",
  "is_active": true,
  "credit_limit": null,
  "created_at": "2024-01-15T16:00:00Z"
}
```

### Update Card

**PUT** `/cards/{card_id}/`

Update card information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "is_active": false,
  "credit_limit": 5000.00
}
```

### Delete Card

**DELETE** `/cards/{card_id}/`

Deactivate a card.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

---

## 📄 Statements

### Generate Statement

**POST** `/accounts/{account_id}/generate-statement/`

Generate an account statement for a specific period.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "account": 1,
  "account_number": "ACC1234567890",
  "statement_period_start": "2024-01-01",
  "statement_period_end": "2024-01-31",
  "opening_balance": "1000.00",
  "closing_balance": "1800.00",
  "total_deposits": "1500.00",
  "total_withdrawals": "700.00",
  "generated_at": "2024-02-01T10:00:00Z",
  "transactions": [
    {
      "id": 1,
      "transaction_id": "TXN1234567890",
      "transaction_type": "DEPOSIT",
      "amount": "500.00",
      "description": "Salary deposit",
      "created_at": "2024-01-15T14:30:00Z"
    },
    {
      "id": 2,
      "transaction_id": "TXN0987654321",
      "transaction_type": "WITHDRAWAL",
      "amount": "200.00",
      "description": "ATM withdrawal",
      "created_at": "2024-01-20T12:15:00Z"
    }
  ]
}
```

### List Statements

**GET** `/accounts/{account_id}/statements/`

Get all statements for an account.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "account": 1,
      "account_number": "ACC1234567890",
      "statement_period_start": "2024-01-01",
      "statement_period_end": "2024-01-31",
      "opening_balance": "1000.00",
      "closing_balance": "1800.00",
      "total_deposits": "1500.00",
      "total_withdrawals": "700.00",
      "generated_at": "2024-02-01T10:00:00Z"
    }
  ]
}
```

---

## 🚨 Error Responses

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **204 No Content**: Request successful, no content returned
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Access denied
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "error": "Error message describing what went wrong",
  "details": {
    "field_name": ["Specific field error message"]
  }
}
```

### Common Error Examples

**Insufficient Funds:**
```json
{
  "error": "Insufficient funds"
}
```

**Invalid Token:**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

**Validation Error:**
```json
{
  "amount": ["This field is required."],
  "account_type": ["Invalid choice. Choose from: CHECKING, SAVINGS, BUSINESS"]
}
```

---

## 📝 Usage Examples

### Complete User Journey with curl

```bash
# 1. Register user
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "username": "testuser",
      "email": "test@example.com",
      "first_name": "Test",
      "last_name": "User",
      "password": "testpass123",
      "password_confirm": "testpass123"
    },
    "phone_number": "+1234567890",
    "address": "123 Test St",
    "date_of_birth": "1990-01-01"
  }'

# 2. Login and get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access'])")

# 3. Create account
curl -X POST http://localhost:8000/api/accounts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"account_type": "CHECKING"}'

# 4. Deposit money
curl -X POST http://localhost:8000/api/accounts/1/deposit/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"amount": 1000, "description": "Initial deposit"}'

# 5. Check balance
curl -X GET http://localhost:8000/api/accounts/1/ \
  -H "Authorization: Bearer $TOKEN"
```

### JavaScript/Fetch Example

```javascript
// Login function
async function login(username, password) {
  const response = await fetch('http://localhost:8000/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  return data.access;
}

// Create account function
async function createAccount(accountType) {
  const token = localStorage.getItem('access_token');

  const response = await fetch('http://localhost:8000/api/accounts/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ account_type: accountType })
  });

  return response.json();
}

// Deposit money function
async function deposit(accountId, amount, description) {
  const token = localStorage.getItem('access_token');

  const response = await fetch(`http://localhost:8000/api/accounts/${accountId}/deposit/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ amount, description })
  });

  return response.json();
}
```

---

## 🔗 Rate Limiting

Currently, no rate limiting is implemented in the development version. For production deployment, consider implementing rate limiting to prevent abuse:

- Authentication endpoints: 5 requests per minute per IP
- Transaction endpoints: 10 requests per minute per user
- General API endpoints: 100 requests per minute per user

---

## 📚 Additional Resources

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [JWT Authentication Guide](https://django-rest-framework-simplejwt.readthedocs.io/)
- [API Testing with Postman](https://www.postman.com/)
- [curl Command Reference](https://curl.se/docs/manpage.html)
