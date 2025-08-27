from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('salon_owner', 'صاحب سالن'),
        ('staff', 'کارمند'),
        ('customer', 'مشتری'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.phone})"
        return f"{self.username} ({self.phone})"

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'