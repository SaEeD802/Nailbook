// Persian Date Picker for NailBook
class PersianDatePicker {
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

    gregorianToPersian(gy, gm, gd) {
        const g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
        let jy, jm, jd, gy2, days;
        
        if (gy <= 1600) {
            jy = 0; gy -= 621;
        } else {
            jy = 979; gy -= 1600;
        }
        
        if (gm > 2) {
            gy2 = gy + 1;
        } else {
            gy2 = gy;
        }
        
        days = (365 * gy) + ((gy2 + 3) / 4) + ((gy2 + 99) / 100) - ((gy2 + 399) / 400) - 80 + gd + g_d_m[gm - 1];
        
        jy += 33 * Math.floor(days / 12053);
        days %= 12053;
        
        jy += 4 * Math.floor(days / 1461);
        days %= 1461;
        
        if (days > 365) {
            jy += Math.floor((days - 1) / 365);
            days = (days - 1) % 365;
        }
        
        if (days < 186) {
            jm = 1 + Math.floor(days / 31);
            jd = 1 + (days % 31);
        } else {
            jm = 7 + Math.floor((days - 186) / 30);
            jd = 1 + ((days - 186) % 30);
        }
        
        return { year: jy, month: jm, day: jd };
    }

    persianToGregorian(jy, jm, jd) {
        let gy, gm, gd;
        
        if (jy <= 979) {
            gy = 1600;
            jy += 621;
        } else {
            gy = 2000;
            jy -= 979;
        }
        
        let g_day_no;
        if (jm < 7) {
            g_day_no = 186 + (jm - 1) * 31 + jd - 1;
        } else {
            g_day_no = 186 + (jm - 7) * 30 + jd - 1;
        }
        
        gy += 400 * Math.floor(jy / 1029);
        jy %= 1029;
        
        let leap = true;
        if (jy >= 29) {
            jy -= 29;
            gy += 128 * Math.floor(jy / 1029);
            jy %= 1029;
            leap = false;
        }
        
        sal_a = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0];
        
        if (jy < 29) {
            gy += 33 * Math.floor(jy / 33);
            jy %= 33;
            
            if (jy >= 1) {
                gy += 4 * Math.floor((jy - 1) / 4);
                jy = (jy - 1) % 4;
                
                if (jy >= 1) {
                    gy += jy;
                }
            }
        }
        
        g_day_no += 365 * jy + Math.floor(jy / 4) - Math.floor(jy / 100) + Math.floor(jy / 400) + 1;
        
        const g_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        
        if ((gy % 4 === 0 && gy % 100 !== 0) || gy % 400 === 0) {
            g_months[1] = 29;
        }
        
        gm = 0;
        while (gm < 12 && g_day_no >= g_months[gm]) {
            g_day_no -= g_months[gm];
            gm++;
        }
        
        gd = g_day_no + 1;
        gm++;
        
