#!/usr/bin/env python3
"""
اسکریپت برای بروزرسانی تمام templates با فیلترهای تاریخ شمسی
"""

import os
import re

# مسیر templates
TEMPLATES_DIR = r'd:\Django Project\NailBook\nailbook\templates'

# فیلترهای تاریخ میلادی که باید تبدیل شوند
DATE_REPLACEMENTS = [
    # تاریخ کامل
    (r'(\{\{\s*\w+\.[\w_]+\|date:"Y/m/d"\s*\}\})', r'{{ \1|persian_date }}'),
    (r'(\{\{\s*\w+\.[\w_]+\|date:"Y-m-d"\s*\}\})', r'{{ \1|persian_date:"%Y-%m-%d" }}'),
    
    # تاریخ و زمان
    (r'(\{\{\s*\w+\.[\w_]+\|date:"Y/m/d H:i"\s*\}\})', r'{{ \1|persian_datetime }}'),
    
    # زمان
    (r'(\{\{\s*\w+\.[\w_]+\|time:"H:i"\s*\}\})', r'{{ \1|persian_time }}'),
    
    # فرمت‌های مختلف تاریخ
    (r'\|date:"Y/m/d"', r'|persian_date'),
    (r'\|date:"Y-m-d"', r'|persian_date:"%Y-%m-%d"'),
    (r'\|date:"Y/m/d H:i"', r'|persian_datetime'),
    (r'\|time:"H:i"', r'|persian_time'),
    
    # قیمت‌ها
    (r'\|floatformat:0', r'|format_price'),
]

def update_template_file(file_path):
    """بروزرسانی یک فایل template"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # اضافه کردن load persian_filters اگر وجود ندارد
        if '{% load persian_filters %}' not in content and ('|date:' in content or '|time:' in content or '|floatformat:' in content):
            if '{% extends' in content:
                # اضافه کردن بعد از extends
                content = re.sub(r'({% extends [^%]+%})', r'\1\n{% load persian_filters %}', content)
            else:
                # اضافه کردن در ابتدای فایل
                content = '{% load persian_filters %}\n' + content
        
        # اعمال تغییرات تاریخ
        for pattern, replacement in DATE_REPLACEMENTS:
            content = re.sub(pattern, replacement, content)
        
        # ذخیره فایل اگر تغییر کرده
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        
        return False
    
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """اجرای اصلی"""
    updated_files = []
    
    # پیمایش تمام فایل‌های HTML
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                if update_template_file(file_path):
                    updated_files.append(file_path)
    
    print(f"\nTotal files updated: {len(updated_files)}")
    for file_path in updated_files:
        print(f"  - {os.path.relpath(file_path, TEMPLATES_DIR)}")

if __name__ == '__main__':
    main()
