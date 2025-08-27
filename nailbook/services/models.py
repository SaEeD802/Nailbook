from django.db import models
from django.core.validators import MinValueValidator

class Service(models.Model):
    salon = models.ForeignKey('salons.Salon', on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200, verbose_name='نام خدمت')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    price = models.PositiveIntegerField(
        verbose_name='قیمت (تومان)',
        validators=[MinValueValidator(1000, message='قیمت باید حداقل 1000 تومان باشد')]
    )
    duration = models.PositiveIntegerField(
        verbose_name='مدت زمان (دقیقه)',
        validators=[MinValueValidator(15, message='مدت زمان باید حداقل 15 دقیقه باشد')]
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.salon.name}"
    
    def get_price_display(self):
        return f"{self.price:,} تومان"
    
    def get_duration_display(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        if hours > 0:
            return f"{hours} ساعت و {minutes} دقیقه"
        return f"{minutes} دقیقه"

    class Meta:
        verbose_name = 'خدمت'
        verbose_name_plural = 'خدمات'
        ordering = ['name']

