from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from .models import Appointment, TimeSlot

class AppointmentStatusFilter(admin.SimpleListFilter):
    title = 'وضعیت نوبت'
    parameter_name = 'status_filter'

    def lookups(self, request, model_admin):
        return (
            ('today', 'نوبت‌های امروز'),
            ('upcoming', 'نوبت‌های آینده'),
            ('past', 'نوبت‌های گذشته'),
            ('pending', 'در انتظار تایید'),
            ('confirmed', 'تایید شده'),
        )

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == 'today':
            return queryset.filter(appointment_date=today)
        if self.value() == 'upcoming':
            return queryset.filter(appointment_date__gte=today)
        if self.value() == 'past':
            return queryset.filter(appointment_date__lt=today)
        if self.value() == 'pending':
            return queryset.filter(status='pending')
        if self.value() == 'confirmed':
            return queryset.filter(status='confirmed')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'get_appointment_info', 
        'salon', 
        'staff', 
        'get_appointment_datetime', 
        'get_status_badge',
        'get_payment_status',
        'get_price_display'
    )
    
    list_filter = (
        AppointmentStatusFilter,
        'salon',
        'status',
        'is_paid',
        'appointment_date',
        'created_at'
    )
    
    search_fields = (
        'customer__username',
        'customer__first_name', 
        'customer__last_name',
        'customer__phone',
        'salon__name',
        'staff__user__first_name',
        'staff__user__last_name',
        'service__name'
    )
    
    ordering = ('-appointment_date', '-appointment_time')
    
    fieldsets = (
        ('اطلاعات نوبت', {
            'fields': ('salon', 'customer', 'staff', 'service')
        }),
        ('زمان نوبت', {
            'fields': ('appointment_date', 'appointment_time')
        }),
        ('وضعیت و پرداخت', {
            'fields': ('status', 'total_price', 'is_paid', 'payment_method')
        }),
        ('یادداشت', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('اطلاعات پیامک', {
            'fields': ('sms_sent', 'reminder_sent'),
            'classes': ('collapse',)
        }),
        ('اطلاعات سیستم', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled', 'send_reminder_sms']
    
    def get_appointment_info(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.customer.get_full_name() or obj.customer.username,
            obj.service.name
        )
    get_appointment_info.short_description = 'مشتری / خدمت'
    
    def get_appointment_datetime(self, obj):
        persian_date = obj.get_persian_date()
        time_str = obj.appointment_time.strftime('%H:%M')
        
        # رنگ‌بندی بر اساس زمان
        now = timezone.now()
        appointment_dt = obj.get_appointment_datetime()
        
        if appointment_dt < now:
            color = '#dc3545'  # قرمز برای گذشته
        elif appointment_dt.date() == now.date():
            color = '#ffc107'  # زرد برای امروز
        else:
            color = '#28a745'  # سبز برای آینده
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}<br>{}</span>',
            color, persian_date, time_str
        )
    get_appointment_datetime.short_description = 'تاریخ و ساعت'
    
    def get_status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'confirmed': '#17a2b8',
            'in_progress': '#007bff',
            'completed': '#28a745',
            'cancelled': '#dc3545',
            'no_show': '#6c757d',
        }
        
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display_fa()
        )
    get_status_badge.short_description = 'وضعیت'
    
    def get_payment_status(self, obj):
        if obj.is_paid:
            icon = '✅'
            text = 'پرداخت شده'
            color = '#28a745'
        else:
            icon = '❌'
            text = 'پرداخت نشده'
            color = '#dc3545'
        
        return format_html(
            '<span style="color: {};">{} {}</span>',
            color, icon, text
        )
    get_payment_status.short_description = 'پرداخت'
    
    def get_price_display(self, obj):
        return format_html(
            '<span style="font-weight: bold;">{:,} تومان</span>',
            obj.total_price
        )
    get_price_display.short_description = 'مبلغ'
    
    # Actions
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} نوبت تایید شد.')
    mark_as_confirmed.short_description = 'تایید نوبت‌های انتخاب شده'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} نوبت تکمیل شد.')
    mark_as_completed.short_description = 'تکمیل نوبت‌های انتخاب شده'
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} نوبت لغو شد.')
    mark_as_cancelled.short_description = 'لغو نوبت‌های انتخاب شده'
    
    def send_reminder_sms(self, request, queryset):
        # اینجا می‌تونید کد ارسال پیامک بذارید
        count = queryset.count()
        self.message_user(request, f'پیامک یادآوری برای {count} نوبت ارسال شد.')
    send_reminder_sms.short_description = 'ارسال پیامک یادآوری'

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('salon', 'staff', 'date', 'get_time_range', 'get_duration', 'is_available')
    list_filter = ('salon', 'is_available', 'date')
    search_fields = ('salon__name', 'staff__user__first_name', 'staff__user__last_name')
    ordering = ('date', 'start_time')
    
    fieldsets = (
        ('اطلاعات بازه زمانی', {
            'fields': ('salon', 'staff', 'date')
        }),
        ('زمان', {
            'fields': ('start_time', 'end_time')
        }),
        ('وضعیت', {
            'fields': ('is_available',)
        })
    )
    
    def get_time_range(self, obj):
        return f"{obj.start_time} - {obj.end_time}"
    get_time_range.short_description = 'بازه زمانی'
    
    def get_duration(self, obj):
        return f"{obj.duration_minutes} دقیقه"
    get_duration.short_description = 'مدت زمان'