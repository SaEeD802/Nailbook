// Simple Persian Date Converter and Picker
class SimplePersianDate {
    constructor() {
        this.persianMonths = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ];
        this.persianWeekdays = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه'];
    }

    // Convert Gregorian to Persian
    gregorianToPersian(gy, gm, gd) {
        const g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
        let jy, jm, jd, gy2, days;
        
        if (gy <= 1600) {
            jy = 0;
            gy -= 621;
        } else {
            jy = 979;
            gy -= 1600;
        }
        
        gy2 = (gm > 2) ? (gy + 1) : gy;
        days = (365 * gy) + (Math.floor((gy2 + 3) / 4)) + (Math.floor((gy2 + 99) / 100)) - (Math.floor((gy2 + 399) / 400)) - 80 + gd + g_d_m[gm - 1];
        
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

    // Convert Persian to Gregorian
    persianToGregorian(jy, jm, jd) {
        let gy, gm, gd, g_day_no, sal_a, v;
        
        if (jy <= 979) {
            gy = 1600;
            jy += 621;
        } else {
            gy = 2000;
            jy -= 979;
        }
        
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
            gy += 128 * Math.floor(jy / 128);
            jy %= 128;
            
            leap = (jy >= 29) ? false : true;
            if (jy >= 29) {
                jy -= 29;
                gy += 4 * Math.floor(jy / 4);
                jy %= 4;
                leap = (jy >= 1) ? false : true;
            }
        }
        
        sal_a = leap ? 366 : 365;
        
        if (g_day_no >= sal_a) {
            g_day_no -= sal_a;
            gy++;
        }
        
        const sal_a2 = ((gy % 4 === 0 && gy % 100 !== 0) || (gy % 400 === 0)) ? 366 : 365;
        const g_d_m = sal_a2 === 366 ? [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335] : [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
        
        for (gm = 0; gm < 12; gm++) {
            v = (gm === 11) ? sal_a2 : g_d_m[gm + 1];
            if (g_day_no < v) break;
        }
        
        gd = g_day_no - g_d_m[gm] + 1;
        gm++;
        
        return { year: gy, month: gm, day: gd };
    }

    // Format Persian date
    formatPersianDate(py, pm, pd) {
        return `${py}/${pm.toString().padStart(2, '0')}/${pd.toString().padStart(2, '0')}`;
    }

    // Format Gregorian date
    formatGregorianDate(gy, gm, gd) {
        return `${gy}-${gm.toString().padStart(2, '0')}-${gd.toString().padStart(2, '0')}`;
    }

    // Get today's Persian date
    getTodayPersian() {
        const today = new Date();
        return this.gregorianToPersian(today.getFullYear(), today.getMonth() + 1, today.getDate());
    }

    // Create simple date picker
    createSimplePicker(input) {
        const today = this.getTodayPersian();
        const currentYear = today.year;
        const currentMonth = today.month;
        
        // Create picker HTML
        const pickerHTML = `
            <div class="simple-persian-picker" style="position: absolute; z-index: 1000; background: white; border: 1px solid #ccc; border-radius: 5px; padding: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 10px;">
                    <select id="year-select" style="margin-left: 5px;">
                        ${Array.from({length: 10}, (_, i) => {
                            const year = currentYear + i - 2;
                            return `<option value="${year}" ${year === currentYear ? 'selected' : ''}>${year}</option>`;
                        }).join('')}
                    </select>
                    <select id="month-select">
                        ${this.persianMonths.map((month, index) => 
                            `<option value="${index + 1}" ${(index + 1) === currentMonth ? 'selected' : ''}>${month}</option>`
                        ).join('')}
                    </select>
                </div>
                <div id="days-grid" style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; text-align: center;">
                    <!-- Days will be populated here -->
                </div>
                <div style="text-align: center; margin-top: 10px;">
                    <button type="button" id="today-btn" style="margin-left: 5px; padding: 5px 10px;">امروز</button>
                    <button type="button" id="close-btn" style="padding: 5px 10px;">بستن</button>
                </div>
            </div>
        `;
        
        // Remove existing picker
        const existingPicker = document.querySelector('.simple-persian-picker');
        if (existingPicker) {
            existingPicker.remove();
        }
        
        // Add picker to DOM
        const pickerDiv = document.createElement('div');
        pickerDiv.innerHTML = pickerHTML;
        const picker = pickerDiv.firstElementChild;
        
        // Position picker
        const rect = input.getBoundingClientRect();
        picker.style.top = (rect.bottom + window.scrollY) + 'px';
        picker.style.left = rect.left + 'px';
        
        document.body.appendChild(picker);
        
        // Populate days
        this.populateDays(picker, currentYear, currentMonth);
        
        // Event listeners
        picker.querySelector('#year-select').addEventListener('change', (e) => {
            const year = parseInt(e.target.value);
            const month = parseInt(picker.querySelector('#month-select').value);
            this.populateDays(picker, year, month);
        });
        
        picker.querySelector('#month-select').addEventListener('change', (e) => {
            const year = parseInt(picker.querySelector('#year-select').value);
            const month = parseInt(e.target.value);
            this.populateDays(picker, year, month);
        });
        
        picker.querySelector('#today-btn').addEventListener('click', () => {
            const todayPersian = this.getTodayPersian();
            this.selectDate(input, todayPersian.year, todayPersian.month, todayPersian.day);
            picker.remove();
        });
        
        picker.querySelector('#close-btn').addEventListener('click', () => {
            picker.remove();
        });
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!picker.contains(e.target) && e.target !== input) {
                picker.remove();
            }
        });
    }
    
    populateDays(picker, year, month) {
        const daysGrid = picker.querySelector('#days-grid');
        const daysInMonth = (month <= 6) ? 31 : (month <= 11) ? 30 : (this.isLeapYear(year) ? 30 : 29);
        
        // Clear existing days
        daysGrid.innerHTML = '';
        
        // Add day numbers
        for (let day = 1; day <= daysInMonth; day++) {
            const dayBtn = document.createElement('button');
            dayBtn.type = 'button';
            dayBtn.textContent = day;
            dayBtn.style.cssText = 'padding: 5px; border: 1px solid #ddd; background: white; cursor: pointer;';
            
            dayBtn.addEventListener('click', () => {
                const input = document.querySelector('input[readonly][placeholder*="شمسی"]');
                this.selectDate(input, year, month, day);
                picker.remove();
            });
            
            daysGrid.appendChild(dayBtn);
        }
    }
    
    selectDate(input, year, month, day) {
        // Display Persian date
        const persianDate = this.formatPersianDate(year, month, day);
        input.value = persianDate;
        
        // Convert to Gregorian and store in hidden input
        const gregorian = this.persianToGregorian(year, month, day);
        const gregorianDate = this.formatGregorianDate(gregorian.year, gregorian.month, gregorian.day);
        
        const hiddenInput = document.getElementById('appointment_date_gregorian');
        if (hiddenInput) {
            hiddenInput.value = gregorianDate;
        }
        
        console.log('Persian date selected:', persianDate);
        console.log('Gregorian date for backend:', gregorianDate);
        
        // Trigger change event
        input.dispatchEvent(new Event('change'));
    }
    
    isLeapYear(year) {
        return ((year + 2346) % 2820) % 128 <= 29;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const persianDate = new SimplePersianDate();
    
    // Setup Persian date picker for readonly date inputs
    setTimeout(() => {
        const dateInputs = document.querySelectorAll('input[readonly][placeholder*="شمسی"]');
        dateInputs.forEach(input => {
            input.addEventListener('click', () => {
                persianDate.createSimplePicker(input);
            });
        });
    }, 500);
});
