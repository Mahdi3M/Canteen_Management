from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    ROLES = (
        ('Admin', 'Admin'),
        ('Bar NCO', 'Bar NCO'),
        ('Customer', 'Customer'),
    )

    ba = models.CharField(blank=True, null=True, max_length=6)
    unit = models.CharField(blank=True, null=True, max_length=32)
    role = models.CharField(max_length=10, choices=ROLES, default='Customer')

    def __str__(self):
        return self.username
    
    @property
    def name(self):
        words = [self.first_name, self.last_name]
        result = ' '.join([word for word in words if word is not None])
        return result