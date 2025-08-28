from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

# Router برای ViewSets
router = DefaultRouter()

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    path('salons/', views.salon_list_api, name='salon_list'),
    path('salons/<int:salon_id>/services/', views.salon_services_api, name='salon_services'),
    path('salons/<int:salon_id>/available-times/', views.available_times_api, name='available_times'),
    path('appointments/', views.appointment_create_api, name='appointment_create'),
    path('appointments/<int:appointment_id>/', views.appointment_detail_api, name='appointment_detail'),
]