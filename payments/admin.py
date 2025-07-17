from django.contrib import admin
from .models import Wallet, Payment, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at']
    search_fields = ['user__username', 'user__email']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payer', 'payee', 'amount', 'payment_type', 'status', 'created_at']
    list_filter = ['payment_type', 'status', 'created_at']
    search_fields = ['payer__username', 'payee__username']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'transaction_type', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['wallet__user__username']
