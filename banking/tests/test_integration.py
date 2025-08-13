from django.test import TransactionTestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from banking.models import AccountHolder, Account, Transaction, MoneyTransfer
from decimal import Decimal
from datetime import date

class BankingWorkflowIntegrationTest(TransactionTestCase):
    """Integration tests for complete banking workflows"""

    def setUp(self):
        self.client = APIClient()

    def test_complete_banking_workflow(self):
        """Test complete user journey from signup to transactions"""

        # 1. User signup
        signup_data = {
            'user': {
                'username': 'integrationuser',
                'email': 'integration@example.com',
                'first_name': 'Integration',
                'last_name': 'User',
                'password': 'testpass123',
                'password_confirm': 'testpass123'
            },
            'phone_number': '+1234567890',
            'address': '123 Integration St',
            'date_of_birth': '1990-01-01'
        }

        response = self.client.post('/api/auth/signup/', signup_data, format='json')
        self.assertEqual(response.status_code, 201)

        # 2. User login
        login_data = {
            'username': 'integrationuser',
            'password': 'testpass123'
        }

        response = self.client.post('/api/auth/login/', login_data, format='json')
        self.assertEqual(response.status_code, 200)

        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 3. Create checking account
        account_data = {'account_type': 'CHECKING'}
        response = self.client.post('/api/accounts/', account_data, format='json')
        self.assertEqual(response.status_code, 201)

        checking_account_id = response.data['id']

        # 4. Create savings account
        account_data = {'account_type': 'SAVINGS'}
        response = self.client.post('/api/accounts/', account_data, format='json')
        self.assertEqual(response.status_code, 201)

        savings_account_id = response.data['id']

        # 5. Deposit money into checking
        deposit_data = {
            'amount': 1000.00,
            'description': 'Initial deposit'
        }
        response = self.client.post(
            f'/api/accounts/{checking_account_id}/deposit/',
            deposit_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['new_balance'], '1000.00')

        # 6. Transfer money from checking to savings
        transfer_data = {
            'from_account': checking_account_id,
            'to_account': savings_account_id,
            'amount': 300.00,
            'description': 'Transfer to savings'
        }
        response = self.client.post('/api/transfers/', transfer_data, format='json')
        self.assertEqual(response.status_code, 201)

        # 7. Verify account balances
        response = self.client.get('/api/accounts/')
        self.assertEqual(response.status_code, 200)

        accounts = response.data['results']
        checking_account = next(acc for acc in accounts if acc['id'] == checking_account_id)
        savings_account = next(acc for acc in accounts if acc['id'] == savings_account_id)

        self.assertEqual(checking_account['balance'], '700.00')
        self.assertEqual(savings_account['balance'], '300.00')

        # 8. Create a card for checking account
        card_data = {
            'account': checking_account_id,
            'card_type': 'DEBIT',
            'cardholder_name': 'Integration User'
        }
        response = self.client.post('/api/cards/', card_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['card_type'], 'DEBIT')

        # 9. Check transaction history
        response = self.client.get(f'/api/accounts/{checking_account_id}/transactions/')
        self.assertEqual(response.status_code, 200)

        transactions = response.data['results']
        self.assertEqual(len(transactions), 2)  # Deposit + Transfer out

        # 10. Generate statement
        statement_data = {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }
        response = self.client.post(
            f'/api/accounts/{checking_account_id}/generate-statement/',
            statement_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('transactions', response.data)

        # 11. Withdraw money
        withdraw_data = {
            'amount': 100.00,
            'description': 'ATM withdrawal'
        }
        response = self.client.post(
            f'/api/accounts/{checking_account_id}/withdraw/',
            withdraw_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['new_balance'], '600.00')
