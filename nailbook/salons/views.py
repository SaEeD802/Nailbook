from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from .models import Salon, Staff
from services.models import Service
from appointments.models import Appointment
import json

@login_required
def salon_dashboard(request):
    """داشبورد مسئول سالن"""
    if request.user.role != 'salon_owner':
        messages.error(request, 'دسترسی غیر مجاز')
        return redirect('accounts:login')
    
    # سالن‌های کاربر
    salons = Salon.objects.filter(owner=request.user).prefetch_related('staff_members', 'services')
    
    if not salons.exists():
        return render(request, 'salons/no_salon.html')
    
    # انتخاب سالن فعال
    selected_salon_id = request.GET.get('salon_id')
    if selected_salon_id:
        selected_salon = get_object_or_404(salons, id=selected_salon_id)
    else:
        selected_salon = salons.first()
    
    # آمار امروز
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(
        salon=selected_salon,
        appointment_date=today
    )
    
    stats = {
        'today_appointments': today_appointments.count(),
        'today_revenue': today_appointments.filter(is_paid=True).aggregate(
            total=Sum('total_price')
        )['total'] or 0,
        'pending_appointments': today_appointments.filter(status='pending').count(),
        'staff_count': selected_salon.staff_members.count(),
    }
    
    # نوبت‌های امروز
    upcoming_appointments = today_appointments.filter(
        status__in=['confirmed', 'pending']
    ).select_related('customer', 'staff__user', 'service').order_by('appointment_time')
    
    # آمار هفتگی
    week_start = today - timedelta(days=today.weekday())
    week_appointments = Appointment.objects.filter(
        salon=selected_salon,
        appointment_date__gte=week_start,
        appointment_date__lte=today
    )
    
    weekly_revenue = week_appointments.filter(is_paid=True).aggregate(
        total=Sum('total_price')
    )['total'] or 0
    
    context = {
        'salons': salons,
        'selected_salon': selected_salon,
        'stats': stats,
        'upcoming_appointments': upcoming_appointments,
        'weekly_revenue': weekly_revenue,
    }
    
    return render(request, 'salons/dashboard.html', context)

@login_required
def salon_create(request):
    """ایجاد سالن جدید"""
    if request.user.role != 'salon_owner':
        messages.error(request, 'دسترسی غیر مجاز')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        salon = Salon.objects.create(
            name=request.POST.get('name'),
            owner=request.user,
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            opening_time=request.POST.get('opening_time', '09:00'),
            closing_time=request.POST.get('closing_time', '21:00'),
            closed_days=request.POST.get('closed_days', '')
        )
        messages.success(request, f'سالن {salon.name} با موفقیت ایجاد شد')
        return redirect('salons:dashboard')
    
    return render(request, 'salons/create.html')

@login_required
def staff_list(request, salon_id):
    """لیست کارمندان سالن"""
    salon = get_object_or_404(Salon, id=salon_id, owner=request.user)
    staff_members = salon.staff_members.select_related('user').all()
    
    context = {
        'salon': salon,
        'staff_members': staff_members
    }
    return render(request, 'salons/staff_list.html', context)

@login_required
def staff_dashboard(request):
    """داشبورد کارمند"""
    if request.user.role != 'staff':
        messages.error(request, 'دسترسی غیر مجاز')
        return redirect('accounts:login')
    
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        messages.error(request, 'اطلاعات کارمند یافت نشد')
        return redirect('accounts:login')
    
    # نوبت‌های امروز
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(
        staff=staff,
        appointment_date=today
    ).select_related('customer', 'service').order_by('appointment_time')
    
    # آمار
    stats = {
        'today_appointments': today_appointments.count(),
        'completed_today': today_appointments.filter(status='completed').count(),
        'pending_appointments': today_appointments.filter(status='pending').count(),
    }
    
    context = {
        'staff': staff,
        'today_appointments': today_appointments,
        'stats': stats
    }
    
    return render(request, 'salons/staff_dashboard.html', context)

