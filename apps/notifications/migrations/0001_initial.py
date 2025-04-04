# Generated by Django 5.1.6 on 2025-03-04 20:16

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('EVENT_INVITE', 'Event Invitation'), ('RSVP_CONFIRMATION', 'RSVP Confirmation'), ('RSVP_UPDATE', 'RSVP Status Update'), ('EVENT_REMINDER', 'Event Reminder'), ('PAYMENT_CONFIRMATION', 'Payment Confirmation'), ('HOST_MESSAGE', 'Host Message'), ('EVENT_UPDATE', 'Event Update'), ('SYSTEM', 'System Notification')], max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('action_link', models.CharField(blank=True, max_length=255, null=True)),
                ('action_text', models.CharField(blank=True, max_length=50, null=True)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='events.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'notifications',
                'ordering': ['-created_at'],
            },
        ),
    ]
