from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from jobs.models import Job, Dispute, Contract
from users.models import UserProfile, Notification, Message
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from payments.models import Payment, Wallet, Transaction
from django.db import models
from .utils import get_category_image, get_category_display_name
import os
from django.conf import settings
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from users.forms import UserProfileForm, EmailChangeForm, UsernameChangeForm
from django.contrib.auth.forms import PasswordChangeForm

def home(request):
    """Homepage view with featured jobs"""
    if request.user.is_authenticated:
        # Redirect authenticated users to their dashboard
        if request.user.is_superuser:
            return redirect('core:admin_dashboard')
        elif request.user.profile.current_role == 'freelancer':
            return redirect('core:freelancer_dashboard')
        elif request.user.profile.current_role == 'client':
            return redirect('core:client_dashboard')
    
    featured_jobs = Job.objects.filter(status='open').order_by('-created_at')[:6]
    
    # Get all categories for the categories section
    categories = [
        'graphic-design',
        'digital-marketing', 
        'writing-translation',
        'video-animation',
        'programming',
        'business',
        'lifestyle'
    ]
    
    # Prepare category data with images
    category_data = []
    for category_slug in categories:
        category_info = get_category_image(category_slug)
        # Check if static image exists
        static_path = os.path.join(settings.BASE_DIR, 'core', 'static', category_info['static'])
        if os.path.exists(static_path):
            image_url = os.path.join('/static/', category_info['static'])
        else:
            image_url = category_info['fallback']
        category_data.append({
            'slug': category_slug,
            'name': get_category_display_name(category_slug),
            'image': image_url,
            'placeholder': category_info['placeholder'],
            'fallback': category_info['fallback'],
        })
    
    context = {
        'featured_jobs': featured_jobs,
        'categories': category_data,
    }
    return render(request, 'core/home.html', context)

