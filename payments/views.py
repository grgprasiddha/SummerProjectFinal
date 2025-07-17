from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wallet, Payment, Transaction

# Create your views here.

@login_required
def wallet(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all()[:10]  # Last 10 transactions
    
    context = {
        'wallet': wallet,
        'transactions': transactions,
    }
    return render(request, 'payments/wallet.html', context)

@login_required
def add_funds(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
            if amount > 0:
                wallet, created = Wallet.objects.get_or_create(user=request.user)
                wallet.add_funds(amount)
                
                # Create transaction record
                Transaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type='credit',
                    description=f'Added ${amount} to wallet',
                    balance_after=wallet.balance
                )
                
                messages.success(request, f'Successfully added ${amount} to your wallet!')
            else:
                messages.error(request, 'Amount must be greater than 0.')
        except ValueError:
            messages.error(request, 'Please enter a valid amount.')
        
        return redirect('payments:wallet')
    
    return render(request, 'payments/add_funds.html')

@login_required
def payment_history(request):
    payments_made = Payment.objects.filter(payer=request.user)
    payments_received = Payment.objects.filter(payee=request.user)
    
    context = {
        'payments_made': payments_made,
        'payments_received': payments_received,
    }
    return render(request, 'payments/payment_history.html', context)
