from django.test import TestCase
from django.contrib.auth.models import User
from banking.serializers import (
    UserRegistrationSerializer, AccountHolderSerializer, AccountSerializer,
    TransactionSerializer, MoneyTransferSerializer, CardSerializer
)
from banking.models import AccountHolder, Account, Transaction, MoneyTransfer, Card
from decimal import Decimal
from datetime import date

class UserRegistrationSerializerTest(TestCase):
    def test_valid_user_registration(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_password_mismatch(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass'
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

class AccountHolderSerializerTest(TestCase):
    def test_valid_account_holder_creation(self):
        data = {
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

        serializer = AccountHolderSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        account_holder = serializer.save()
        self.assertEqual(account_holder.user.username, 'testuser')
        self.assertEqual(account_holder.phone_number, '+1234567890')
