from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'salon', 'get_price_display', 'get_duration_display', 'is_active', 'created_at')
    list_filter = ('salon', 'is_active', 'created_at')
    search_fields = ('name', 'salon__name', 'description')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('اطلاعات خدمت', {
            'fields': ('name', 'salon', 'description')
        }),
        ('قیمت و زمان', {
            'fields': ('price', 'duration')
        }),
        ('وضعیت', {
            'fields': ('is_active', 'created_at')
        })
    )
    
    readonly_fields = ('created_at',)
    
    def get_price_display(self, obj):
        return format_html(
            '<span style="color: green; font-weight: bold;">{:,} تومان</span>',
            obj.price
        )
    get_price_display.short_description = 'قیمت'
    
    def get_duration_display(self, obj):
        hours = obj.duration // 60
        minutes = obj.duration % 60
        if hours > 0:
            return f"{hours} ساعت و {minutes} دقیقه"
        return f"{minutes} دقیقه"
    get_duration_display.short_description = 'مدت زمان'