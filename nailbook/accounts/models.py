from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('salon_owner', 'صاحب سالن'),
        ('staff', 'کارمند'),
        ('customer', 'مشتری'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer', verbose_name='نقش')
    phone = models.CharField(max_length=11, unique=True, verbose_name='تلفن')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='ایجاد شده در')

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.phone}"
