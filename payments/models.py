from django.db import models
from django.contrib.auth.models import User
from jobs.models import Contract

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pending_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Wallet - ${self.balance} (Pending: ${self.pending_balance})"
    
    def add_funds(self, amount):
        self.balance += amount
        self.save()
    
    def deduct_funds(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False
    
    def add_pending_funds(self, amount):
        """Add funds to pending balance (escrow)"""
        self.pending_balance += amount
        self.save()
    
    def release_pending_funds(self, amount):
        """Release pending funds to available balance"""
        if self.pending_balance >= amount:
            self.pending_balance -= amount
            self.balance += amount
            self.save()
            return True
        return False
    
    def refund_pending_funds(self, amount):
        """Refund pending funds (in case of dispute/cancellation)"""
        if self.pending_balance >= amount:
            self.pending_balance -= amount
            self.save()
            return True
        return False

class Payment(models.Model):
    PAYMENT_TYPES = (
        ('escrow', 'Escrow'),
        ('release', 'Release'),
        ('refund', 'Refund'),
        ('withdrawal', 'Withdrawal'),
        ('deposit', 'Deposit'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')
    payee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment of ${self.amount} from {self.payer.username} to {self.payee.username}"
    
    class Meta:
        ordering = ['-created_at']

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.TextField()
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type.title()} of ${self.amount} - {self.wallet.user.username}"
    
    class Meta:
        ordering = ['-created_at']
