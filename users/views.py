from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, UserProfileForm, EmailChangeForm, UsernameChangeForm
from .models import UserProfile, Message, Notification
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def form_valid(self, form):
        user = form.get_user()
        if hasattr(user, 'profile') and getattr(user.profile, 'is_banned', False):
            from django.contrib import messages
            messages.error(self.request, 'Your account has been banned. Please contact support for more information.')
            return self.render_to_response(self.get_context_data(form=form))
        return super().form_valid(form)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'users/profile.html')

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            # Save first_name and last_name to the User model
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            # Redirect to dashboard with #settings tab
            if profile.current_role == 'freelancer':
                return redirect('/freelancer-dashboard/#settings')
            else:
                return redirect('/client-dashboard/#settings')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def switch_role(request, role):
    """Switch between freelancer and client roles"""
    if role not in ['freelancer', 'client']:
        messages.error(request, 'Invalid role specified.')
        return redirect('users:profile')
    
    profile = request.user.profile
    
    if profile.can_switch_to_role(role):
        if profile.switch_role(role):
            messages.success(request, f'Switched to {role} role successfully!')
        else:
            messages.error(request, 'Failed to switch role.')
    else:
        messages.error(request, f'You are not authorized to switch to {role} role.')
    
    # Redirect to appropriate dashboard based on new role
    if role == 'freelancer':
        return redirect('core:freelancer_dashboard')
    elif role == 'client':
        return redirect('core:client_dashboard')
    
    return redirect('users:profile')

@login_required
def inbox(request):
    # Show all conversations (unique users who have sent/received messages)
    user = request.user
    
    # Get all messages where user is sender or recipient
    all_messages = Message.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-created_at')
    
    # Get unique conversation partners
    partners = set()
    
    for msg in all_messages:
        if msg.sender == user:
            partner = msg.recipient
        else:
            partner = msg.sender
        partners.add(partner)
    
    # Convert to list and sort by username for now
    sorted_partners = sorted(partners, key=lambda p: p.username)
    
    # Debug information
    print(f"Debug: Found {len(partners)} conversation partners")
    print(f"Debug: Total messages for user: {all_messages.count()}")
    for partner in sorted_partners:
        print(f"Debug: Partner {partner.username} (ID: {partner.id})")
    
    return render(request, 'users/inbox.html', {
        'partners': sorted_partners,
        'debug_info': {
            'total_partners': len(partners),
            'total_messages': all_messages.count()
        }
    })

@login_required
def conversation(request, user_id):
    user = request.user
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        (Q(sender=user) & Q(recipient=other_user)) |
        (Q(sender=other_user) & Q(recipient=user))
    ).order_by('created_at')
    # Mark all received messages as read
    Message.objects.filter(sender=other_user, recipient=user, is_read=False).update(is_read=True)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=user, recipient=other_user, content=content)
            return redirect('users:conversation', user_id=other_user.id)
    return render(request, 'users/conversation.html', {'other_user': other_user, 'messages': messages})

