from django.shortcuts import render
from django.db.models import Q, Sum
# Create your views here.
from rest_framework import generics, status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

from .models import AccountHolder, Account, Transaction, MoneyTransfer, Card, Statement
from .serializers import (
    UserRegistrationSerializer, AccountHolderSerializer, AccountSerializer,
    TransactionSerializer, MoneyTransferSerializer, CardSerializer, StatementSerializer
)

class SignUpView(generics.CreateAPIView):
    queryset = AccountHolder.objects.all()
    serializer_class = AccountHolderSerializer
    permission_classes = [permissions.AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

@api_view(['GET'])
def account_holder_profile(request):
    try:
        account_holder = AccountHolder.objects.get(user=request.user)
        serializer = AccountHolderSerializer(account_holder)
        return Response(serializer.data)
    except AccountHolder.DoesNotExist:
        return Response({'error': 'Account holder not found'}, status=404)

class AccountListCreateView(generics.ListCreateAPIView):
    serializer_class = AccountSerializer

    def get_queryset(self):
        account_holder = AccountHolder.objects.get(user=self.request.user)
        return Account.objects.filter(account_holder=account_holder)

    def perform_create(self, serializer):
        account_holder = AccountHolder.objects.get(user=self.request.user)
        serializer.save(account_holder=account_holder)

class AccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AccountSerializer

    def get_queryset(self):
        account_holder = AccountHolder.objects.get(user=self.request.user)
        return Account.objects.filter(account_holder=account_holder)

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        account_id = self.kwargs.get('account_id')
        account_holder = AccountHolder.objects.get(user=self.request.user)
        return Transaction.objects.filter(
            account_id=account_id,
            account__account_holder=account_holder
        )

@api_view(['POST'])
def deposit_money(request, account_id):
    try:
        account_holder = AccountHolder.objects.get(user=request.user)
        account = Account.objects.get(id=account_id, account_holder=account_holder)

        amount = Decimal(str(request.data.get('amount', 0)))
        description = request.data.get('description', 'Deposit')

        if amount <= 0:
            return Response({'error': 'Amount must be positive'}, status=400)

        with transaction.atomic():
            account.balance += amount
            account.save()

            Transaction.objects.create(
                account=account,
                transaction_type='DEPOSIT',
                amount=amount,
                description=description,
                balance_after=account.balance
            )

        return Response({
            'message': 'Deposit successful',
            'new_balance': account.balance
        })

    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def withdraw_money(request, account_id):
    try:
        account_holder = AccountHolder.objects.get(user=request.user)
        account = Account.objects.get(id=account_id, account_holder=account_holder)

        amount = Decimal(str(request.data.get('amount', 0)))
        description = request.data.get('description', 'Withdrawal')

        if amount <= 0:
            return Response({'error': 'Amount must be positive'}, status=400)

        if account.balance < amount:
            return Response({'error': 'Insufficient funds'}, status=400)

        with transaction.atomic():
            account.balance -= amount
            account.save()

            Transaction.objects.create(
                account=account,
                transaction_type='WITHDRAWAL',
                amount=amount,
                description=description,
                balance_after=account.balance
            )

        return Response({
            'message': 'Withdrawal successful',
            'new_balance': account.balance
        })

    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

class MoneyTransferListCreateView(generics.ListCreateAPIView):
    serializer_class = MoneyTransferSerializer

    def get_queryset(self):
        account_holder = AccountHolder.objects.get(user=self.request.user)
        user_accounts = Account.objects.filter(account_holder=account_holder)
        return MoneyTransfer.objects.filter(
            Q(from_account__in=user_accounts) |
            Q(to_account__in=user_accounts)
        )

    def perform_create(self, serializer):
        from_account = serializer.validated_data['from_account']
        to_account = serializer.validated_data['to_account']
        amount = serializer.validated_data['amount']

        # Verify user owns the from_account
        account_holder = AccountHolder.objects.get(user=self.request.user)
        if from_account.account_holder != account_holder:
            raise ValidationError("You can only transfer from your own accounts")

        if from_account.balance < amount:
            raise ValidationError("Insufficient funds")

        if from_account == to_account:
            raise ValidationError("Cannot transfer to the same account")

        with transaction.atomic():
            # Deduct from source account
            from_account.balance -= amount
            from_account.save()

            # Add to destination account
            to_account.balance += amount
            to_account.save()

            # Create transfer record
            money_transfer = serializer.save(status='COMPLETED', completed_at=timezone.now())

            # Create transaction records
            Transaction.objects.create(
                account=from_account,
                transaction_type='TRANSFER_OUT',
                amount=amount,
                description=f"Transfer to {to_account.account_number}",
                reference_number=money_transfer.transfer_id,
                balance_after=from_account.balance
            )

            Transaction.objects.create(
                account=to_account,
                transaction_type='TRANSFER_IN',
                amount=amount,
                description=f"Transfer from {from_account.account_number}",
                reference_number=money_transfer.transfer_id,
                balance_after=to_account.balance
            )

class CardListCreateView(generics.ListCreateAPIView):
    serializer_class = CardSerializer

    def get_queryset(self):
        account_holder = AccountHolder.objects.get(user=self.request.user)
        user_accounts = Account.objects.filter(account_holder=account_holder)
        return Card.objects.filter(account__in=user_accounts)

    def perform_create(self, serializer):
        account = serializer.validated_data['account']
        account_holder = AccountHolder.objects.get(user=self.request.user)

        if account.account_holder != account_holder:
            raise ValidationError("You can only create cards for your own accounts")

        # Generate CVV and expiry date
        serializer.save(
            cvv=str(uuid.uuid4().int)[:3],
            expiry_date=timezone.now().date() + timedelta(days=1825)  # 5 years
        )

class CardDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CardSerializer

    def get_queryset(self):
        account_holder = AccountHolder.objects.get(user=self.request.user)
        user_accounts = Account.objects.filter(account_holder=account_holder)
        return Card.objects.filter(account__in=user_accounts)

class StatementListView(generics.ListAPIView):
    serializer_class = StatementSerializer

    def get_queryset(self):
        account_id = self.kwargs.get('account_id')
        account_holder = AccountHolder.objects.get(user=self.request.user)
        return Statement.objects.filter(
            account_id=account_id,
            account__account_holder=account_holder
        )

@api_view(['POST'])
def generate_statement(request, account_id):
    try:
        account_holder = AccountHolder.objects.get(user=request.user)
        account = Account.objects.get(id=account_id, account_holder=account_holder)

        start_date = datetime.strptime(request.data.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.data.get('end_date'), '%Y-%m-%d').date()

        # Get transactions for the period
        transactions = Transaction.objects.filter(
            account=account,
            created_at__date__range=[start_date, end_date]
        )

        # Calculate totals
        deposits = transactions.filter(
            transaction_type__in=['DEPOSIT', 'TRANSFER_IN']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        withdrawals = transactions.filter(
            transaction_type__in=['WITHDRAWAL', 'TRANSFER_OUT']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Get opening balance (current balance minus net transactions)
        opening_balance = account.balance - deposits + withdrawals

        statement = Statement.objects.create(
            account=account,
            statement_period_start=start_date,
            statement_period_end=end_date,
            opening_balance=opening_balance,
            closing_balance=account.balance,
            total_deposits=deposits,
            total_withdrawals=withdrawals
        )

        serializer = StatementSerializer(statement)
        return Response(serializer.data)

    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
