from django.urls import path
from . import views

app_name = 'salons'

urlpatterns = [
    # Dashboard URLs
    path('dashboard/', views.salon_dashboard, name='dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    
    # Salon Management
    path('create/', views.salon_create, name='create'),
    path('<int:salon_id>/edit/', views.salon_edit, name='edit'),
    path('<int:salon_id>/delete/', views.salon_delete, name='delete'),
    
    # Staff Management
    path('<int:salon_id>/staff/', views.staff_list, name='staff_list'),
    path('<int:salon_id>/staff/add/', views.staff_add, name='staff_add'),
    path('staff/<int:staff_id>/edit/', views.staff_edit, name='staff_edit'),
    path('staff/<int:staff_id>/delete/', views.staff_delete, name='staff_delete'),
    
    # Reports & Analytics
    path('<int:salon_id>/reports/', views.salon_reports, name='reports'),
    path('<int:salon_id>/analytics/', views.salon_analytics, name='analytics'),
]

