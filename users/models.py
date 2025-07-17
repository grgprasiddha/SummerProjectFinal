from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    USER_TYPES = (
        ('freelancer', 'Freelancer'),
        ('client', 'Client'),
    )
    
    VISIBILITY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
        ('friends', 'Friends Only'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='client')
    current_role = models.CharField(max_length=20, choices=USER_TYPES, default='client')
    bio = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_banned = models.BooleanField(default=False)
    timeout_until = models.DateTimeField(blank=True, null=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    job_alerts = models.BooleanField(default=True)
    message_notifications = models.BooleanField(default=True)
    
    # Privacy settings
    profile_visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    show_contact_info = models.BooleanField(default=True)
    allow_messages = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    def can_switch_to_role(self, role):
        return role in ['freelancer', 'client'] or self.user.is_superuser
    
    def switch_role(self, role):
        """Switch to a different role if allowed"""
        if self.can_switch_to_role(role):
            self.current_role = role
            self.save()
            return True
        return False

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username}: {self.content[:30]}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('job_request', 'Job Request'),
        ('proposal_accepted', 'Proposal Accepted'),
        ('proposal_rejected', 'Proposal Rejected'),
        ('payment_received', 'Payment Received'),
        ('payment_sent', 'Payment Sent'),
        ('dispute_created', 'Dispute Created'),
        ('dispute_resolved', 'Dispute Resolved'),
        ('system', 'System Message'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    related_proposal = models.ForeignKey('jobs.Proposal', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} - {self.recipient.username}: {self.title}"

    class Meta:
        ordering = ['-created_at']
