let flatpickrInstance = null;
let selectedSpecialistId = null;
let selectedDate = null;
let selectedTime = null;

function initDatePicker(specialistId) {
    const dateInput = document.getElementById('appointmentDate');
    if (!dateInput) return;

    // Если уже есть экземпляр — удаляем его
    if (flatpickrInstance) {
        flatpickrInstance.destroy();
    }

    if (!specialistId) {
        // Специалист не выбран — запрещаем все даты
        flatpickrInstance = flatpickr(dateInput, {
            locale: 'ru',
            minDate: 'today',
            dateFormat: 'Y-m-d',
            disable: [date => true],
            onChange: function() {
                document.getElementById('timeSlots').innerHTML = '<div class="loading-slots">Выберите специалиста</div>';
            }
        });
        return;
    }

    // Загружаем доступные даты специалиста
    fetch(`/api/available-dates/?personal_id=${specialistId}`)
        .then(response => response.json())
        .then(data => {
            const availableDates = data.available_dates || [];

            // Форматируем даты для flatpickr
            const disabledDates = [
    date => {
        const localDate = new Date(dateStr);
        const correctedDate = new Date(localDate.getTime() - localDate.getTimezoneOffset() * 60000);
        const dateStr = correctedDate.toISOString().split('T')[0];
        return !availableDates.includes(dateStr);
    }
];

            // Создаём календарь с фильтром
            flatpickrInstance = flatpickr(dateInput, {
                locale: 'ru',
                minDate: 'today',
                dateFormat: 'Y-m-d',
                disable: disabledDates,
                onDayCreate: function (_, __, ___, dateElem) {
                    const dateStr = dateElem.dateObj.toISOString().split('T')[0];
                    if (availableDates.includes(dateStr)) {
                        dateElem.className += ' available-date';
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
            console.error("Ошибка загрузки доступных дат:", error);
            flatpickrInstance = flatpickr(dateInput, {
                locale: 'ru',
                minDate: 'today',
                dateFormat: 'Y-m-d',
                disable: [date => true],
                onChange: function() {
                    document.getElementById('timeSlots').innerHTML = '<div class="loading-slots">Ошибка загрузки доступных дат</div>';
                }
            });
        });
}
function loadAvailableTimeSlots(specialistId, dateStr) {
    const serviceSelect = document.getElementById('serviceSelect');
    const serviceId = serviceSelect.value;
    const serviceDuration = parseInt(serviceSelect.options[serviceSelect.selectedIndex]?.dataset.duration || 30);

    const timeSlotsContainer = document.getElementById('timeSlots');
    timeSlotsContainer.innerHTML = '<div class="loading-slots">Загрузка доступного времени...</div>';

    fetch(`/api/available-time-slots/?specialist_id=${specialistId}&date=${dateStr}&service_id=${serviceId}&duration=${serviceDuration}`)
        .then(response => response.json())
        .then(data => {
            timeSlotsContainer.innerHTML = '';
            
            if (!data.available_slots || data.available_slots.length === 0) {
                timeSlotsContainer.innerHTML = '<div class="loading-slots">Нет доступных слотов</div>';
                return;
            }

            const slotGrid = document.createElement('div');
            slotGrid.className = 'slot-grid';

            data.available_slots.forEach(slot => {
                const slotElement = document.createElement('div');
                slotElement.className = `time-slot ${slot.available ? 'available' : 'booked'}`;
                slotElement.textContent = slot.time;
                slotElement.dataset.time = slot.time;

                if (slot.available) {
                    slotElement.addEventListener('click', function () {
                        // Снимаем выделение с других слотов
                        document.querySelectorAll('.time-slot').forEach(el => el.classList.remove('selected'));
                        this.classList.add('selected');
                        document.getElementById('appointmentTime').value = this.dataset.time;
                        selectedTime = this.dataset.time;
                    });
                } else {
                    slotElement.title = 'Время занято другой записью';
                }

                slotGrid.appendChild(slotElement);
            });

            timeSlotsContainer.appendChild(slotGrid);
        })
        .catch(error => {
            console.error("Ошибка загрузки слотов:", error);
            timeSlotsContainer.innerHTML = '<div class="loading-slots">Ошибка загрузки доступного времени</div>';
        });
}