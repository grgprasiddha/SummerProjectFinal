from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile
from jobs.models import Job, Proposal
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seed the database with demo data'

    def handle(self, *args, **kwargs):
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin / admin123'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists.'))

        # Create demo client
        client, _ = User.objects.get_or_create(username='client1', defaults={
            'email': 'client1@example.com',
        })
        client.set_password('client123')
        client.save()
        client.profile.user_type = 'client'
        client.profile.current_role = 'client'
        client.profile.save()

        # Create demo freelancer
        freelancer, _ = User.objects.get_or_create(username='freelancer1', defaults={
            'email': 'freelancer1@example.com',
        })
        freelancer.set_password('freelancer123')
        freelancer.save()
        freelancer.profile.user_type = 'freelancer'
        freelancer.profile.current_role = 'freelancer'
        freelancer.profile.skills = 'Web Design, Python, Logo Design'
        freelancer.profile.hourly_rate = 20
        freelancer.profile.save()

        # Create a user that can switch between roles
        switcher, _ = User.objects.get_or_create(username='switcher', defaults={
            'email': 'switcher@example.com',
        })
        switcher.set_password('switcher123')
        switcher.save()
        switcher.profile.user_type = 'freelancer'  # Can be both
        switcher.profile.current_role = 'freelancer'
        switcher.profile.skills = 'Full Stack Development, UI/UX Design'
        switcher.profile.hourly_rate = 25
        switcher.profile.save()

        # Create demo jobs
        job, _ = Job.objects.get_or_create(
            title='Design a Modern Logo',
            client=client,
            defaults={
                'description': 'Need a modern logo for a tech startup.',
                'category': 'graphic-design',
                'budget': 100,
                'deadline': timezone.now().date(),
                'status': 'open',
            }
        )

        # Create demo proposal
        Proposal.objects.get_or_create(
            job=job,
            freelancer=freelancer,
            defaults={
                'bid_amount': 90,
                'cover_letter': 'I am an experienced designer and can deliver a great logo.',
                'estimated_days': 3,
                'status': 'pending',
            }
        )

        self.stdout.write(self.style.SUCCESS('Seed data created!'))
        self.stdout.write(self.style.SUCCESS('Demo users:'))
        self.stdout.write(self.style.SUCCESS('- admin / admin123 (Superuser)'))
        self.stdout.write(self.style.SUCCESS('- client1 / client123 (Client only)'))
        self.stdout.write(self.style.SUCCESS('- freelancer1 / freelancer123 (Freelancer only)'))
        self.stdout.write(self.style.SUCCESS('- switcher / switcher123 (Can switch roles)')) 