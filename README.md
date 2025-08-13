SETUP INSTRUCTIONS:

1. Create virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

2. Upgrade pip and install setuptools to avoid pkg_resources warnings:
   pip install --upgrade pip setuptools

3. Install dependencies:
   pip install -r requirements.txt

4. Run migrations:
   python manage.py makemigrations banking
   python manage.py migrate

5. Create superuser:
   python manage.py createsuperuser

6. Run the server:
   python manage.py runserver

ALTERNATIVE FIX for pkg_resources warning:
If you still see pkg_resources warnings, add this to the top of manage.py:

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")

API ENDPOINTS:

Authentication:
- POST /api/auth/signup/ - User registration
- POST /api/auth/login/ - User login
- POST /api/auth/refresh/ - Token refresh

Account Holders:
- GET /api/profile/ - Get user profile

Accounts:
- GET /api/accounts/ - List user accounts
- POST /api/accounts/ - Create new account
- GET /api/accounts/{id}/ - Get account details
- PUT /api/accounts/{id}/ - Update account
- DELETE /api/accounts/{id}/ - Delete account

Transactions:
- GET /api/accounts/{id}/transactions/ - List account transactions
- POST /api/accounts/{id}/deposit/ - Deposit money
- POST /api/accounts/{id}/withdraw/ - Withdraw money

Money Transfers:
- GET /api/transfers/ - List transfers
- POST /api/transfers/ - Create money transfer

Cards:
- GET /api/cards/ - List user cards
- POST /api/cards/ - Create new card
- GET /api/cards/{id}/ - Get card details
- PUT /api/cards/{id}/
