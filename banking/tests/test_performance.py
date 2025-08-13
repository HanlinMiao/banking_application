from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from banking.models import AccountHolder, Account, Transaction
from decimal import Decimal
from datetime import date
import time

class PerformanceTestCase(TestCase):
    """Basic performance tests"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='perfuser',
            email='perf@example.com',
            password='testpass123'
        )
        self.account_holder = AccountHolder.objects.create(
            user=self.user,
            phone_number='+1234567890',
            address='123 Perf St',
            date_of_birth=date(1990, 1, 1)
        )
        self.account = Account.objects.create(
            account_holder=self.account_holder,
            account_type='CHECKING',
            balance=Decimal('10000.00')
        )

        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_bulk_transaction_creation(self):
        """Test creating many transactions"""
        start_time = time.time()

        # Create 100 transactions
        for i in range(100):
            Transaction.objects.create(
                account=self.account,
                transaction_type='DEPOSIT',
                amount=Decimal('10.00'),
                balance_after=self.account.balance + Decimal('10.00') * (i + 1)
            )

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time (adjust threshold as needed)
        self.assertLess(duration, 5.0, "Bulk transaction creation took too long")

        # Verify all transactions were created
        transaction_count = Transaction.objects.filter(account=self.account).count()
        self.assertEqual(transaction_count, 100)

    def test_transaction_list_pagination(self):
        """Test paginated transaction listing performance"""
        # Create test transactions
        for i in range(50):
            Transaction.objects.create(
                account=self.account,
                transaction_type='DEPOSIT',
                amount=Decimal('10.00'),
                balance_after=self.account.balance + Decimal('10.00') * (i + 1)
            )

        start_time = time.time()

        response = self.client.get(f'/api/accounts/{self.account.id}/transactions/')

        end_time = time.time()
        duration = end_time - start_time

        self.assertEqual(response.status_code, 200)
        self.assertLess(duration, 2.0, "Transaction listing took too long")
