window.Modal = {
    open: function() {
        document.getElementById('bookingOverlay').style.display = 'block';
        document.getElementById('bookingModal').style.display = 'block';
        this.showStep(1);
        this.resetForm();
        
        // Добавляем обработчики клавиш при открытии
        this.addKeyListeners();
    },

    close: function() {
        document.getElementById('bookingOverlay').style.display = 'none';
        document.getElementById('bookingModal').style.display = 'none';
        
        // Удаляем обработчики клавиш при закрытии
        this.removeKeyListeners();
    },

    addKeyListeners: function() {
        // Обработчик для Esc
        this.escapeHandler = (e) => {
            if (e.key === 'Escape') {
                this.close();
            }
        };
        
        // Обработчик для Enter
        this.enterHandler = (e) => {
            if (e.key === 'Enter') {
                const activeStep = document.querySelector('.modal-step.active');
                if (!activeStep) return;

                const step = activeStep.dataset.step;
                
                if (step === '1') {
                    document.getElementById('nextStep1').click();
                } else if (step === '2') {
                    document.getElementById('nextStep2').click();
                } else if (step === '3') {
                    document.getElementById('bookAppointmentBtn').click();
                }
            }
        };

        document.addEventListener('keydown', this.escapeHandler);
        document.addEventListener('keydown', this.enterHandler);
    },

    removeKeyListeners: function() {
        document.removeEventListener('keydown', this.escapeHandler);
        document.removeEventListener('keydown', this.enterHandler);
    },

    showStep: function(stepNumber) {
        document.querySelectorAll('.modal-step').forEach(step => {
            step.classList.remove('active');
        });
        const stepElement = document.querySelector(`.modal-step[data-step="${stepNumber}"]`);
        if (stepElement) {
            stepElement.classList.add('active');
        }
        if (stepNumber === 3) {
            this.initDatePicker();
        }
    },

    initDatePicker: function() {
        if (window.flatpickrInstance) {
            window.flatpickrInstance.destroy();
            window.flatpickrInstance = null;
        }

        const specialistId = document.getElementById('specialistSelect').value;

        if (!specialistId) {
            document.getElementById('timeSlots').innerHTML = '<div class="loading-slots">Выберите специалиста</div>';
            return;
        }

        API.getAvailableDates(specialistId)
            .then(data => {
                const availableDates = data.available_dates || [];
                
                const formatDateForComparison = (date) => {
                    const d = new Date(date);
                    return [
                        d.getFullYear(),
                        String(d.getMonth() + 1).padStart(2, '0'),
                        String(d.getDate()).padStart(2, '0')
                    ].join('-');
                };

                window.flatpickrInstance = flatpickr('#appointmentDate', {
                    locale: 'ru',
                    minDate: 'today',
                    dateFormat: 'Y-m-d',
                    disableMobile: true,
                    disable: [
                        function(date) {
                            const dateStr = formatDateForComparison(date);
                            return !availableDates.includes(dateStr);
                        }
                    ],
                    onDayCreate: function(dObj, dStr, fp, dayElem) {
                        dayElem.classList.remove('available-date', 'flatpickr-disabled');
                        
                        const dateStr = formatDateForComparison(dayElem.dateObj);
                        
                        if (availableDates.includes(dateStr)) {
                            dayElem.classList.add('available-date');
                        } else {
                            dayElem.classList.add('flatpickr-disabled');
                        }
                    },
                    onChange: function(selectedDates, dateStr) {
                        selectedDate = dateStr;
                        if (selectedSpecialistId && dateStr) {
                            loadAvailableTimeSlots(selectedSpecialistId, dateStr);
                        }
                    }
                });

                if (availableDates.length === 0) {
                    document.getElementById('timeSlots').innerHTML = '<div class="loading-slots">Специалист не работает в ближайшее время</div>';
                }
            })
            .catch(error => {
                console.error("Ошибка получения доступных дат:", error);
                document.getElementById('timeSlots').innerHTML = '<div class="loading-slots">Ошибка загрузки доступных дат</div>';
            });
    },

    resetForm: function() {
        document.getElementById('phone').value = '';
        document.getElementById('fullName').value = '';
        document.getElementById('birthDate').value = '';
        document.getElementById('serviceSelect').selectedIndex = 0;

        const specialistSelect = document.getElementById('specialistSelect');
        if (specialistSelect) {
            specialistSelect.innerHTML = '<option value="">-- Сначала выберите услугу --</option>';
        }

        document.getElementById('appointmentDate').value = '';
        const timeSlots = document.getElementById('timeSlots');
        if (timeSlots) {
            timeSlots.innerHTML = '<div class="loading-slots">Выберите специалиста и дату</div>';
        }

        document.getElementById('appointmentTime').value = '';
        document.getElementById('clientId').value = '';
        selectedSpecialistId = null;
        selectedDate = null;
        selectedTime = null;

        document.querySelectorAll('.error-message').forEach(el => {
            el.style.display = 'none';
        });

        if (window.flatpickrInstance) {
            window.flatpickrInstance.destroy();
            window.flatpickrInstance = null;
        }
    },

    showError: function(message, elementId = 'modalError') {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
            setTimeout(() => {
                errorElement.style.display = 'none';
            }, 5000);
        } else {
            alert(message);
        }
    }
};

// Назначаем обработчик для кнопки закрытия
document.getElementById('closeModalBtn').addEventListener('click', () => Modal.close());