@login_required
def admin_dashboard(request):
    """Admin dashboard with system overview"""
    if not request.user.is_superuser:
        return redirect('core:home')
    total_users = request.user.__class__.objects.count()
    total_jobs = Job.objects.count()
    open_jobs = Job.objects.filter(status='open').count()
    completed_jobs = Job.objects.filter(status='completed').count()
    recent_jobs = Job.objects.order_by('-created_at')[:5]
    
    # Add dispute statistics
    from jobs.models import Dispute
    total_disputes = Dispute.objects.count()
    open_disputes = Dispute.objects.filter(status='open').count()
    recent_disputes = Dispute.objects.filter(status='open').order_by('-created_at')[:5]
    
    # Add pending withdrawal requests
    from payments.models import Payment
    withdrawal_requests = Payment.objects.filter(payment_type='withdrawal', status='pending').order_by('-created_at')
    
    context = {
        'total_users': total_users,
        'total_jobs': total_jobs,
        'open_jobs': open_jobs,
        'completed_jobs': completed_jobs,
        'recent_jobs': recent_jobs,
        'total_disputes': total_disputes,
        'open_disputes': open_disputes,
        'recent_disputes': recent_disputes,
        'withdrawal_requests': withdrawal_requests,
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
def freelancer_dashboard(request):
    """Freelancer dashboard with available jobs and proposals, and embedded browse gigs panel"""
    if request.user.profile.current_role != 'freelancer':
        return redirect('core:home')

    # Search and filter logic for embedded browse gigs
    category = request.GET.get('category')
    search = request.GET.get('search', '').strip()
    jobs = Job.objects.filter(status='open')
    if category:
        jobs = jobs.filter(category=category)
    if search:
        jobs = jobs.filter(models.Q(title__icontains=search) | models.Q(description__icontains=search))
    categories = Job.CATEGORY_CHOICES

    my_proposals = request.user.proposals.all().order_by('-created_at')[:5]
    active_contracts = request.user.contracts.filter(status='active')[:5]
    notifications = request.user.notifications.all()[:5]  # Get latest 5 notifications
    # Add wallet balance
    try:
        wallet_balance = request.user.wallet.balance
        pending_balance = request.user.wallet.pending_balance
    except Exception:
        wallet_balance = 0
        pending_balance = 0
    
    # Add inbox data
    all_messages = Message.objects.filter(models.Q(sender=request.user) | models.Q(recipient=request.user)).order_by('-created_at')
    partners = set()
    partner_data = {}
    
    for msg in all_messages:
        if msg.sender == request.user:
            partner = msg.recipient
        else:
            partner = msg.sender
        partners.add(partner)
        
        if partner not in partner_data:
            conversation_messages = Message.objects.filter(
                (models.Q(sender=request.user) & models.Q(recipient=partner)) |
                (models.Q(sender=partner) & models.Q(recipient=request.user))
            ).order_by('-created_at')
            
            latest_msg = conversation_messages.first()
            unread_count = Message.objects.filter(
                sender=partner, 
                recipient=request.user, 
                is_read=False
            ).count()
            
            partner_data[partner] = {
                'latest_message': latest_msg,
                'unread_count': unread_count,
                'total_messages': conversation_messages.count()
            }
    
    sorted_partners = sorted(
        partners, 
        key=lambda p: partner_data[p]['latest_message'].created_at if partner_data[p]['latest_message'] else p.date_joined,
        reverse=True
    )
    
    # Settings forms
    profile_form = UserProfileForm(instance=request.user.profile, user=request.user)
    email_form = EmailChangeForm(instance=request.user)
    username_form = UsernameChangeForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    context = {
        'jobs': jobs,
        'categories': categories,
        'selected_category': category,
        'search_query': search,
        'my_proposals': my_proposals,
        'active_contracts': active_contracts,
        'notifications': notifications,
        'wallet_balance': wallet_balance,
        'pending_balance': pending_balance,
        'all_messages': all_messages,
        'partners': sorted_partners,
        'partner_data': partner_data,
        'profile_form': profile_form,
        'email_form': email_form,
        'username_form': username_form,
        'password_form': password_form,
        'profile': request.user.profile,
        'user': request.user,
    }
    return render(request, 'core/freelancer_dashboard.html', context)

@login_required
def client_dashboard(request):
    """Client dashboard with posted jobs and proposals"""
    if request.user.profile.current_role != 'client':
        return redirect('core:home')
    
    my_jobs = request.user.posted_jobs.all().order_by('-created_at')[:10]
    # Calculate total proposals received for all jobs
    proposals_received_count = sum(job.proposals.count() for job in my_jobs)
    # Calculate total spent by the client (sum of completed payments made by the user)
    total_spent = Payment.objects.filter(payer=request.user, status='completed').aggregate(total=models.Sum('amount'))['total'] or 0
    recent_proposals = []
    for job in my_jobs[:5]:
        proposals = job.proposals.all()[:3]
        recent_proposals.extend(proposals)
    
    notifications = request.user.notifications.all()[:5]  # Get latest 5 notifications
    # Add wallet balance
    try:
        wallet_balance = request.user.wallet.balance
    except Exception:
        wallet_balance = 0
    
    # Add inbox data
    all_messages = Message.objects.filter(models.Q(sender=request.user) | models.Q(recipient=request.user)).order_by('-created_at')
    partners = set()
    partner_data = {}
    
    for msg in all_messages:
        if msg.sender == request.user:
            partner = msg.recipient
        else:
            partner = msg.sender
        partners.add(partner)
        
        if partner not in partner_data:
            conversation_messages = Message.objects.filter(
                (models.Q(sender=request.user) & models.Q(recipient=partner)) |
                (models.Q(sender=partner) & models.Q(recipient=request.user))
            ).order_by('-created_at')
            
            latest_msg = conversation_messages.first()
            unread_count = Message.objects.filter(
                sender=partner, 
                recipient=request.user, 
                is_read=False
            ).count()
            
            partner_data[partner] = {
                'latest_message': latest_msg,
                'unread_count': unread_count,
                'total_messages': conversation_messages.count()
            }
    
    sorted_partners = sorted(
        partners, 
        key=lambda p: partner_data[p]['latest_message'].created_at if partner_data[p]['latest_message'] else p.date_joined,
        reverse=True
    )
    
    # Settings forms
    profile_form = UserProfileForm(instance=request.user.profile, user=request.user)
    email_form = EmailChangeForm(instance=request.user)
    username_form = UsernameChangeForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    context = {
        'my_jobs': my_jobs,
        'recent_proposals': recent_proposals[:10],
        'proposals_received_count': proposals_received_count,
        'total_spent': total_spent,
        'notifications': notifications,
        'wallet_balance': wallet_balance,
        'all_messages': all_messages,
        'partners': sorted_partners,
        'partner_data': partner_data,
        'profile_form': profile_form,
        'email_form': email_form,
        'username_form': username_form,
        'password_form': password_form,
        'profile': request.user.profile,
        'user': request.user,
    }
    return render(request, 'core/client_dashboard.html', context)

@login_required
def admin_disputes(request):
    if not request.user.is_superuser:
        return redirect('core:home')
    disputes = Dispute.objects.filter(status='open').select_related('contract', 'raised_by', 'contract__freelancer', 'contract__job', 'contract__job__client')
    context = {
        'disputes': disputes,
    }
    return render(request, 'core/admin_disputes.html', context)

@require_POST
@login_required
def admin_ban_user(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    user_id = request.POST.get('user_id')
    try:
        user = User.objects.get(id=user_id)
        user.profile.is_banned = True
        user.profile.save()
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

@require_POST
@login_required
def admin_timeout_user(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    user_id = request.POST.get('user_id')
    timeout_minutes = int(request.POST.get('timeout_minutes', 60))
    try:
        user = User.objects.get(id=user_id)
        user.profile.timeout_until = timezone.now() + timezone.timedelta(minutes=timeout_minutes)
        user.profile.save()
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

@require_POST
@login_required
def admin_unban_user(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    user_id = request.POST.get('user_id')
    try:
        user = User.objects.get(id=user_id)
        user.profile.is_banned = False
        user.profile.save()
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

@require_POST
def admin_wallet_adjust(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    user_id = request.POST.get('user_id')
    amount = request.POST.get('amount')
    tx_type = request.POST.get('type')
    desc = request.POST.get('desc', '')
    try:
        amount = Decimal(amount)
        if amount <= 0:
            return JsonResponse({'success': False, 'error': 'Amount must be positive.'})
        wallet = Wallet.objects.get(user_id=user_id)
        if tx_type == 'credit':
            wallet.add_funds(amount)
            Transaction.objects.create(wallet=wallet, amount=amount, transaction_type='credit', description=desc or 'Admin credit', balance_after=wallet.balance)
            return JsonResponse({'success': True})
        elif tx_type == 'debit':
            if wallet.balance < amount:
                return JsonResponse({'success': False, 'error': 'Insufficient balance.'})
            wallet.deduct_funds(amount)
            Transaction.objects.create(wallet=wallet, amount=amount, transaction_type='debit', description=desc or 'Admin debit', balance_after=wallet.balance)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid transaction type.'})
    except Wallet.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Wallet not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@login_required
def request_withdrawal(request):
    try:
        amount = request.POST.get('amount')
        amount = Decimal(amount)
        if amount <= 0:
            return JsonResponse({'success': False, 'error': 'Amount must be positive.'})
        wallet = request.user.wallet
        if wallet.balance < amount:
            return JsonResponse({'success': False, 'error': 'Insufficient wallet balance.'})
        # Create a pending withdrawal payment
        Payment.objects.create(
            payer=request.user,
            payee=request.user,
            amount=amount,
            payment_type='withdrawal',
            status='pending',
            description='User requested withdrawal'
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def admin_manage_users(request):
    if not request.user.is_superuser:
        return redirect('core:home')
    query = request.GET.get('q', '')
    users_qs = User.objects.all().select_related('profile')
    if query:
        users_qs = users_qs.filter(username__icontains=query)
    users_qs = users_qs.order_by('username')
    users_qs = users_qs.exclude(is_superuser=True)
    # Attach wallet balance to each user
    for u in users_qs:
        try:
            u.wallet_balance = u.wallet.balance
        except Exception:
            u.wallet_balance = 0
    active_users = [u for u in users_qs if not getattr(u.profile, 'is_banned', False)]
    banned_users = [u for u in users_qs if getattr(u.profile, 'is_banned', False)]
    context = {
        'users': active_users,
        'banned_users': banned_users,
        'query': query,
    }
    return render(request, 'core/admin_manage_users.html', context)

@require_POST
@login_required
def admin_send_message(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    user_id = request.POST.get('user_id')
    message = request.POST.get('message')
    try:
        user = User.objects.get(id=user_id)
        # Simulate sending message (could be email, notification, etc.)
        print(f"Admin message to {user.username}: {message}")
        # Optionally, store in a Message model or send email
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

def banned_info(request):
    return render(request, 'core/banned_info.html')
