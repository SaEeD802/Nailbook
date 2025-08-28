from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Service
from salons.models import Salon

@login_required
def service_list(request, salon_id):
    """لیست خدمات سالن"""
    salon = get_object_or_404(Salon, id=salon_id)
    
    # اگر مسئول سالن است یا کارمند همان سالن
    if not (request.user == salon.owner or 
            (hasattr(request.user, 'staff') and request.user.staff.salon == salon)):
        messages.error(request, 'دسترسی غیر مجاز')
        return redirect('accounts:login')
    
    services = salon.services.filter(is_active=True).order_by('name')
    
    context = {
        'salon': salon,
        'services': services
    }
    return render(request, 'services/list.html', context)

@login_required
def service_create(request, salon_id):
    """ایجاد خدمت جدید"""
    salon = get_object_or_404(Salon, id=salon_id, owner=request.user)
    
    if request.method == 'POST':
        service = Service.objects.create(
            salon=salon,
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            price=int(request.POST.get('price')),
            duration=int(request.POST.get('duration'))
        )
        messages.success(request, f'خدمت {service.name} اضافه شد')
        return redirect('services:list', salon_id=salon.id)
    
    return render(request, 'services/create.html', {'salon': salon})

def public_services(request, salon_id):
    """لیست عمومی خدمات برای مشتریان"""
    salon = get_object_or_404(Salon, id=salon_id, is_active=True)
    services = salon.services.filter(is_active=True).order_by('name')
    
    context = {
        'salon': salon,
        'services': services
    }
    return render(request, 'services/public_list.html', context)

@login_required
def service_edit(request, service_id):
    """ویرایش خدمت"""
    service = get_object_or_404(Service, id=service_id)
    
    # بررسی مجوز
    if service.salon.owner != request.user:
        messages.error(request, 'دسترسی غیر مجاز')
        return redirect('salons:dashboard')
    
    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.description = request.POST.get('description', '')
        service.price = int(request.POST.get('price'))
        service.duration = int(request.POST.get('duration'))
        service.save()
        
        messages.success(request, f'خدمت {service.name} بروزرسانی شد')
        return redirect('services:list', salon_id=service.salon.id)
    
    context = {'service': service}
    return render(request, 'services/edit.html', context)

@login_required
def service_delete(request, service_id):
    """حذف خدمت"""
    service = get_object_or_404(Service, id=service_id)
    
    # بررسی مجوز
    if service.salon.owner != request.user:
        messages.error(request, 'دسترسی غیر مجاز')
        return redirect('salons:dashboard')
    
    if request.method == 'POST':
        salon_id = service.salon.id
        service_name = service.name
        service.delete()
        
        messages.success(request, f'خدمت {service_name} حذف شد')
        return redirect('services:list', salon_id=salon_id)
    
    context = {'service': service}
    return render(request, 'services/delete_confirm.html', context)

def service_detail(request, service_id):
    """جزئیات خدمت"""
    service = get_object_or_404(Service, id=service_id, is_active=True)
    
    context = {
        'service': service,
        'salon': service.salon
    }
    return render(request, 'services/detail.html', context)