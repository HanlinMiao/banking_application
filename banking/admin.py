from django.contrib import admin

# Register your models here.
from .models import AccountHolder, Account, Transaction, MoneyTransfer, Card, Statement

@admin.register(AccountHolder)
class AccountHolderAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'account_holder', 'account_type', 'balance', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['account_number', 'account_holder__user__username']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'account', 'transaction_type', 'amount', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['transaction_id', 'account__account_number']

@admin.register(MoneyTransfer)
class MoneyTransferAdmin(admin.ModelAdmin):
    list_display = ['transfer_id', 'from_account', 'to_account', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['card_number', 'account', 'card_type', 'cardholder_name', 'is_active']
    list_filter = ['card_type', 'is_active']

@admin.register(Statement)
class StatementAdmin(admin.ModelAdmin):
    list_display = ['account', 'statement_period_start', 'statement_period_end', 'generated_at']
    list_filter = ['generated_at']
