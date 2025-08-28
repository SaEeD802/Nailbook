from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
import json

from salons.models import Salon, Staff
from services.models import Service
from appointments.models import Appointment

@api_view(['GET'])
@permission_classes([AllowAny])
def salon_list_api(request):
    """API لیست سالن‌ها"""
    salons = Salon.objects.filter(is_active=True).values(
        'id', 'name', 'phone', 'address', 'opening_time', 'closing_time'
    )
    return Response(list(salons))

@api_view(['GET'])
@permission_classes([AllowAny])
def salon_services_api(request, salon_id):
    """API خدمات سالن"""
    salon = get_object_or_404(Salon, id=salon_id, is_active=True)
    services = salon.services.filter(is_active=True).values(
        'id', 'name', 'description', 'price', 'duration'
    )
    return Response(list(services))

@api_view(['GET'])
@permission_classes([AllowAny])
def available_times_api(request, salon_id):
    """API ساعات خالی"""
    salon = get_object_or_404(Salon, id=salon_id)
    date_str = request.GET.get('date')
    staff_id = request.GET.get('staff_id')
    
    if not date_str or not staff_id:
        return Response({'error': 'تاریخ و کارمند الزامی است'}, status=400)
    
    try:
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        staff = get_object_or_404(Staff, id=staff_id, salon=salon)
        
        # ساعات رزرو شده
        booked_times = Appointment.objects.filter(
            salon=salon,
            staff=staff,
            appointment_date=appointment_date,
            status__in=['pending', 'confirmed', 'in_progress']
        ).values_list('appointment_time', flat=True)
        
        # تولید ساعات موجود
        available_times = []
        current_time = datetime.combine(appointment_date, salon.opening_time)
        end_time = datetime.combine(appointment_date, salon.closing_time)
        
        while current_time < end_time:
            time_only = current_time.time()
            if time_only not in booked_times:
                available_times.append(time_only.strftime('%H:%M'))
            current_time += timedelta(minutes=30)
        
        return Response({'available_times': available_times})
    
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def appointment_create_api(request):
    """API ایجاد نوبت"""
    try:
        data = request.data
        
        salon = get_object_or_404(Salon, id=data['salon_id'])
        service = get_object_or_404(Service, id=data['service_id'])
        staff = get_object_or_404(Staff, id=data['staff_id'])
        
        appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        
        # بررسی تداخل
        if Appointment.objects.filter(
            salon=salon,
            staff=staff,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status__in=['pending', 'confirmed', 'in_progress']
        ).exists():
            return Response({'error': 'این زمان رزرو شده است'}, status=400)
        
        # ایجاد نوبت
        appointment = Appointment.objects.create(
            salon=salon,
            customer=request.user if request.user.is_authenticated else None,
            staff=staff,
            service=service,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            total_price=service.price,
            notes=data.get('notes', '')
        )
        
        return Response({
            'id': appointment.id,
            'message': 'نوبت با موفقیت ثبت شد'
        }, status=201)
        
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def appointment_detail_api(request, appointment_id):
    """API جزئیات نوبت"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    data = {
        'id': appointment.id,
        'salon': appointment.salon.name,
        'customer': appointment.customer.get_full_name() if appointment.customer else 'مهمان',
        'staff': appointment.staff.user.get_full_name(),
        'service': appointment.service.name,
        'appointment_date': appointment.appointment_date.strftime('%Y-%m-%d'),
        'appointment_time': appointment.appointment_time.strftime('%H:%M'),
        'status': appointment.get_status_display_fa(),
        'total_price': appointment.total_price,
        'is_paid': appointment.is_paid,
        'notes': appointment.notes
    }
    
    return Response(data)
