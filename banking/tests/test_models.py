from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta
from banking.models import AccountHolder, Account, Transaction, MoneyTransfer, Card, Statement

class AccountHolderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_create_account_holder(self):
        account_holder = AccountHolder.objects.create(
            user=self.user,
            phone_number='+1234567890',
            address='123 Test St',
            date_of_birth=date(1990, 1, 1)
        )

        self.assertEqual(account_holder.user, self.user)
        self.assertEqual(account_holder.phone_number, '+1234567890')
        self.assertEqual(str(account_holder), 'Test User - test@example.com')

    def test_account_holder_required_fields(self):
        with self.assertRaises(Exception):
            AccountHolder.objects.create(
                user=self.user,
                # Missing required fields
            )

class AccountModelTest(TestCase):
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

    def test_create_account(self):
        account = Account.objects.create(
            account_holder=self.account_holder,
            account_type='CHECKING'
        )

        self.assertEqual(account.account_holder, self.account_holder)
        self.assertEqual(account.account_type, 'CHECKING')
        self.assertEqual(account.balance, Decimal('0.00'))
        self.assertTrue(account.is_active)
        self.assertTrue(account.account_number.startswith('ACC'))
        self.assertEqual(len(account.account_number), 13)  # ACC + 10 chars

    def test_account_number_generation(self):
        account1 = Account.objects.create(
            account_holder=self.account_holder,
            account_type='CHECKING'
        )
        account2 = Account.objects.create(
            account_holder=self.account_holder,
            account_type='SAVINGS'
        )

        self.assertNotEqual(account1.account_number, account2.account_number)
        self.assertTrue(account1.account_number.startswith('ACC'))
        self.assertTrue(account2.account_number.startswith('ACC'))

class TransactionModelTest(TestCase):
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

    def test_create_transaction(self):
        transaction = Transaction.objects.create(
            account=self.account,
            transaction_type='DEPOSIT',
            amount=Decimal('100.00'),
            description='Test deposit',
            balance_after=Decimal('1100.00')
        )

        self.assertEqual(transaction.account, self.account)
        self.assertEqual(transaction.transaction_type, 'DEPOSIT')
        self.assertEqual(transaction.amount, Decimal('100.00'))
        self.assertTrue(transaction.transaction_id.startswith('TXN'))

    def test_transaction_id_generation(self):
        transaction1 = Transaction.objects.create(
            account=self.account,
            transaction_type='DEPOSIT',
            amount=Decimal('100.00'),
            balance_after=Decimal('1100.00')
        )
        transaction2 = Transaction.objects.create(
            account=self.account,
            transaction_type='WITHDRAWAL',
            amount=Decimal('50.00'),
            balance_after=Decimal('1050.00')
        )

        self.assertNotEqual(transaction1.transaction_id, transaction2.transaction_id)

class MoneyTransferModelTest(TestCase):
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
        self.from_account = Account.objects.create(
            account_holder=self.account_holder,
            account_type='CHECKING',
            balance=Decimal('1000.00')
        )
        self.to_account = Account.objects.create(
            account_holder=self.account_holder,
            account_type='SAVINGS',
            balance=Decimal('500.00')
        )

    def test_create_money_transfer(self):
        transfer = MoneyTransfer.objects.create(
            from_account=self.from_account,
            to_account=self.to_account,
            amount=Decimal('250.00'),
            description='Test transfer'
        )

        self.assertEqual(transfer.from_account, self.from_account)
        self.assertEqual(transfer.to_account, self.to_account)
        self.assertEqual(transfer.amount, Decimal('250.00'))
        self.assertEqual(transfer.status, 'PENDING')
        self.assertTrue(transfer.transfer_id.startswith('TRF'))
