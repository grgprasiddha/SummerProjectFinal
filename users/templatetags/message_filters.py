from django import template
from django.db.models import Q
from users.models import Message
from jobs.models import Contract

register = template.Library()

@register.filter
def get_latest_message(partner, user):
    """Get the latest message between two users"""
    messages = Message.objects.filter(
        (Q(sender=user) & Q(recipient=partner)) |
        (Q(sender=partner) & Q(recipient=user))
    ).order_by('-created_at')
    
    return messages.first()

@register.filter
def has_unread_messages(partner, user):
    """Check if there are unread messages from a partner"""
    return Message.objects.filter(
        sender=partner,
        recipient=user,
        is_read=False
    ).exists()

@register.filter
def has_contract_with(partner, user):
    """Check if there's an active contract between two users"""
    return Contract.objects.filter(
        (Q(freelancer=user) & Q(job__client=partner)) |
        (Q(freelancer=partner) & Q(job__client=user)),
        status='active'
    ).exists()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    return dictionary.get(key) 