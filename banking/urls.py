from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Account Holders
    path('profile/', views.account_holder_profile, name='profile'),

    # Accounts
    path('accounts/', views.AccountListCreateView.as_view(), name='account-list'),
    path('accounts/<int:pk>/', views.AccountDetailView.as_view(), name='account-detail'),

    # Transactions
    path('accounts/<int:account_id>/transactions/', views.TransactionListView.as_view(), name='transactions'),
    path('accounts/<int:account_id>/deposit/', views.deposit_money, name='deposit'),
    path('accounts/<int:account_id>/withdraw/', views.withdraw_money, name='withdraw'),

    # Money Transfers
    path('transfers/', views.MoneyTransferListCreateView.as_view(), name='transfers'),

    # Cards
    path('cards/', views.CardListCreateView.as_view(), name='card-list'),
    path('cards/<int:pk>/', views.CardDetailView.as_view(), name='card-detail'),

    # Statements
    path('accounts/<int:account_id>/statements/', views.StatementListView.as_view(), name='statements'),
    path('accounts/<int:account_id>/generate-statement/', views.generate_statement, name='generate-statement'),
]
