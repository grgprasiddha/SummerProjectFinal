from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('wallet/', views.wallet, name='wallet'),
    path('add-funds/', views.add_funds, name='add_funds'),
    path('history/', views.payment_history, name='history'),
] 