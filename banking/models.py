from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

class AccountHolder(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.email}"

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('CHECKING', 'Checking'),
        ('SAVINGS', 'Savings'),
        ('BUSINESS', 'Business'),
    ]

    account_number = models.CharField(max_length=20, unique=True)
    account_holder = models.ForeignKey(AccountHolder, on_delete=models.CASCADE, related_name='accounts')
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = f"ACC{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.account_number} - {self.account_holder}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSFER_IN', 'Transfer In'),
        ('TRANSFER_OUT', 'Transfer Out'),
    ]

    transaction_id = models.CharField(max_length=20, unique=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=12, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    description = models.TextField(blank=True)
    reference_number = models.CharField(max_length=50, blank=True)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - {self.account.account_number}"

    class Meta:
        ordering = ['-created_at']

class MoneyTransfer(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    transfer_id = models.CharField(max_length=20, unique=True)
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='outgoing_transfers')
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='incoming_transfers')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.transfer_id:
            self.transfer_id = f"TRF{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transfer_id} - {self.amount}"

class Card(models.Model):
    CARD_TYPES = [
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
    ]

    card_number = models.CharField(max_length=16, unique=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='cards')
    card_type = models.CharField(max_length=6, choices=CARD_TYPES)
    cardholder_name = models.CharField(max_length=100)
    expiry_date = models.DateField()
    cvv = models.CharField(max_length=4)
    is_active = models.BooleanField(default=True)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.card_number:
            self.card_number = f"4{uuid.uuid4().hex[:15]}"[:16]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.card_number[-4:]} - {self.cardholder_name}"

class Statement(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='statements')
    statement_period_start = models.DateField()
    statement_period_end = models.DateField()
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2)
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2)
    total_deposits = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_withdrawals = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Statement {self.account.account_number} - {self.statement_period_start} to {self.statement_period_end}"

    class Meta:
        ordering = ['-generated_at']
