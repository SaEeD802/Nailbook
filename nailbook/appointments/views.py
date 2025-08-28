from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta, time
from .models import Appointment, TimeSlot
from salons.models import Salon, Staff
from services.models import Service
from accounts.models import User
import json

@login_required
def customer_dashboard(request):
    """داشبورد مشتری"""
    # نوبت‌های آینده
    upcoming_appointments = Appointment.objects.filter(
        customer=request.user,
        appointment_date__gte=timezone.now().date()
    ).select_related('salon', 'staff__user', 'service').order_by('appointment_date', 'appointment_time')
    
    # نوبت‌های گذشته
    past_appointments = Appointment.objects.filter(
        customer=request.user,
        appointment_date__lt=timezone.now().date()
    ).select_related('salon', 'staff__user', 'service').order_by('-appointment_date', '-appointment_time')[:10]
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments
    }
    return render(request, 'appointments/customer_dashboard.html', context)

def salon_list(request):
    """لیست عمومی سالن‌ها"""
    salons = Salon.objects.filter(is_active=True).select_related('owner')
    
    # جستجو
    search = request.GET.get('search', '')
    if search:
        salons = salons.filter(
            Q(name__icontains=search) | Q(address__icontains=search)
        )
    
    context = {
        'salons': salons,
        'search': search
    }
    return render(request, 'appointments/salon_list.html', context)

def appointment_book(request, salon_id):
    """رزرو نوبت"""
    salon = get_object_or_404(Salon, id=salon_id, is_active=True)
    services = salon.services.filter(is_active=True)
    staff_members = salon.staff_members.all().select_related('user')
    
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        staff_id = request.POST.get('staff_id')
        appointment_date = request.POST.get('appointment_date_gregorian') or request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        notes = request.POST.get('notes', '')
        
        # اعتبارسنجی
        try:
            service = get_object_or_404(Service, id=service_id, salon=salon)
            staff = get_object_or_404(Staff, id=staff_id, salon=salon)
            
            # تبدیل تاریخ و ساعت
            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            appointment_time = datetime.strptime(appointment_time, '%H:%M').time()
            
            # بررسی تداخل زمانی
            existing_appointment = Appointment.objects.filter(
                salon=salon,
                staff=staff,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=['pending', 'confirmed', 'in_progress']
            ).exists()
            
            if existing_appointment:
                messages.error(request, 'این زمان قبلاً رزرو شده است')
                return redirect('appointments:book', salon_id=salon.id)
            
            # ایجاد نوبت
            appointment = Appointment.objects.create(
                salon=salon,
                customer=request.user if request.user.is_authenticated else None,
                staff=staff,
                service=service,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                total_price=service.price,
                notes=notes
            )
            
            messages.success(request, 'نوبت شما با موفقیت ثبت شد')
            
            if request.user.is_authenticated:
                return redirect('appointments:customer_dashboard')
            else:
                return render(request, 'appointments/booking_success.html', {'appointment': appointment})
        
        except Exception as e:
            messages.error(request, f'خطا در ثبت نوبت: {str(e)}')
    
    context = {
        'salon': salon,
        'services': services,
        'staff_members': staff_members
    }
    return render(request, 'appointments/book.html', context)