        return { year: gy, month: gm, day: gd };
    }

    createDatePicker(input) {
        this.targetInput = input;
        
        // Create picker container
        const picker = document.createElement('div');
        picker.className = 'persian-datepicker';
        picker.innerHTML = this.getPickerHTML();
        
        // Position picker
        const rect = input.getBoundingClientRect();
        picker.style.position = 'absolute';
        picker.style.top = (rect.bottom + window.scrollY + 5) + 'px';
        picker.style.left = (rect.left + window.scrollX) + 'px';
        picker.style.zIndex = '9999';
        
        document.body.appendChild(picker);
        
        // Add event listeners
        this.addEventListeners(picker);
        
        // Close on outside click
        setTimeout(() => {
            document.addEventListener('click', (e) => {
                if (!picker.contains(e.target) && e.target !== input) {
                    picker.remove();
                }
            });
        }, 100);
        
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
        const daysInMonth = month <= 6 ? 31 : (month <= 11 ? 30 : (this.isLeapYear(year) ? 30 : 29));
        
        // Get first day of month
        const firstDay = this.persianToGregorian(year, month, 1);
        const firstDayOfWeek = new Date(firstDay.year, firstDay.month - 1, firstDay.day).getDay();
        const adjustedFirstDay = firstDayOfWeek === 6 ? 0 : firstDayOfWeek + 1;
        
        let html = '';
        
        // Empty cells for days before month starts
        for (let i = 0; i < adjustedFirstDay; i++) {
            html += '<div class="day empty"></div>';
        }
        
        // Days of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const isToday = this.isToday(year, month, day);
            const isSelected = this.isSelected(year, month, day);
            
            html += `<div class="day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''}" data-day="${day}">${day}</div>`;
        }
        
        return html;
    }

    isLeapYear(year) {
        const breaks = [
            -61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210,
            1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178
        ];
        
        let jp = breaks[0];
        let j = 1;
        let jump = 0;
        
        for (let j = 1; j < breaks.length; j++) {
            const jm = breaks[j];
            jump = jm - jp;
            if (year < jm) break;
            jp = jm;
        }
        
        let n = year - jp;
        
        if (n < jump) {
            if (jump - n < 6) n = n - jump + ((jump + 4) / 6) * 6;
            let leap = ((n + 1) % 33) % 4;
            if (jump === 33 && leap === 1) leap = 0;
            return leap === 1;
        } else {
            return false;
        }
    }

    isToday(year, month, day) {
        const today = this.getCurrentPersianDate();
        return year === today.year && month === today.month && day === today.day;
    }

    isSelected(year, month, day) {
        if (!this.selectedDate) return false;
        return year === this.selectedDate.year && month === this.selectedDate.month && day === this.selectedDate.day;
    }

    addEventListeners(picker) {
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
        picker.addEventListener('click', (e) => {
            if (e.target.classList.contains('day') && !e.target.classList.contains('empty')) {
                const day = parseInt(e.target.dataset.day);
                this.selectDate(this.currentDate.year, this.currentDate.month, day);
                this.updateInputValue();
                picker.remove();
            }
        });
        
        // Footer buttons
        picker.querySelector('.btn-today').addEventListener('click', () => {
            const today = this.getCurrentPersianDate();
            this.selectDate(today.year, today.month, today.day);
            this.updateInputValue();
            picker.remove();
        });
        
        picker.querySelector('.btn-clear').addEventListener('click', () => {
            this.selectedDate = null;
            this.targetInput.value = '';
            picker.remove();
        });
    }

    updatePicker(picker) {
        picker.querySelector('.current-month-year').textContent = 
            `${this.months[this.currentDate.month - 1]} ${this.currentDate.year}`;
        picker.querySelector('.persian-datepicker-days').innerHTML = this.getDaysHTML();
    }

    selectDate(year, month, day) {
        this.selectedDate = { year, month, day };
    }

    updateInputValue() {
        if (this.selectedDate && this.targetInput) {
            const gregorian = this.persianToGregorian(
                this.selectedDate.year, 
                this.selectedDate.month, 
                this.selectedDate.day
            );
            
            // Format for HTML date input (YYYY-MM-DD)
            const formattedDate = `${gregorian.year}-${gregorian.month.toString().padStart(2, '0')}-${gregorian.day.toString().padStart(2, '0')}`;
            this.targetInput.value = formattedDate;
            
            // Display Persian date in a data attribute or adjacent element
            const persianDisplay = `${this.selectedDate.year}/${this.selectedDate.month.toString().padStart(2, '0')}/${this.selectedDate.day.toString().padStart(2, '0')}`;
            this.targetInput.setAttribute('data-persian-date', persianDisplay);
            
            // Trigger change event
            this.targetInput.dispatchEvent(new Event('change'));
        }
    }
}

// Initialize Persian Date Picker
document.addEventListener('DOMContentLoaded', function() {
    const persianPicker = new PersianDatePicker();
    
    // Apply to all date inputs
    document.querySelectorAll('input[type="date"]').forEach(input => {
        // Hide default date picker
        input.style.position = 'relative';
        
        // Add Persian date display
        const display = document.createElement('div');
        display.className = 'persian-date-display';
        display.style.cssText = 'position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: white; border: 1px solid #ced4da; border-radius: 0.375rem; padding: 0.375rem 0.75rem; cursor: pointer; display: flex; align-items: center;';
        display.textContent = 'انتخاب تاریخ';
        
        input.parentNode.style.position = 'relative';
        input.style.opacity = '0';
        input.parentNode.appendChild(display);
        
        // Click handler
        display.addEventListener('click', (e) => {
            e.preventDefault();
            persianPicker.createDatePicker(input);
        });
        
        // Update display when value changes
        input.addEventListener('change', () => {
            if (input.value) {
                const persianDate = input.getAttribute('data-persian-date');
                display.textContent = persianDate || input.value;
            } else {
                display.textContent = 'انتخاب تاریخ';
            }
        });
    });
});
