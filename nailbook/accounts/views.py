from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import User
import json

def register_view(request):
    """ثبت نام کاربران"""
    if request.method == 'POST':
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role', 'customer')
        
        # بررسی وجود کاربر
        if User.objects.filter(username=username).exists():
            messages.error(request, 'این نام کاربری قبلاً استفاده شده است')
            return render(request, 'accounts/register.html')
        
        if phone and User.objects.filter(phone=phone).exists():
            messages.error(request, 'این شماره تلفن قبلاً ثبت شده است')
            return render(request, 'accounts/register.html')
        
        # ایجاد کاربر جدید
        user = User.objects.create_user(
            username=username,
            password=password,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        login(request, user)
        messages.success(request, f'خوش آمدید {user.get_full_name()}!')
        
        # هدایت بر اساس نقش
        if role == 'salon_owner':
            return redirect('salons:dashboard')
        else:
            return redirect('appointments:customer_dashboard')
    
    return render(request, 'accounts/register.html')

def login_view(request):
    """ورود کاربران"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            
            # هدایت بر اساس نقش
            if user.role == 'salon_owner':
                return redirect('salons:dashboard')
            elif user.role == 'staff':
                return redirect('salons:staff_dashboard')
            else:
                return redirect('appointments:customer_dashboard')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است')
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    """خروج کاربر"""
    logout(request)
    messages.success(request, 'با موفقیت خارج شدید')
    return redirect('accounts:login')

@login_required
def profile_view(request):
    """پروفایل کاربر"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.phone = request.POST.get('phone', '')
        user.save()
        messages.success(request, 'پروفایل با موفقیت بروزرسانی شد')
    
    return render(request, 'accounts/profile.html')

