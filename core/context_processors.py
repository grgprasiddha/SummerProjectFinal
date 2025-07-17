from users.models import Notification

def notification_data(request):
    """Add notification data to all templates"""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        recent_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]
        total_count = Notification.objects.filter(recipient=request.user).count()
        
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent_notifications,
            'total_notifications_count': total_count,
        }
    else:
        return {
            'unread_notifications_count': 0,
            'recent_notifications': [],
            'total_notifications_count': 0,
        } 