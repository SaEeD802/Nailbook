from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Service Management (for salon owners)
    path('<int:salon_id>/', views.service_list, name='list'),
    path('<int:salon_id>/create/', views.service_create, name='create'),
    path('<int:service_id>/edit/', views.service_edit, name='edit'),
    path('<int:service_id>/delete/', views.service_delete, name='delete'),
    
    # Public Service Views (for customers)
    path('<int:salon_id>/public/', views.public_services, name='public_list'),
    path('<int:service_id>/detail/', views.service_detail, name='detail'),
]

