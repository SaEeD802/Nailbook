from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Salon(models.Model):
    name = models.CharField(max_length=200, verbose_name='نام سالن')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_salons')
    phone = models.CharField(max_length=15, verbose_name='تلفن')
    address = models.TextField(verbose_name='آدرس')
    
    # ساعات کاری
    opening_time = models.TimeField(default='09:00', verbose_name='ساعت شروع')
    closing_time = models.TimeField(default='21:00', verbose_name='ساعت پایان')
    
    # روزهای تعطیل
    closed_days = models.CharField(
        max_length=20, 
        default='friday',
        help_text='روزهای تعطیل (جمعه کاما-separated)',
        verbose_name='روزهای تعطیل'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='staff_members')
    specialties = models.TextField(help_text='تخصص‌ها (مثال: ژل‌لاک، کاشت)', blank=True)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.salon.name}"