@require_http_methods(["GET"])
def get_available_times(request, salon_id):
    """دریافت ساعات خالی برای رزرو (AJAX)"""
    salon = get_object_or_404(Salon, id=salon_id)
    date_str = request.GET.get('date')
    staff_id = request.GET.get('staff_id')
    
    if not date_str or not staff_id:
        return JsonResponse({'error': 'تاریخ و کارمند الزامی است'}, status=400)
    
    try:
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        staff = get_object_or_404(Staff, id=staff_id, salon=salon)
        
        # ساعات کاری سالن
        opening_time = salon.opening_time
        closing_time = salon.closing_time
        
        # ساعات رزرو شده
        booked_times = Appointment.objects.filter(
            salon=salon,
            staff=staff,
            appointment_date=appointment_date,
            status__in=['pending', 'confirmed', 'in_progress']
        ).values_list('appointment_time', flat=True)
        
        # تولید ساعات موجود (هر 30 دقیقه)
        available_times = []
        current_time = datetime.combine(appointment_date, opening_time)
        end_time = datetime.combine(appointment_date, closing_time)
        
        while current_time < end_time:
            time_only = current_time.time()
            if time_only not in booked_times:
                available_times.append(time_only.strftime('%H:%M'))
            current_time += timedelta(minutes=30)
        
        return JsonResponse({'available_times': available_times})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def appointment_cancel(request, appointment_id):
    """لغو نوبت"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # بررسی مجوز
    if not (appointment.customer == request.user or 
            appointment.salon.owner == request.user or
            (hasattr(request.user, 'staff') and request.user.staff.salon == appointment.salon)):
        messages.error(request, 'دسترسی غیر مجاز')
        return redirect('appointments:customer_dashboard')
    
    if not appointment.can_be_cancelled():
        messages.error(request, 'این نوبت قابل لغو نیست')
        return redirect('appointments:customer_dashboard')
    
    appointment.status = 'cancelled'
    appointment.save()
    
    messages.success(request, 'نوبت با موفقیت لغو شد')
    
    # هدایت بر اساس نقش کاربر
    if request.user.role == 'salon_owner':
        return redirect('salons:dashboard')
    elif request.user.role == 'staff':
        return redirect('salons:staff_dashboard')
    else:
        return redirect('appointments:customer_dashboard')

@login_required
def appointment_update_status(request, appointment_id):
    """تغییر وضعیت نوبت"""
    if request.method != 'POST':
        return JsonResponse({'error': 'فقط POST مجاز است'}, status=405)
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # بررسی مجوز (فقط مسئول سالن و کارمند)
    if not (appointment.salon.owner == request.user or 
            (hasattr(request.user, 'staff') and request.user.staff.salon == appointment.salon)):
        return JsonResponse({'error': 'دسترسی غیر مجاز'}, status=403)
    
    new_status = request.POST.get('status')
    if new_status not in dict(Appointment.STATUS_CHOICES):
        return JsonResponse({'error': 'وضعیت نامعتبر'}, status=400)
    
    appointment.status = new_status
    appointment.save()
    
    return JsonResponse({
        'success': True,
        'status': appointment.get_status_display_fa(),
        'status_value': appointment.status
    })

def appointment_calendar_data(request, salon_id):
    """داده‌های تقویم برای نمایش نوبت‌ها (AJAX)"""
    salon = get_object_or_404(Salon, id=salon_id)
    
    # بررسی مجوز
    if not (salon.owner == request.user or 
            (hasattr(request.user, 'staff') and request.user.staff.salon == salon)):
        return JsonResponse({'error': 'دسترسی غیر مجاز'}, status=403)
    
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    if start_date and end_date:
        appointments = Appointment.objects.filter(
            salon=salon,
            appointment_date__gte=start_date,
            appointment_date__lte=end_date
        ).select_related('customer', 'staff__user', 'service')
    else:
        # نوبت‌های این ماه
        today = timezone.now().date()
        month_start = today.replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        
        appointments = Appointment.objects.filter(
            salon=salon,
            appointment_date__gte=month_start,
            appointment_date__lt=next_month
        ).select_related('customer', 'staff__user', 'service')
    
    # تبدیل به فرمت FullCalendar
    events = []
    for appointment in appointments:
        color = {
            'pending': '#ffc107',
            'confirmed': '#17a2b8', 
            'in_progress': '#007bff',
            'completed': '#28a745',
            'cancelled': '#dc3545',
            'no_show': '#6c757d',
        }.get(appointment.status, '#6c757d')
        
        events.append({
            'id': appointment.id,
            'title': f"{appointment.customer.get_full_name()} - {appointment.service.name}",
            'start': f"{appointment.appointment_date}T{appointment.appointment_time}",
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'customer': appointment.customer.get_full_name(),
                'service': appointment.service.name,
                'staff': appointment.staff.user.get_full_name(),
                'status': appointment.get_status_display_fa(),
                'price': appointment.total_price,
                'phone': appointment.customer.phone,
            }
        })
    
    return JsonResponse(events, safe=False)

@login_required
def my_appointments(request):
    """نوبت‌های من"""
    appointments = Appointment.objects.filter(
        customer=request.user
    ).select_related('salon', 'staff__user', 'service').order_by('-appointment_date', '-appointment_time')
    
    context = {'appointments': appointments}
    return render(request, 'appointments/my_appointments.html', context)

@login_required
def appointment_detail(request, appointment_id):
    """جزئیات نوبت"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # بررسی مجوز
    if not (appointment.customer == request.user or 
            appointment.salon.owner == request.user or
            (hasattr(request.user, 'staff') and request.user.staff.salon == appointment.salon)):
        messages.error(request, 'دسترسی غیر مجاز')
        return redirect('appointments:customer_dashboard')
    
    context = {'appointment': appointment}
    return render(request, 'appointments/detail.html', context)

