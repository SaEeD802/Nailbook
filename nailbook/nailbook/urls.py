from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def home_redirect(request):
    """هدایت صفحه اصلی به لیست سالن‌ها"""
    return redirect('appointments:salon_list')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    
    # App URLs
    path('accounts/', include('accounts.urls')),
    path('salons/', include('salons.urls')),
    path('services/', include('services.urls')),
    path('appointments/', include('appointments.urls')),
    
    # API URLs (for future use)
    path('api/v1/', include('api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "نیل بوک - پنل مدیریت"
admin.site.site_title = "نیل بوک"
admin.site.index_title = "خوش آمدید به پنل مدیریت نیل بوک"

