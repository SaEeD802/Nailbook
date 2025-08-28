#!/usr/bin/env python3
"""
اسکریپت برای رفع خطاهای syntax در templates
"""

import os
import re

# مسیر templates
TEMPLATES_DIR = r'd:\Django Project\NailBook\nailbook\templates'

def fix_template_file(file_path):
    """رفع خطاهای syntax در یک فایل template"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # رفع مشکل {{ {{ ... }}|filter }}
        content = re.sub(r'\{\{\s*\{\{\s*([^}]+)\s*\}\}\s*\|\s*([^}]+)\s*\}\}', r'{{ \1|\2 }}', content)
        
        # رفع مشکل دیگر فیلترهای تکراری
        content = re.sub(r'\|\s*persian_date\s*\|\s*persian_date', r'|persian_date', content)
        content = re.sub(r'\|\s*persian_time\s*\|\s*persian_time', r'|persian_time', content)
        content = re.sub(r'\|\s*persian_datetime\s*\|\s*persian_datetime', r'|persian_datetime', content)
        content = re.sub(r'\|\s*format_price\s*\|\s*format_price', r'|format_price', content)
        
        # ذخیره فایل اگر تغییر کرده
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        
        return False
    
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """اجرای اصلی"""
    fixed_files = []
    
    # پیمایش تمام فایل‌های HTML
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                if fix_template_file(file_path):
                    fixed_files.append(file_path)
    
    print(f"\nTotal files fixed: {len(fixed_files)}")
    for file_path in fixed_files:
        print(f"  - {os.path.relpath(file_path, TEMPLATES_DIR)}")

if __name__ == '__main__':
    main()
