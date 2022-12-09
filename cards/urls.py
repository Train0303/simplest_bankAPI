from django.contrib import admin
from django.urls import path,include

from .views.card import CreateCardView,CreateAccountView,CardListView,AccountListView
from .views.transaction import DepositAPIView,WithdrawAPIView,TransactionListAPIView

app_name='cards'
urlpatterns = [
    path('create',CreateCardView.as_view(), name='card_create'),
    path('create/account',CreateAccountView.as_view(), name='account_create'),
    path('list',CardListView.as_view(),name='card_list'),
    path('list/account',AccountListView.as_view(),name='account_list'),
    path('transaction/deposit',DepositAPIView.as_view(),name='deposit'),
    path('transaction/withdraw',WithdrawAPIView.as_view(),name='withdraw'),
    path('transaction/list',TransactionListAPIView.as_view(),name='transaction_list'),
]
