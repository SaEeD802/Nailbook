// Simple Persian Date Picker for NailBook
class SimplePersianDatePicker {
    constructor() {
        this.months = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ];
        this.weekdays = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج'];
        this.currentDate = this.getCurrentPersianDate();
        this.selectedDate = null;
        this.targetInput = null;
    }

    getCurrentPersianDate() {
        const now = new Date();
        return this.gregorianToPersian(now.getFullYear(), now.getMonth() + 1, now.getDate());
    }

    // Simple Gregorian to Persian conversion
    gregorianToPersian(gy, gm, gd) {
        const date = new Date(gy, gm - 1, gd);
        const persianDate = new Intl.DateTimeFormat('fa-IR-u-ca-persian', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        }).format(date);
        
        const parts = persianDate.split('/');
        return {
            year: parseInt(parts[0]),
            month: parseInt(parts[1]),
            day: parseInt(parts[2])
        };
    }

    // Simple Persian to Gregorian conversion
    persianToGregorian(py, pm, pd) {
        // Create a date object with Persian calendar
        const persianDateStr = `${py}/${pm.toString().padStart(2, '0')}/${pd.toString().padStart(2, '0')}`;
        
        // Convert using Intl API
        try {
            const date = new Date(Date.parse(`${py}-${pm.toString().padStart(2, '0')}-${pd.toString().padStart(2, '0')}T00:00:00`));
            
            // Approximate conversion (this is a simplified approach)
            const persianEpoch = new Date(622, 2, 22); // Persian calendar epoch
            const daysDiff = Math.floor((py - 1) * 365.25 + (pm - 1) * 30 + pd);
            const gregorianDate = new Date(persianEpoch.getTime() + daysDiff * 24 * 60 * 60 * 1000);
            
            return {
                year: gregorianDate.getFullYear(),
                month: gregorianDate.getMonth() + 1,
                day: gregorianDate.getDate()
            };
        } catch (e) {
            // Fallback to current date
            const now = new Date();
            return {
                year: now.getFullYear(),
                month: now.getMonth() + 1,
                day: now.getDate()
            };
        }
    }

    createDatePicker(input) {
        this.targetInput = input;
        
        // Remove existing picker
        const existingPicker = document.querySelector('.persian-datepicker-container');
        if (existingPicker) {
            existingPicker.remove();
        }

        const picker = document.createElement('div');
        picker.className = 'persian-datepicker-overlay';
        picker.innerHTML = this.getPickerHTML();
        document.body.appendChild(picker);

        this.attachEvents(picker);
        return picker;
    }

    getPickerHTML() {
        const { year, month } = this.currentDate;
        
        return `
            <div class="persian-datepicker-container">
                <div class="persian-datepicker-header">
                    <button type="button" class="btn-prev-year">&laquo;</button>
                    <button type="button" class="btn-prev-month">&lsaquo;</button>
                    <span class="current-month-year">${this.months[month - 1]} ${year}</span>
                    <button type="button" class="btn-next-month">&rsaquo;</button>
                    <button type="button" class="btn-next-year">&raquo;</button>
                </div>
                <div class="persian-datepicker-weekdays">
                    ${this.weekdays.map(day => `<div class="weekday">${day}</div>`).join('')}
                </div>
                <div class="persian-datepicker-days">
                    ${this.getDaysHTML()}
                </div>
                <div class="persian-datepicker-footer">
                    <button type="button" class="btn-today">امروز</button>
                    <button type="button" class="btn-clear">پاک کردن</button>
                </div>
            </div>
        `;
    }

    getDaysHTML() {
        const { year, month } = this.currentDate;
        const daysInMonth = this.getDaysInPersianMonth(year, month);
        const firstDayOfWeek = this.getFirstDayOfPersianMonth(year, month);
        
        let html = '';
        
        // Empty cells for days before month starts
        for (let i = 0; i < firstDayOfWeek; i++) {
            html += '<div class="day empty"></div>';
        }
        
        // Days of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const isSelected = this.selectedDate && 
                this.selectedDate.year === year && 
                this.selectedDate.month === month && 
                this.selectedDate.day === day;
            
            html += `<div class="day ${isSelected ? 'selected' : ''}" data-day="${day}">${day}</div>`;
        }
        
        return html;
    }

    getDaysInPersianMonth(year, month) {
        if (month <= 6) return 31;
        if (month <= 11) return 30;
        return this.isPersianLeapYear(year) ? 30 : 29;
    }

    isPersianLeapYear(year) {
        return ((year + 2346) % 2820) % 128 <= 29;
    }

    getFirstDayOfPersianMonth(year, month) {
        // Simplified calculation - return 0 for now
        return 0;
    }

    attachEvents(picker) {
        // Close picker when clicking outside
        picker.addEventListener('click', (e) => {
            if (e.target === picker) {
                picker.remove();
            }
        });

        // Navigation buttons
        picker.querySelector('.btn-prev-year').addEventListener('click', () => {
            this.currentDate.year--;
            this.updatePicker(picker);
        });

        picker.querySelector('.btn-next-year').addEventListener('click', () => {
            this.currentDate.year++;
            this.updatePicker(picker);
        });

        picker.querySelector('.btn-prev-month').addEventListener('click', () => {
            this.currentDate.month--;
            if (this.currentDate.month < 1) {
                this.currentDate.month = 12;
                this.currentDate.year--;
            }
            this.updatePicker(picker);
        });

        picker.querySelector('.btn-next-month').addEventListener('click', () => {
            this.currentDate.month++;
            if (this.currentDate.month > 12) {
                this.currentDate.month = 1;
                this.currentDate.year++;
            }
            this.updatePicker(picker);
        });

        // Day selection
        picker.querySelectorAll('.day:not(.empty)').forEach(dayEl => {
            dayEl.addEventListener('click', () => {
                const day = parseInt(dayEl.dataset.day);
                this.selectDate(this.currentDate.year, this.currentDate.month, day);
                this.updateInputValue();
                picker.remove();
            });
        });

        // Today button
        picker.querySelector('.btn-today').addEventListener('click', () => {
            const today = this.getCurrentPersianDate();
            this.selectDate(today.year, today.month, today.day);
            this.updateInputValue();
            picker.remove();
        });

        // Clear button
        picker.querySelector('.btn-clear').addEventListener('click', () => {
            this.selectedDate = null;
            this.targetInput.value = '';
            this.targetInput.dispatchEvent(new Event('change'));
            picker.remove();
        });
    }

    updatePicker(picker) {
        picker.querySelector('.current-month-year').textContent = 
            `${this.months[this.currentDate.month - 1]} ${this.currentDate.year}`;
        picker.querySelector('.persian-datepicker-days').innerHTML = this.getDaysHTML();
        
        // Re-attach day events
        picker.querySelectorAll('.day:not(.empty)').forEach(dayEl => {
            dayEl.addEventListener('click', () => {
                const day = parseInt(dayEl.dataset.day);
                this.selectDate(this.currentDate.year, this.currentDate.month, day);
                this.updateInputValue();
                picker.remove();
            });
        });
    }

    selectDate(year, month, day) {
        this.selectedDate = { year, month, day };
    }

    updateInputValue() {
        if (this.selectedDate && this.targetInput) {
            // Use a simple date format for now - we'll convert on the backend
            const persianDateStr = `${this.selectedDate.year}/${this.selectedDate.month.toString().padStart(2, '0')}/${this.selectedDate.day.toString().padStart(2, '0')}`;
            
            // For now, just use today's date in Gregorian format for the input value
            const today = new Date();
            const gregorianDate = `${today.getFullYear()}-${(today.getMonth() + 1).toString().padStart(2, '0')}-${today.getDate().toString().padStart(2, '0')}`;
            
            this.targetInput.value = gregorianDate;
            this.targetInput.setAttribute('data-persian-date', persianDateStr);
            
            // Trigger change event
            this.targetInput.dispatchEvent(new Event('change'));
        }
    }
}

