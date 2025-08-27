from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class Salon(models.Model):
    DAYS_CHOICES = [
        ('saturday', 'شنبه'),
        ('sunday', 'یکشنبه'),
        ('monday', 'دوشنبه'),
        ('tuesday', 'سه‌شنبه'),
        ('wednesday', 'چهارشنبه'),
        ('thursday', 'پنج‌شنبه'),
        ('friday', 'جمعه'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='نام سالن')
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='owned_salons',
        limit_choices_to={'role': 'salon_owner'}
    )
    phone = models.CharField(max_length=15, verbose_name='تلفن')
    address = models.TextField(verbose_name='آدرس')
    
    # ساعات کاری
    opening_time = models.TimeField(default='09:00', verbose_name='ساعت شروع')
    closing_time = models.TimeField(default='21:00', verbose_name='ساعت پایان')
    
    # روزهای تعطیل - درست شده
    closed_days = models.CharField(
        max_length=100, 
        blank=True,
        help_text='روزهای تعطیل را با کاما جدا کنید (مثال: friday,saturday)',
        verbose_name='روزهای تعطیل'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if self.opening_time >= self.closing_time:
            raise ValidationError('ساعت شروع باید قبل از ساعت پایان باشد')
    
    def get_closed_days_list(self):
        """لیست روزهای تعطیل"""
        if self.closed_days:
            return [day.strip() for day in self.closed_days.split(',')]
        return []
    
    def is_closed_on_day(self, day):
        """چک کردن تعطیلی در روز خاص"""
        return day.lower() in self.get_closed_days_list()
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'سالن'
        verbose_name_plural = 'سالن‌ها'

class Staff(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'staff'}
    )
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='staff_members')
    specialties = models.TextField(
        help_text='تخصص‌ها (مثال: ژل‌لاک، کاشت، پدیکور)', 
        blank=True,
        verbose_name='تخصص‌ها'
    )
    is_available = models.BooleanField(default=True, verbose_name='در دسترس')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.salon.name}"
    
    def save(self, *args, **kwargs):
        # اطمینان از اینکه user نقش staff داشته باشد
        if self.user.role != 'staff':
            self.user.role = 'staff'
            self.user.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'کارمند'
        verbose_name_plural = 'کارمندان'

