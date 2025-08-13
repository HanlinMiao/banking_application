from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from banking.models import AccountHolder, Account, Transaction, MoneyTransfer, Card
from decimal import Decimal
from datetime import date, timedelta
import json

class AuthenticationTestCase(APITestCase):
    def setUp(self):
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')

        self.user_data = {
            'user': {
                'username': 'testuser',
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'password': 'testpass123',
                'password_confirm': 'testpass123'
            },
            'phone_number': '+1234567890',
            'address': '123 Test St',
            'date_of_birth': '1990-01-01'
        }

    def test_user_signup(self):
        response = self.client.post(self.signup_url, self.user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(AccountHolder.objects.filter(user__username='testuser').exists())

    def test_user_signup_invalid_data(self):
        invalid_data = self.user_data.copy()
        invalid_data['user']['password_confirm'] = 'wrongpass'

        response = self.client.post(self.signup_url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        # First create a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AccountViewTestCase(APITestCase):
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

        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.accounts_url = reverse('account-list')

    def test_create_account(self):
        account_data = {
            'account_type': 'CHECKING'
        }

        response = self.client.post(self.accounts_url, account_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['account_type'], 'CHECKING')
        self.assertTrue(response.data['account_number'].startswith('ACC'))

    def test_list_accounts(self):
        # Create test accounts
        Account.objects.create(
            account_holder=self.account_holder,
            account_type='CHECKING'
        )
        Account.objects.create(
            account_holder=self.account_holder,
            account_type='SAVINGS'
        )

        response = self.client.get(self.accounts_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_account_detail(self):
        account = Account.objects.create(
            account_holder=self.account_holder,
            account_type='CHECKING'
        )

        url = reverse('account-detail', kwargs={'pk': account.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], account.id)

    def test_unauthorized_access(self):
        # Remove authorization
        self.client.credentials()

        response = self.client.get(self.accounts_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class TransactionViewTestCase(APITestCase):
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

        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_deposit_money(self):
        url = reverse('deposit', kwargs={'account_id': self.account.id})
        deposit_data = {
            'amount': 500.00,
            'description': 'Test deposit'
        }

        response = self.client.post(url, deposit_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Deposit successful')

        # Refresh account from database
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('1500.00'))

        # Check transaction was created
        self.assertTrue(Transaction.objects.filter(
            account=self.account,
            transaction_type='DEPOSIT',
            amount=Decimal('500.00')
        ).exists())

    def test_withdraw_money(self):
        url = reverse('withdraw', kwargs={'account_id': self.account.id})
        withdraw_data = {
            'amount': 300.00,
            'description': 'Test withdrawal'
        }

        response = self.client.post(url, withdraw_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Withdrawal successful')

        # Refresh account from database
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('700.00'))

    def test_withdraw_insufficient_funds(self):
        url = reverse('withdraw', kwargs={'account_id': self.account.id})
        withdraw_data = {
            'amount': 1500.00,  # More than balance
            'description': 'Test withdrawal'
        }

        response = self.client.post(url, withdraw_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient funds', response.data['error'])

    def test_deposit_negative_amount(self):
        url = reverse('deposit', kwargs={'account_id': self.account.id})
        deposit_data = {
            'amount': -100.00,
            'description': 'Invalid deposit'
        }

        response = self.client.post(url, deposit_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Amount must be positive', response.data['error'])

    def test_list_transactions(self):
        # Create test transactions
        Transaction.objects.create(
            account=self.account,
            transaction_type='DEPOSIT',
            amount=Decimal('500.00'),
            balance_after=Decimal('1500.00')
        )
        Transaction.objects.create(
            account=self.account,
            transaction_type='WITHDRAWAL',
            amount=Decimal('200.00'),
            balance_after=Decimal('1300.00')
        )

        url = reverse('transactions', kwargs={'account_id': self.account.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

class MoneyTransferViewTestCase(APITestCase):
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

        # Create another user for transfer testing
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.account_holder2 = AccountHolder.objects.create(
            user=self.user2,
            phone_number='+0987654321',
            address='456 Test Ave',
            date_of_birth=date(1991, 2, 2)
        )

        self.from_account = Account.objects.create(
            account_holder=self.account_holder,
            account_type='CHECKING',
            balance=Decimal('1000.00')
        )
        self.to_account = Account.objects.create(
            account_holder=self.account_holder2,
            account_type='SAVINGS',
            balance=Decimal('500.00')
        )

        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.transfers_url = reverse('transfers')

    def test_money_transfer(self):
        transfer_data = {
            'from_account': self.from_account.id,
            'to_account': self.to_account.id,
            'amount': 250.00,
            'description': 'Test transfer'
        }

        response = self.client.post(self.transfers_url, transfer_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check balances updated
        self.from_account.refresh_from_db()
        self.to_account.refresh_from_db()

        self.assertEqual(self.from_account.balance, Decimal('750.00'))
        self.assertEqual(self.to_account.balance, Decimal('750.00'))

        # Check transfer record created
        transfer = MoneyTransfer.objects.get(id=response.data['id'])
        self.assertEqual(transfer.status, 'COMPLETED')
        self.assertIsNotNone(transfer.completed_at)

    def test_transfer_insufficient_funds(self):
        transfer_data = {
            'from_account': self.from_account.id,
            'to_account': self.to_account.id,
            'amount': 1500.00,  # More than balance
            'description': 'Test transfer'
        }

        response = self.client.post(self.transfers_url, transfer_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transfer_same_account(self):
        transfer_data = {
            'from_account': self.from_account.id,
            'to_account': self.from_account.id,  # Same account
            'amount': 100.00,
            'description': 'Test transfer'
        }

        response = self.client.post(self.transfers_url, transfer_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_transfers(self):
        # Create test transfer
        MoneyTransfer.objects.create(
            from_account=self.from_account,
            to_account=self.to_account,
            amount=Decimal('100.00'),
            status='COMPLETED'
        )

        response = self.client.get(self.transfers_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class CardViewTestCase(APITestCase):
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
            account_type='CHECKING'
        )

        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.cards_url = reverse('card-list')

    def test_create_card(self):
        card_data = {
            'account': self.account.id,
            'card_type': 'DEBIT',
            'cardholder_name': 'Test User'
        }

        response = self.client.post(self.cards_url, card_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['card_type'], 'DEBIT')
        self.assertEqual(response.data['cardholder_name'], 'Test User')
        self.assertIn('masked_card_number', response.data)

    def test_list_cards(self):
        # Create test card
        Card.objects.create(
            account=self.account,
            card_type='DEBIT',
            cardholder_name='Test User',
            expiry_date=date.today() + timedelta(days=1825),
            cvv='123'
        )

        response = self.client.get(self.cards_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class StatementViewTestCase(APITestCase):
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

        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_generate_statement(self):
        # Create some transactions
        Transaction.objects.create(
            account=self.account,
            transaction_type='DEPOSIT',
            amount=Decimal('500.00'),
            balance_after=Decimal('1500.00')
        )
        Transaction.objects.create(
            account=self.account,
            transaction_type='WITHDRAWAL',
            amount=Decimal('200.00'),
            balance_after=Decimal('1300.00')
        )

        url = reverse('generate-statement', kwargs={'account_id': self.account.id})
        statement_data = {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }

        response = self.client.post(url, statement_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('opening_balance', response.data)
        self.assertIn('closing_balance', response.data)
        self.assertIn('total_deposits', response.data)
        self.assertIn('total_withdrawals', response.data)
        self.assertIn('transactions', response.data)
