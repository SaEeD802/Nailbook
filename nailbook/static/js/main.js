// Main JavaScript for NailBook
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete, .btn-danger[href*="delete"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('آیا مطمئن هستید که می‌خواهید این مورد را حذف کنید؟')) {
                e.preventDefault();
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Phone number formatting
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0 && !value.startsWith('09')) {
                if (value.startsWith('9')) {
                    value = '0' + value;
                }
            }
            if (value.length > 11) {
                value = value.substring(0, 11);
            }
            e.target.value = value;
        });
    });

    // Price formatting
    const priceInputs = document.querySelectorAll('input[name="price"]');
    priceInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/[^\d]/g, '');
            e.target.value = value;
        });
    });

    // Date validation (prevent past dates)
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        const today = new Date().toISOString().split('T')[0];
        if (!input.hasAttribute('min')) {
            input.setAttribute('min', today);
        }
    });
});

// Utility functions
function formatPrice(price) {
    return new Intl.NumberFormat('fa-IR').format(price) + ' تومان';
}

function showLoading(element) {
    const originalText = element.innerHTML;
    element.innerHTML = '<span class="loading"></span> در حال پردازش...';
    element.disabled = true;
    return originalText;
}

function hideLoading(element, originalText) {
    element.innerHTML = originalText;
    element.disabled = false;
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

// AJAX helper functions
function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    };
    
    return fetch(url, { ...defaultOptions, ...options })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Status update function for appointments
function updateAppointmentStatus(appointmentId, status) {
    const button = event.target;
    const originalText = showLoading(button);
    
    makeRequest(`/appointments/update-status/${appointmentId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCsrfToken()
        },
        body: `status=${status}`
    })
    .then(data => {
        if (data.success) {
            showToast('وضعیت با موفقیت بروزرسانی شد', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            throw new Error(data.error || 'خطا در بروزرسانی');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('خطا در بروزرسانی وضعیت', 'danger');
        hideLoading(button, originalText);
    });
}

// Load available times for appointment booking
function loadAvailableTimes(salonId, staffId, date, targetSelect) {
    if (!staffId || !date) {
        targetSelect.innerHTML = '<option value="">ابتدا تاریخ و کارمند را انتخاب کنید</option>';
        targetSelect.disabled = true;
        return;
    }
    
    targetSelect.innerHTML = '<option value="">در حال بارگذاری...</option>';
    targetSelect.disabled = true;
    
    makeRequest(`/appointments/available-times/${salonId}/?staff_id=${staffId}&date=${date}`)
        .then(data => {
            targetSelect.innerHTML = '<option value="">ساعت مورد نظر را انتخاب کنید</option>';
            
            if (data.available_times && data.available_times.length > 0) {
                data.available_times.forEach(time => {
                    const option = document.createElement('option');
                    option.value = time;
                    option.textContent = time;
                    targetSelect.appendChild(option);
                });
                targetSelect.disabled = false;
            } else {
                targetSelect.innerHTML = '<option value="">ساعت خالی موجود نیست</option>';
            }
        })
        .catch(error => {
            console.error('Error loading times:', error);
            targetSelect.innerHTML = '<option value="">خطا در بارگذاری ساعات</option>';
            showToast('خطا در بارگذاری ساعات خالی', 'danger');
        });
}

// Search functionality
function initializeSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.form.submit();
            }, 500);
        });
    }
}

// Initialize search on page load
document.addEventListener('DOMContentLoaded', initializeSearch);