@login_required
def notifications(request):
    """View all notifications for the current user"""
    notifications = request.user.notifications.all()
    return render(request, 'users/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'success': True})

@login_required
def settings(request):
    """User settings page with profile, notifications, security, and account preferences"""
    user = request.user
    profile = user.profile
    
    # Handle form submissions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            form = UserProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('users:settings')
        
        elif action == 'change_password':
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!')
                return redirect('users:settings')
        
        elif action == 'update_email':
            email_form = EmailChangeForm(request.POST, instance=user)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, 'Email updated successfully!')
                return redirect('users:settings')
        
        elif action == 'update_username':
            username_form = UsernameChangeForm(request.POST, instance=user)
            if username_form.is_valid():
                username_form.save()
                messages.success(request, 'Username updated successfully!')
                return redirect('users:settings')
        
        elif action == 'update_notifications':
            # Update notification preferences
            email_notifications = request.POST.get('email_notifications') == 'on'
            push_notifications = request.POST.get('push_notifications') == 'on'
            job_alerts = request.POST.get('job_alerts') == 'on'
            message_notifications = request.POST.get('message_notifications') == 'on'
            
            # Save to profile (you might want to add these fields to UserProfile model)
            profile.email_notifications = email_notifications
            profile.push_notifications = push_notifications
            profile.job_alerts = job_alerts
            profile.message_notifications = message_notifications
            profile.save()
            
            messages.success(request, 'Notification preferences updated!')
            return redirect('users:settings')
        
        elif action == 'update_privacy':
            # Update privacy settings
            profile_visibility = request.POST.get('profile_visibility', 'public')
            show_contact_info = request.POST.get('show_contact_info') == 'on'
            allow_messages = request.POST.get('allow_messages') == 'on'
            
            profile.profile_visibility = profile_visibility
            profile.show_contact_info = show_contact_info
            profile.allow_messages = allow_messages
            profile.save()
            
            messages.success(request, 'Privacy settings updated!')
            return redirect('users:settings')
    
    # Initialize forms
    profile_form = UserProfileForm(instance=profile)
    password_form = PasswordChangeForm(user)
    email_form = EmailChangeForm(instance=user)
    username_form = UsernameChangeForm(instance=user)
    
    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'email_form': email_form,
        'username_form': username_form,
        'profile': profile,
    }
    
    return render(request, 'users/settings.html', context)

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return redirect('core:home')
    return redirect('users:settings')

@login_required
def test_messages(request):
    """Test view to check if messages are being found"""
    user = request.user
    
    # Get all messages for this user
    all_messages = Message.objects.filter(Q(sender=user) | Q(recipient=user))
    
    # Get unique partners
    partners = set()
    for msg in all_messages:
        if msg.sender == user:
            partners.add(msg.recipient)
        else:
            partners.add(msg.sender)
    
    context = {
        'user': user,
        'total_messages': all_messages.count(),
        'partners': list(partners),
        'all_messages': all_messages[:10],  # Show first 10 messages
    }
    
    return render(request, 'users/test_messages.html', context)

@login_required
def get_conversation_messages(request):
    """Get messages for a specific conversation via AJAX"""
    partner_id = request.GET.get('partner_id')
    if not partner_id:
        return JsonResponse({'success': False, 'error': 'Partner ID required'})
    
    try:
        partner = User.objects.get(id=partner_id)
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(recipient=partner)) |
            (Q(sender=partner) & Q(recipient=request.user))
        ).order_by('created_at')
        
        # Mark messages as read
        Message.objects.filter(sender=partner, recipient=request.user, is_read=False).update(is_read=True)
        
        # Serialize messages
        messages_data = []
        for message in messages:
            messages_data.append({
                'id': message.id,
                'content': message.content,
                'sender_id': message.sender.id,
                'recipient_id': message.recipient.id,
                'created_at': message.created_at.isoformat(),
                'is_read': message.is_read
            })
        
        return JsonResponse({
            'success': True,
            'messages': messages_data
        })
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def send_message(request):
    """Send a message via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'})
    
    recipient_id = request.POST.get('recipient_id')
    content = request.POST.get('content')
    
    if not recipient_id or not content:
        return JsonResponse({'success': False, 'error': 'Recipient ID and content required'})
    
    try:
        recipient = User.objects.get(id=recipient_id)
        
        # Create the message
        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content
        )
        
        # Create notification for the recipient if they allow message notifications
        if hasattr(recipient, 'profile') and getattr(recipient.profile, 'message_notifications', True):
            from .models import Notification
            Notification.objects.create(
                recipient=recipient,
                notification_type='message',
                title=f'New Message from {request.user.username}',
                message=f'You have received a new message.',
            )
        
        # Return success response
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'sender_id': message.sender.id,
                'recipient_id': message.recipient.id,
                'created_at': message.created_at.isoformat(),
                'is_read': message.is_read
            }
        })
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Recipient not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
