import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model with additional fields for Invike platform
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    avatar = models.URLField(blank=True, null=True)
    ROLE_CHOICES = (
        ('HOST', 'Host'),
        ('GUEST', 'Guest'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='GUEST')
    
    # Add phone number for social auth verification and local authentication
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Fields for social auth
    google_id = models.CharField(max_length=255, blank=True, null=True)
    apple_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Override groups and user_permissions with custom related_names
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='invike_users',  # Custom related_name
        blank=True,
        help_text='The groups this user belongs to.'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='invike_users',  # Custom related_name
        blank=True,
        help_text='Specific permissions for this user.'
    )
    
    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email