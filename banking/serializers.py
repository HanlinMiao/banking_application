from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import AccountHolder, Account, Transaction, MoneyTransfer, Card, Statement

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class AccountHolderSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()

    class Meta:
        model = AccountHolder
        fields = ['user', 'phone_number', 'address', 'date_of_birth']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserRegistrationSerializer().create(user_data)
        account_holder = AccountHolder.objects.create(user=user, **validated_data)
        return account_holder

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'account_number', 'account_type', 'balance', 'is_active', 'created_at']
        read_only_fields = ['account_number', 'balance']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['transaction_id', 'balance_after']

class MoneyTransferSerializer(serializers.ModelSerializer):
    from_account_number = serializers.CharField(source='from_account.account_number', read_only=True)
    to_account_number = serializers.CharField(source='to_account.account_number', read_only=True)

    class Meta:
        model = MoneyTransfer
        fields = ['id', 'transfer_id', 'from_account', 'to_account', 'from_account_number',
                 'to_account_number', 'amount', 'description', 'status', 'created_at', 'completed_at']
        read_only_fields = ['transfer_id', 'status', 'completed_at']

class CardSerializer(serializers.ModelSerializer):
    masked_card_number = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = ['id', 'card_number', 'masked_card_number', 'card_type', 'cardholder_name',
                 'expiry_date', 'is_active', 'credit_limit', 'created_at']
        read_only_fields = ['card_number']

    def get_masked_card_number(self, obj):
        return f"****-****-****-{obj.card_number[-4:]}"

class StatementSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(source='account.account_number', read_only=True)
    transactions = serializers.SerializerMethodField()

    class Meta:
        model = Statement
        fields = ['id', 'account', 'account_number', 'statement_period_start',
                 'statement_period_end', 'opening_balance', 'closing_balance',
                 'total_deposits', 'total_withdrawals', 'generated_at', 'transactions']

    def get_transactions(self, obj):
        transactions = Transaction.objects.filter(
            account=obj.account,
            created_at__date__range=[obj.statement_period_start, obj.statement_period_end]
        )
        return TransactionSerializer(transactions, many=True).data
