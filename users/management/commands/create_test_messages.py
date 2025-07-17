from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Message
from datetime import datetime, timedelta
from django.db import models

class Command(BaseCommand):
    help = 'Create test messages for debugging the inbox'

    def handle(self, *args, **options):
        # Get or create test users
        user1, created1 = User.objects.get_or_create(
            username='testuser1',
            defaults={
                'email': 'test1@example.com',
                'first_name': 'Test',
                'last_name': 'User1'
            }
        )
        
        user2, created2 = User.objects.get_or_create(
            username='testuser2',
            defaults={
                'email': 'test2@example.com',
                'first_name': 'Test',
                'last_name': 'User2'
            }
        )
        
        if created1:
            self.stdout.write(f'Created user: {user1.username}')
        if created2:
            self.stdout.write(f'Created user: {user2.username}')
        
        # Create some test messages
        messages_data = [
            {
                'sender': user1,
                'recipient': user2,
                'content': 'Hello! How are you doing?',
                'created_at': datetime.now() - timedelta(hours=2)
            },
            {
                'sender': user2,
                'recipient': user1,
                'content': 'Hi! I\'m doing great, thanks for asking. How about you?',
                'created_at': datetime.now() - timedelta(hours=1, minutes=30)
            },
            {
                'sender': user1,
                'recipient': user2,
                'content': 'I\'m doing well too! Are you interested in working on a project together?',
                'created_at': datetime.now() - timedelta(hours=1)
            },
            {
                'sender': user2,
                'recipient': user1,
                'content': 'Absolutely! I\'d love to collaborate. What kind of project do you have in mind?',
                'created_at': datetime.now() - timedelta(minutes=30)
            },
            {
                'sender': user1,
                'recipient': user2,
                'content': 'Great! I\'ll send you the details soon.',
                'created_at': datetime.now() - timedelta(minutes=15)
            }
        ]
        
        created_count = 0
        for msg_data in messages_data:
            message, created = Message.objects.get_or_create(
                sender=msg_data['sender'],
                recipient=msg_data['recipient'],
                content=msg_data['content'],
                defaults={
                    'created_at': msg_data['created_at']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created message: {message.content[:30]}...')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} test messages between {user1.username} and {user2.username}'
            )
        )
        
        # Show total message count
        total_messages = Message.objects.count()
        self.stdout.write(f'Total messages in database: {total_messages}')
        
        # Show messages for each user
        user1_messages = Message.objects.filter(
            models.Q(sender=user1) | models.Q(recipient=user1)
        ).count()
        user2_messages = Message.objects.filter(
            models.Q(sender=user2) | models.Q(recipient=user2)
        ).count()
        
        self.stdout.write(f'Messages for {user1.username}: {user1_messages}')
        self.stdout.write(f'Messages for {user2.username}: {user2_messages}') 