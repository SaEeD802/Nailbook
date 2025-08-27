from django.db import models
from django.utils import timezone
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
    
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='appointments')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    appointment_date = models.DateField(verbose_name='تاریخ نوبت')
    appointment_time = models.TimeField(verbose_name='ساعت نوبت')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, verbose_name='یادداشت')
    
    # پرداخت
    total_price = models.PositiveIntegerField(verbose_name='مبلغ کل')
    is_paid = models.BooleanField(default=False)
    
    # SMS
    sms_sent = models.BooleanField(default=False, verbose_name='پیامک ارسال شده')
    reminder_sent = models.BooleanField(default=False, verbose_name='یادآوری ارسال شده')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        unique_together = ['salon', 'staff', 'appointment_date', 'appointment_time']
    
    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.service.name} - {self.get_persian_date()}"
    
    def get_persian_date(self):
        """تبدیل تاریخ به شمسی"""
        gregorian_date = self.appointment_date
        persian_date = jdatetime.date.fromgregorian(
            year=gregorian_date.year,
            month=gregorian_date.month,
            day=gregorian_date.day
        )
        return persian_date.strftime('%Y/%m/%d')
    
    def get_status_display_fa(self):
        """نمایش وضعیت به فارسی"""
        status_fa = dict(self.STATUS_CHOICES)
        return status_fa.get(self.status, self.status)


class TimeSlot(models.Model):
    """بازه‌های زمانی موجود برای رزرو"""
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='time_slots')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['salon', 'staff', 'date', 'start_time']
    
    def __str__(self):
        return f"{self.salon.name} - {self.staff.user.get_full_name()} - {self.date} {self.start_time}"