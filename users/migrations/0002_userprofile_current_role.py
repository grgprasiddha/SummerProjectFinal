# Generated by Django 5.1.6 on 2025-06-24 04:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='current_role',
            field=models.CharField(choices=[('freelancer', 'Freelancer'), ('client', 'Client')], default='client', max_length=20),
        ),
    ]
