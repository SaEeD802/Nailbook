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
from accounts.models import User
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
    
    # نوبت‌های این هفته
    week_start = today - timezone.timedelta(days=today.weekday())
    week_end = week_start + timezone.timedelta(days=6)
    week_appointments = Appointment.objects.filter(
        staff=staff,
        appointment_date__range=[week_start, week_end]
    ).count()
    
    # آمار
    stats = {
        'today_appointments': today_appointments.count(),
        'completed_today': today_appointments.filter(status='completed').count(),
        'pending_appointments': today_appointments.filter(status='pending').count(),
        'week_appointments': week_appointments,
    }
    
    context = {
        'staff': staff,
        'salon': staff.salon,
        'today_appointments': today_appointments,
        'stats': stats
    }
    
    return render(request, 'salons/staff_dashboard.html', context)

@login_required
def salon_edit(request, salon_id):
    """ویرایش سالن"""
    salon = get_object_or_404(Salon, id=salon_id, owner=request.user)
    
    if request.method == 'POST':
        salon.name = request.POST.get('name')
        salon.phone = request.POST.get('phone')
        salon.address = request.POST.get('address')
        salon.opening_time = request.POST.get('opening_time')
        salon.closing_time = request.POST.get('closing_time')
        salon.closed_days = request.POST.get('closed_days', '')
        salon.save()
        
        messages.success(request, 'اطلاعات سالن بروزرسانی شد')
        return redirect('salons:dashboard')
    
    context = {'salon': salon}
    return render(request, 'salons/edit.html', context)

@login_required
def salon_delete(request, salon_id):
    """حذف سالن"""
    salon = get_object_or_404(Salon, id=salon_id, owner=request.user)
    
    if request.method == 'POST':
        salon_name = salon.name
        salon.delete()
        messages.success(request, f'سالن {salon_name} حذف شد')
        return redirect('salons:dashboard')
    
    context = {'salon': salon}
    return render(request, 'salons/delete_confirm.html', context)

@login_required
def staff_add(request, salon_id):
    """اضافه کردن کارمند"""
    salon = get_object_or_404(Salon, id=salon_id, owner=request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        specialties = request.POST.get('specialties', '')
        
        # بررسی وجود کاربر
        if User.objects.filter(username=username).exists():
            messages.error(request, 'این نام کاربری قبلاً استفاده شده است')
            return render(request, 'salons/staff_add.html', {'salon': salon})
        
        # ایجاد کاربر کارمند
        user = User.objects.create_user(
            username=username,
            password=password,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            role='staff'
        )
        
        # ایجاد کارمند
        Staff.objects.create(
            user=user,
            salon=salon,
            specialties=specialties
        )
        
        messages.success(request, f'کارمند {user.get_full_name()} اضافه شد')
        return redirect('salons:staff_list', salon_id=salon.id)
    
    context = {'salon': salon}
    return render(request, 'salons/staff_add.html', context)

@login_required
def staff_edit(request, staff_id):
    """ویرایش کارمند"""
    staff = get_object_or_404(Staff, id=staff_id)
    
    # بررسی مجوز
    if staff.salon.owner != request.user:
        messages.error(request, 'دسترسی غیر مجاز')
        return redirect('salons:dashboard')
    
    if request.method == 'POST':
        staff.user.first_name = request.POST.get('first_name', '')
        staff.user.last_name = request.POST.get('last_name', '')
        staff.user.phone = request.POST.get('phone', '')
        staff.user.save()
        
        staff.specialties = request.POST.get('specialties', '')
        staff.is_available = request.POST.get('is_available') == 'on'
        staff.save()
        
        messages.success(request, 'اطلاعات کارمند بروزرسانی شد')
        return redirect('salons:staff_list', salon_id=staff.salon.id)
    
    context = {
        'staff': staff,
        'salon': staff.salon
    }
    return render(request, 'salons/staff_edit.html', context)

@login_required
def staff_delete(request, staff_id):
    """حذف کارمند"""
    staff = get_object_or_404(Staff, id=staff_id)
    
    # بررسی مجوز
    if staff.salon.owner != request.user:
        messages.error(request, 'دسترسی غیر مجاز')
        return redirect('salons:dashboard')
    
    if request.method == 'POST':
        salon_id = staff.salon.id
        staff_name = staff.user.get_full_name()
        staff.user.delete()  # حذف کاربر که کارمند هم حذف می‌شود
        
        messages.success(request, f'کارمند {staff_name} حذف شد')
        return redirect('salons:staff_list', salon_id=salon_id)
    
    context = {'staff': staff}
    return render(request, 'salons/staff_delete_confirm.html', context)

@login_required
def salon_reports(request, salon_id):
    """گزارشات سالن"""
    salon = get_object_or_404(Salon, id=salon_id, owner=request.user)
    
    # فیلتر تاریخ
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    appointments = Appointment.objects.filter(salon=salon)
    
    if from_date:
        appointments = appointments.filter(appointment_date__gte=from_date)
    if to_date:
        appointments = appointments.filter(appointment_date__lte=to_date)
    
    # آمار کلی
    total_appointments = appointments.count()
    completed_appointments = appointments.filter(status='completed').count()
    total_revenue = appointments.filter(is_paid=True).aggregate(
        total=Sum('total_price')
    )['total'] or 0
    
    # آمار ماهانه
    monthly_stats = appointments.filter(
        appointment_date__gte=timezone.now().date().replace(day=1)
    ).aggregate(
        count=Count('id'),
        revenue=Sum('total_price', filter=Q(is_paid=True))
    )
    
    context = {
        'salon': salon,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'total_revenue': total_revenue,
        'monthly_stats': monthly_stats,
        'from_date': from_date,
        'to_date': to_date
    }
    
    return render(request, 'salons/reports.html', context)

@login_required
def salon_analytics(request, salon_id):
    """تحلیل‌های سالن"""
    salon = get_object_or_404(Salon, id=salon_id, owner=request.user)
    
    # آمار 30 روز گذشته
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_appointments = Appointment.objects.filter(
        salon=salon,
        appointment_date__gte=thirty_days_ago
    )
    
    # محبوب‌ترین خدمات
    popular_services = recent_appointments.values('service__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # بهترین کارمندان
    top_staff = recent_appointments.values(
        'staff__user__first_name', 'staff__user__last_name'
    ).annotate(
        count=Count('id'),
        revenue=Sum('total_price', filter=Q(is_paid=True))
    ).order_by('-revenue')[:5]
    
    # آمار روزانه
    daily_stats = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        day_appointments = recent_appointments.filter(appointment_date=date)
        daily_stats.append({
            'date': date,
            'count': day_appointments.count(),
            'revenue': day_appointments.filter(is_paid=True).aggregate(
                total=Sum('total_price')
            )['total'] or 0
        })
    
    context = {
        'salon': salon,
        'popular_services': popular_services,
        'top_staff': top_staff,
        'daily_stats': daily_stats
    }
    
    return render(request, 'salons/analytics.html', context)

