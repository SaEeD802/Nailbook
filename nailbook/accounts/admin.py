from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.html import format_html
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'phone', 'role', 'first_name', 'last_name', 'email')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('username', 'phone', 'get_full_name', 'role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active', 'created_at')
    search_fields = ('username', 'phone', 'first_name', 'last_name', 'email')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('اطلاعات اضافی', {
            'fields': ('role', 'phone', 'created_at'),
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('اطلاعات اضافی', {
            'fields': ('role', 'phone', 'first_name', 'last_name', 'email'),
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username
    get_full_name.short_description = 'نام کامل'

