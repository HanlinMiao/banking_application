from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from banking.models import AccountHolder, Account, Transaction
from decimal import Decimal
from datetime import date

class PermissionTestCase(TestCase):
    """Test security and permission restrictions"""

    def setUp(self):
        # Create first user
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.account_holder1 = AccountHolder.objects.create(
            user=self.user1,
            phone_number='+1111111111',
            address='111 Test St',
            date_of_birth=date(1990, 1, 1)
        )
        self.account1 = Account.objects.create(
            account_holder=self.account_holder1,
            account_type='CHECKING',
            balance=Decimal('1000.00')
        )

        # Create second user
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.account_holder2 = AccountHolder.objects.create(
            user=self.user2,
            phone_number='+2222222222',
            address='222 Test St',
            date_of_birth=date(1991, 2, 2)
        )
        self.account2 = Account.objects.create(
            account_holder=self.account_holder2,
            account_type='SAVINGS',
            balance=Decimal('500.00')
        )

        self.client = APIClient()

    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_user_can_only_see_own_accounts(self):
        """Test that users can only access their own accounts"""
        token = self.get_token_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get('/api/accounts/')
        self.assertEqual(response.status_code, 200)

        accounts = response.data['results']
        self.assertEqual(len(accounts), 1)
        self.assertEqual(accounts[0]['id'], self.account1.id)

    def test_user_cannot_access_other_user_account(self):
        """Test that user cannot access another user's account details"""
        token = self.get_token_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Try to access user2's account
        response = self.client.get(f'/api/accounts/{self.account2.id}/')
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_deposit_to_other_user_account(self):
        """Test that user cannot deposit to another user's account"""
        token = self.get_token_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        deposit_data = {
            'amount': 100.00,
            'description': 'Unauthorized deposit attempt'
        }

        response = self.client.post(
            f'/api/accounts/{self.account2.id}/deposit/',
            deposit_data,
            format='json'
        )
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_transfer_from_other_user_account(self):
        """Test that user cannot transfer from another user's account"""
        token = self.get_token_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        transfer_data = {
            'from_account': self.account2.id,  # User2's account
            'to_account': self.account1.id,    # User1's account
            'amount': 100.00,
            'description': 'Unauthorized transfer attempt'
        }

        response = self.client.post('/api/transfers/', transfer_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_user_cannot_see_other_user_transactions(self):
        """Test that user cannot see another user's transactions"""
        token = self.get_token_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get(f'/api/accounts/{self.account2.id}/transactions/')
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied"""
        # No authentication credentials
        response = self.client.get('/api/accounts/')
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/api/accounts/', {'account_type': 'CHECKING'})
        self.assertEqual(response.status_code, 401)