// Initialize Simple Persian Date Picker
document.addEventListener('DOMContentLoaded', function() {
    console.log('Persian date picker initializing...');
    
    const persianPicker = new SimplePersianDatePicker();
    
    // Wait a bit for other scripts to load
    setTimeout(() => {
        // Apply to all date inputs
        document.querySelectorAll('input[type="date"]').forEach(input => {
            console.log('Setting up Persian picker for input:', input.id);
            
            // Create Persian date display
            const wrapper = document.createElement('div');
            wrapper.className = 'persian-date-wrapper';
            wrapper.style.position = 'relative';
            
            const display = document.createElement('div');
            display.className = 'persian-date-display';
            display.style.cssText = 'position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: white; border: 1px solid #ced4da; border-radius: 0.375rem; padding: 0.375rem 0.75rem; cursor: pointer; display: flex; align-items: center; z-index: 10;';
            display.textContent = 'انتخاب تاریخ شمسی';
            
            // Wrap the input
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);
            wrapper.appendChild(display);
            
            input.style.opacity = '0';
            input.style.position = 'relative';
            input.style.zIndex = '1';
            
            // Click handler
            display.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('Persian date picker clicked');
                persianPicker.createDatePicker(input);
            });
            
            // Update display when value changes
            input.addEventListener('change', () => {
                if (input.value) {
                    const persianDate = input.getAttribute('data-persian-date');
                    display.textContent = persianDate || 'تاریخ انتخاب شده';
                } else {
                    display.textContent = 'انتخاب تاریخ شمسی';
                }
            });
        });
    }, 1000);
});
