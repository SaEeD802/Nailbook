from django.db import models

from nailbook.salons.models import Salon

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200, verbose_name='نام خدمت')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    price = models.PositiveIntegerField(verbose_name='قیمت (تومان)')
    duration = models.PositiveIntegerField(verbose_name='مدت زمان (دقیقه)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.salon.name}"
    
    def get_price_display(self):
        return f"{self.price:,} تومان"
        