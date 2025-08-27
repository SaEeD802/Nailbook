from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import jdatetime

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار تایید'),
        ('confirmed', 'تایید شده'),
        ('in_progress', 'در حال انجام'),
        ('completed', 'تکمیل شده'),
        ('cancelled', 'لغو شده'),
        ('no_show', 'عدم حضور'),
    ]
    
    salon = models.ForeignKey('salons.Salon', on_delete=models.CASCADE, related_name='appointments')
    customer = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='appointments',
        limit_choices_to={'role': 'customer'}
    )
    staff = models.ForeignKey('salons.Staff', on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE)
    
    appointment_date = models.DateField(verbose_name='تاریخ نوبت')
    appointment_time = models.TimeField(verbose_name='ساعت نوبت')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, verbose_name='یادداشت')
    
    # پرداخت
    total_price = models.PositiveIntegerField(verbose_name='مبلغ کل')
    is_paid = models.BooleanField(default=False, verbose_name='پرداخت شده')
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'نقدی'),
            ('card', 'کارتی'),
            ('online', 'آنلاین'),
        ],
        blank=True,
        verbose_name='روش پرداخت'
    )
    
    # SMS
    sms_sent = models.BooleanField(default=False, verbose_name='پیامک ارسال شده')
    reminder_sent = models.BooleanField(default=False, verbose_name='یادآوری ارسال شده')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        unique_together = ['salon', 'staff', 'appointment_date', 'appointment_time']
        verbose_name = 'نوبت'
        verbose_name_plural = 'نوبت‌ها'
    
    def clean(self):
        """اعتبارسنجی مدل"""
        errors = {}
        
        # چک کردن تاریخ گذشته
        if self.appointment_date < timezone.now().date():
            errors['appointment_date'] = 'تاریخ نوبت نمی‌تواند در گذشته باشد'
        
        # چک کردن ساعات کاری سالن
        if hasattr(self, 'salon'):
            if (self.appointment_time < self.salon.opening_time or 
                self.appointment_time > self.salon.closing_time):
                errors['appointment_time'] = f'ساعت نوبت باید بین {self.salon.opening_time} تا {self.salon.closing_time} باشد'
        
        # چک کردن انطباق staff با salon
        if hasattr(self, 'staff') and hasattr(self, 'salon'):
            if self.staff.salon != self.salon:
                errors['staff'] = 'کارمند انتخابی متعلق به این سالن نیست'
        
        # چک کردن انطباق service با salon
        if hasattr(self, 'service') and hasattr(self, 'salon'):
            if self.service.salon != self.salon:
                errors['service'] = 'خدمت انتخابی متعلق به این سالن نیست'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        # تنظیم خودکار قیمت از روی سرویس
        if not self.total_price and hasattr(self, 'service'):
            self.total_price = self.service.price
        
        # اطمینان از اینکه customer نقش customer داشته باشد
        if self.customer.role != 'customer':
            self.customer.role = 'customer'
            self.customer.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.service.name} - {self.get_persian_date()}"
    
    def get_persian_date(self):
        """تبدیل تاریخ به شمسی"""
        try:
            gregorian_date = self.appointment_date
            persian_date = jdatetime.date.fromgregorian(
                year=gregorian_date.year,
                month=gregorian_date.month,
                day=gregorian_date.day
            )
            return persian_date.strftime('%Y/%m/%d')
        except:
            return str(self.appointment_date)
    
    def get_status_display_fa(self):
        """نمایش وضعیت به فارسی"""
        status_fa = dict(self.STATUS_CHOICES)
        return status_fa.get(self.status, self.status)
    
    def get_appointment_datetime(self):
        """ترکیب تاریخ و ساعت"""
        return datetime.combine(self.appointment_date, self.appointment_time)
    
    def is_upcoming(self):
        """آیا نوبت در آینده است؟"""
        return self.get_appointment_datetime() > timezone.now()
    
    def can_be_cancelled(self):
        """آیا قابل لغو است؟"""
        if self.status in ['completed', 'cancelled', 'no_show']:
            return False
        # حداقل 2 ساعت قبل از نوبت قابل لغو است
        return self.get_appointment_datetime() > timezone.now() + timedelta(hours=2)


class TimeSlot(models.Model):
    """بازه‌های زمانی موجود برای رزرو"""
    salon = models.ForeignKey('salons.Salon', on_delete=models.CASCADE, related_name='time_slots')
    staff = models.ForeignKey('salons.Staff', on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['salon', 'staff', 'date', 'start_time']
        verbose_name = 'بازه زمانی'
        verbose_name_plural = 'بازه‌های زمانی'
        ordering = ['date', 'start_time']
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('ساعت شروع باید قبل از ساعت پایان باشد')
        
        if self.date < timezone.now().date():
            raise ValidationError('تاریخ نمی‌تواند در گذشته باشد')
    
    def __str__(self):
        return f"{self.salon.name} - {self.staff.user.get_full_name()} - {self.date} ({self.start_time}-{self.end_time})"
    
    @property
    def duration_minutes(self):
        """محاسبه مدت زمان بازه به دقیقه"""
        start_dt = datetime.combine(self.date, self.start_time)
        end_dt = datetime.combine(self.date, self.end_time)
        return int((end_dt - start_dt).total_seconds() / 60)