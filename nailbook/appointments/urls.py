from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Customer URLs
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('salons/', views.salon_list, name='salon_list'),
    path('book/<int:salon_id>/', views.appointment_book, name='book'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    
    # Appointment Management
    path('<int:appointment_id>/', views.appointment_detail, name='detail'),
    path('<int:appointment_id>/cancel/', views.appointment_cancel, name='cancel'),
    path('<int:appointment_id>/reschedule/', views.appointment_reschedule, name='reschedule'),
    
    # AJAX URLs
    path('available-times/<int:salon_id>/', views.get_available_times, name='available_times'),
    path('update-status/<int:appointment_id>/', views.appointment_update_status, name='update_status'),
    path('calendar-data/<int:salon_id>/', views.appointment_calendar_data, name='calendar_data'),
    
    # Booking without login (for walk-in customers)
    path('quick-book/<int:salon_id>/', views.quick_book, name='quick_book'),
    path('booking-success/<int:appointment_id>/', views.booking_success, name='booking_success'),
    
    # Admin/Staff URLs
    path('manage/<int:salon_id>/', views.appointment_manage, name='manage'),
    path('today/<int:salon_id>/', views.today_appointments, name='today'),
]

