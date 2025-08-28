from django import template
from django.utils import timezone
import jdatetime
from datetime import datetime, date, time

register = template.Library()

@register.filter
def persian_date(value, format_string="%Y/%m/%d"):
    """تبدیل تاریخ میلادی به شمسی"""
    if not value:
        return ""
    
    if isinstance(value, str):
        return value
    
    if isinstance(value, datetime):
        j_date = jdatetime.datetime.fromgregorian(datetime=value)
    elif isinstance(value, date):
        j_date = jdatetime.date.fromgregorian(date=value)
    else:
        return value
    
    return j_date.strftime(format_string)

@register.filter
def persian_datetime(value, format_string="%Y/%m/%d - %H:%M"):
    """تبدیل تاریخ و زمان میلادی به شمسی"""
    if not value:
        return ""
    
    if isinstance(value, str):
        return value
    
    if isinstance(value, datetime):
        j_datetime = jdatetime.datetime.fromgregorian(datetime=value)
        return j_datetime.strftime(format_string)
    
    return value

@register.filter
def persian_time(value, format_string="%H:%M"):
    """فرمت زمان"""
    if not value:
        return ""
    
    if isinstance(value, str):
        return value
    
    if isinstance(value, (datetime, time)):
        if isinstance(value, datetime):
            return value.strftime(format_string)
        else:
            return value.strftime(format_string)
    
    return value

@register.filter
def persian_weekday(value):
    """نام روز هفته به فارسی"""
    if not value:
        return ""
    
    weekdays = {
        0: 'دوشنبه',
        1: 'سه‌شنبه', 
        2: 'چهارشنبه',
        3: 'پنج‌شنبه',
        4: 'جمعه',
        5: 'شنبه',
        6: 'یکشنبه'
    }
    
    if isinstance(value, datetime):
        j_date = jdatetime.datetime.fromgregorian(datetime=value)
        return weekdays.get(j_date.weekday(), '')
    elif isinstance(value, date):
        j_date = jdatetime.date.fromgregorian(date=value)
        return weekdays.get(j_date.weekday(), '')
    
    return value

@register.filter
def persian_month_name(value):
    """نام ماه شمسی"""
    if not value:
        return ""
    
    months = {
        1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد',
        4: 'تیر', 5: 'مرداد', 6: 'شهریور',
        7: 'مهر', 8: 'آبان', 9: 'آذر',
        10: 'دی', 11: 'بهمن', 12: 'اسفند'
    }
    
    if isinstance(value, (datetime, date)):
        if isinstance(value, datetime):
            j_date = jdatetime.datetime.fromgregorian(datetime=value)
        else:
            j_date = jdatetime.date.fromgregorian(date=value)
        return months.get(j_date.month, '')
    
    return value

@register.filter
def time_until(value):
    """زمان باقی‌مانده تا تاریخ مشخص"""
    if not value:
        return ""
    
    if isinstance(value, datetime):
        now = timezone.now()
        diff = value - now
        
        if diff.days > 0:
            return f"{diff.days} روز"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} ساعت"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} دقیقه"
        else:
            return "کمتر از یک دقیقه"
    
    return value

@register.filter
def format_price(value):
    """فرمت قیمت با جداکننده هزارگان"""
    if not value:
        return "0"
    
    try:
        price = int(float(value))
        return f"{price:,}".replace(',', '،')
    except (ValueError, TypeError):
        return value
