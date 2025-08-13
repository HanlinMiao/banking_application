from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from banking.models import AccountHolder, Account, Transaction, MoneyTransfer
from decimal import Decimal
from datetime import date

class EdgeCaseTestCase(TestCase):
    """Test edge cases and error conditions"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.account_holder = AccountHolder.objects.create(
            user=self.user,
            phone_number='+1234567890',
            address='123 Test St',
            date_of_birth=date(1990, 1, 1)
        )
        self.account = Account.objects.create(
            account_holder=self.account_holder,
            account_type='CHECKING',
            balance=Decimal('1000.00')
        )

        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_zero_amount_deposit(self):
        """Test deposit with zero amount"""
        deposit_data = {
            'amount': 0.00,
            'description': 'Zero deposit'
        }

        response = self.client.post(
            f'/api/accounts/{self.account.id}/deposit/',
            deposit_data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Amount must be positive', response.data['error'])

    def test_negative_amount_withdrawal(self):
        """Test withdrawal with negative amount"""
        withdraw_data = {
            'amount': -50.00,
            'description': 'Negative withdrawal'
        }

        response = self.client.post(
            f'/api/accounts/{self.account.id}/withdraw/',
            withdraw_data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Amount must be positive', response.data['error'])

    def test_extremely_large_amount(self):
        """Test transaction with extremely large amount"""
        deposit_data = {
            'amount': 999999999999.99,
            'description': 'Large deposit'
        }

        response = self.client.post(
            f'/api/accounts/{self.account.id}/deposit/',
            deposit_data,
            format='json'
        )
        # Should handle large numbers gracefully
        self.assertIn(response.status_code, [200, 400])

    def test_decimal_precision(self):
        """Test decimal precision handling"""
        deposit_data = {
            'amount': 123.456,  # More than 2 decimal places
            'description': 'Precision test'
        }

        response = self.client.post(
            f'/api/accounts/{self.account.id}/deposit/',
            deposit_data,
            format='json'
        )
        # Should round to 2 decimal places or handle appropriately
        self.assertIn(response.status_code, [200, 400])

    def test_nonexistent_account_operations(self):
        """Test operations on non-existent account"""
        nonexistent_id = 99999

        deposit_data = {
            'amount': 100.00,
            'description': 'Deposit to nonexistent account'
        }

        response = self.client.post(
            f'/api/accounts/{nonexistent_id}/deposit/',
            deposit_data,
            format='json'
        )
        self.assertEqual(response.status_code, 404)

    def test_concurrent_transactions(self):
        """Test handling of potential race conditions"""
        # This is a simplified test - in production, you'd use threading
        initial_balance = self.account.balance

        # Simulate multiple simultaneous withdrawals
        withdraw_data = {
            'amount': 600.00,
            'description': 'Concurrent withdrawal'
        }

        # First withdrawal
        response1 = self.client.post(
            f'/api/accounts/{self.account.id}/withdraw/',
            withdraw_data,
            format='json'
        )

        # Second withdrawal (should fail due to insufficient funds)
        response2 = self.client.post(
            f'/api/accounts/{self.account.id}/withdraw/',
            withdraw_data,
            format='json'
        )

        # One should succeed, one should fail
        success_count = sum(1 for r in [response1, response2] if r.status_code == 200)
        self.assertEqual(success_count, 1)

    def test_invalid_account_type(self):
        """Test account creation with invalid account type"""
        account_data = {
            'account_type': 'INVALID_TYPE'
        }

        response = self.client.post('/api/accounts/', account_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_transfer_to_same_account(self):
        """Test transfer to the same account"""
        transfer_data = {
            'from_account': self.account.id,
            'to_account': self.account.id,
            'amount': 100.00,
            'description': 'Self transfer'
        }

        response = self.client.post('/api/transfers/', transfer_data, format='json')
        self.assertEqual(response.status_code, 400)
