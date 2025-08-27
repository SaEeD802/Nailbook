from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Salon, Staff

class StaffInline(admin.TabularInline):
    model = Staff
    extra = 0
    fields = ('user', 'specialties', 'is_available')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = Staff._meta.get_field('user').remote_field.model.objects.filter(role='staff')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'phone', 'get_staff_count', 'get_working_hours', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'owner')
    search_fields = ('name', 'owner__username', 'owner__phone', 'phone', 'address')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'owner', 'phone', 'address')
        }),
        ('ساعات کاری', {
            'fields': ('opening_time', 'closing_time', 'closed_days'),
            'description': 'روزهای تعطیل را با کاما جدا کنید (مثال: friday,saturday)'
        }),
        ('وضعیت', {
            'fields': ('is_active', 'created_at')
        })
    )
    
    readonly_fields = ('created_at',)
    inlines = [StaffInline]
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            kwargs["queryset"] = Salon._meta.get_field('owner').remote_field.model.objects.filter(role='salon_owner')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_staff_count(self, obj):
        count = obj.staff_members.count()
        if count > 0:
            return format_html(
                '<a href="{}?salon__id__exact={}">{} نفر</a>',
                reverse('admin:salons_staff_changelist'),
                obj.id,
                count
            )
        return '0 نفر'
    get_staff_count.short_description = 'تعداد کارمند'
    
    def get_working_hours(self, obj):
        return f"{obj.opening_time} - {obj.closing_time}"
    get_working_hours.short_description = 'ساعات کاری'

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('get_staff_name', 'salon', 'get_specialties', 'is_available')
    list_filter = ('salon', 'is_available')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'salon__name', 'specialties')
    
    fieldsets = (
        ('اطلاعات کارمند', {
            'fields': ('user', 'salon')
        }),
        ('تخصص و وضعیت', {
            'fields': ('specialties', 'is_available')
        })
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = Staff._meta.get_field('user').remote_field.model.objects.filter(role='staff')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_staff_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_staff_name.short_description = 'نام کارمند'
    
    def get_specialties(self, obj):
        if obj.specialties:
            specs = obj.specialties.split(',')
            if len(specs) <= 3:
                return obj.specialties
            return f"{', '.join(specs[:3])}..."
        return 'تعریف نشده'
    get_specialties.short_description = 'تخصص‌ها'