@login_required
def appointment_reschedule(request, appointment_id):
    """تغییر زمان نوبت"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # بررسی مجوز
    if appointment.customer != request.user:
        messages.error(request, 'دسترسی غیر مجاز')
        return redirect('appointments:customer_dashboard')
    
    if not appointment.can_be_cancelled():
        messages.error(request, 'این نوبت قابل تغییر نیست')
        return redirect('appointments:customer_dashboard')
    
    if request.method == 'POST':
        new_date = request.POST.get('appointment_date')
        new_time = request.POST.get('appointment_time')
        
        try:
            appointment_date = datetime.strptime(new_date, '%Y-%m-%d').date()
            appointment_time = datetime.strptime(new_time, '%H:%M').time()
            
            # بررسی تداخل
            if Appointment.objects.filter(
                salon=appointment.salon,
                staff=appointment.staff,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=['pending', 'confirmed', 'in_progress']
            ).exclude(id=appointment.id).exists():
                messages.error(request, 'این زمان رزرو شده است')
                return render(request, 'appointments/reschedule.html', {'appointment': appointment})
            
            appointment.appointment_date = appointment_date
            appointment.appointment_time = appointment_time
            appointment.status = 'pending'  # بازگشت به حالت انتظار
            appointment.save()
            
            messages.success(request, 'زمان نوبت تغییر کرد')
            return redirect('appointments:customer_dashboard')
            
        except Exception as e:
            messages.error(request, f'خطا: {str(e)}')
    
    context = {
        'appointment': appointment,
        'staff_members': appointment.salon.staff_members.filter(is_available=True)
    }
    return render(request, 'appointments/reschedule.html', context)

def quick_book(request, salon_id):
    """رزرو سریع بدون ثبت‌نام"""
    salon = get_object_or_404(Salon, id=salon_id, is_active=True)
    services = salon.services.filter(is_active=True)
    staff_members = salon.staff_members.all().select_related('user')
    
    if request.method == 'POST':
        # اطلاعات مشتری
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        
        service_id = request.POST.get('service_id')
        staff_id = request.POST.get('staff_id')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        notes = request.POST.get('notes', '')
        
        try:
            service = get_object_or_404(Service, id=service_id, salon=salon)
            staff = get_object_or_404(Staff, id=staff_id, salon=salon)
            
            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            appointment_time = datetime.strptime(appointment_time, '%H:%M').time()
            
            # بررسی تداخل
            if Appointment.objects.filter(
                salon=salon,
                staff=staff,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=['pending', 'confirmed', 'in_progress']
            ).exists():
                messages.error(request, 'این زمان رزرو شده است')
                return render(request, 'appointments/quick_book.html', {
                    'salon': salon, 'services': services, 'staff_members': staff_members
                })
            
            # ایجاد یا پیدا کردن مشتری
            customer = None
            if customer_phone:
                try:
                    customer = User.objects.get(phone=customer_phone)
                except User.DoesNotExist:
                    # ایجاد مشتری جدید
                    username = f"guest_{customer_phone}"
                    customer = User.objects.create_user(
                        username=username,
                        phone=customer_phone,
                        first_name=customer_name,
                        role='customer'
                    )
            
            # ایجاد نوبت
            appointment = Appointment.objects.create(
                salon=salon,
                customer=customer,
                staff=staff,
                service=service,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                total_price=service.price,
                notes=f"نام: {customer_name}\nتلفن: {customer_phone}\n{notes}"
            )
            
            return redirect('appointments:booking_success', appointment_id=appointment.id)
            
        except Exception as e:
            messages.error(request, f'خطا: {str(e)}')
    
    context = {
        'salon': salon,
        'services': services,
        'staff_members': staff_members
    }
    return render(request, 'appointments/quick_book.html', context)

def booking_success(request, appointment_id):
    """صفحه موفقیت رزرو"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    context = {'appointment': appointment}
    return render(request, 'appointments/booking_success.html', context)

@login_required
def appointment_manage(request, salon_id):
    """مدیریت نوبت‌های سالن"""
    salon = get_object_or_404(Salon, id=salon_id)
    
    # بررسی مجوز
    if not (salon.owner == request.user or 
            (hasattr(request.user, 'staff') and request.user.staff.salon == salon)):
        messages.error(request, 'دسترسی غیر مجاز')
        return redirect('accounts:login')
    
    # فیلترها
    status_filter = request.GET.get('status', 'all')
    date_filter = request.GET.get('date')
    
    appointments = Appointment.objects.filter(salon=salon).select_related(
        'customer', 'staff__user', 'service'
    ).order_by('-appointment_date', '-appointment_time')
    
    if status_filter != 'all':
        appointments = appointments.filter(status=status_filter)
    
    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)
    
    context = {
        'salon': salon,
        'appointments': appointments,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'status_choices': Appointment.STATUS_CHOICES
    }
    return render(request, 'appointments/manage.html', context)

@login_required
def today_appointments(request, salon_id):
    """نوبت‌های امروز"""
    salon = get_object_or_404(Salon, id=salon_id)
    
    # بررسی مجوز
    if not (salon.owner == request.user or 
            (hasattr(request.user, 'staff') and request.user.staff.salon == salon)):
        messages.error(request, 'دسترسی غیر مجاز')
        return redirect('accounts:login')
    
    today = timezone.now().date()
    appointments = Appointment.objects.filter(
        salon=salon,
        appointment_date=today
    ).select_related('customer', 'staff__user', 'service').order_by('appointment_time')
    
    context = {
        'salon': salon,
        'appointments': appointments,
        'today': today
    }
    return render(request, 'appointments/today.html', context)