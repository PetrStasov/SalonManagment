document.addEventListener('DOMContentLoaded', function () {
    // Инициализация частиц
    initParticles();

    // Открытие модального окна
    const openBookingBtn = document.getElementById('openBookingBtn');
    if (openBookingBtn) {
        openBookingBtn.addEventListener('click', Modal.open.bind(Modal));
    }

    // Шаг 1: Далее
    const nextStep1Btn = document.getElementById('nextStep1');
    if (nextStep1Btn) {
        nextStep1Btn.addEventListener('click', function () {
            const phoneInput = document.getElementById('phone');
            const phoneValue = phoneInput.value.trim();
            const phoneRegex = /^\+375\d{9}$/;

            if (!phoneRegex.test(phoneValue)) {
                document.getElementById('phoneError').textContent = 'Введите номер в формате +375XXXXXXXXX';
                document.getElementById('phoneError').style.display = 'block';
                return;
            }

            document.getElementById('phoneError').style.display = 'none';

            API.checkPhone(phoneValue)
                .then(data => {
                    if (data.exists) {
                        document.getElementById('clientId').value = data.client_id;
                        // Сохраняем данные клиента
                        sessionStorage.setItem('currentClient', JSON.stringify({
                            id: data.client_id,
                            phone: phoneValue,
                            name: data.full_name || ''
                        }));
                        Modal.showStep(3);
                    } else {
                        Modal.showStep(2);
                    }
                })
                .catch(error => {
                    document.getElementById('phoneError').textContent = 'Ошибка проверки номера';
                    document.getElementById('phoneError').style.display = 'block';
                });
        });
    }

    // Шаг 2: Назад
    const prevStep2Btn = document.getElementById('prevStep2');
    if (prevStep2Btn) {
        prevStep2Btn.addEventListener('click', function () {
            Modal.showStep(1);
        });
    }

    // Шаг 2: Далее
    const nextStep2Btn = document.getElementById('nextStep2');
    if (nextStep2Btn) {
        nextStep2Btn.addEventListener('click', function () {
            const fullName = document.getElementById('fullName').value.trim();
            const phone = document.getElementById('phone').value.trim();
            const birthDate = document.getElementById('birthDate').value;

            if (!fullName || fullName.split(' ').length < 2) {
                document.getElementById('nameError').textContent = 'Введите ФИО полностью';
                document.getElementById('nameError').style.display = 'block';
                return;
            }

            document.getElementById('nameError').style.display = 'none';

            API.createClient(fullName, phone, birthDate)
                .then(data => {
                    if (data.client_id) {
                        document.getElementById('clientId').value = data.client_id;
                        // Сохраняем данные клиента
                        sessionStorage.setItem('currentClient', JSON.stringify({
                            id: data.client_id,
                            phone: phone,
                            name: fullName
                        }));
                        Modal.showStep(3);
                    } else {
                        throw new Error(data.message || "Ошибка сохранения клиента");
                    }
                })
                .catch(error => {
                    document.getElementById('nameError').textContent = error.message;
                    document.getElementById('nameError').style.display = 'block';
                });
        });
    }

    // Шаг 3: Назад
    const prevStep3Btn = document.getElementById('prevStep3');
    if (prevStep3Btn) {
        prevStep3Btn.addEventListener('click', function () {
            Modal.showStep(2);
        });
    }

    // Шаг 3: Записаться
    const bookAppointmentBtn = document.getElementById('bookAppointmentBtn');
    if (bookAppointmentBtn) {
        bookAppointmentBtn.addEventListener('click', function () {
            const clientId = document.getElementById('clientId').value;
            const serviceId = document.getElementById('serviceSelect').value;
            const specialistId = document.getElementById('specialistSelect').value;
            const date = document.getElementById('appointmentDate').value;
            const time = document.getElementById('appointmentTime').value;

            // Проверка всех обязательных полей
            if (!clientId) {
                Modal.showError("Необходимо заполнить данные клиента", "timeError");
                Modal.showStep(1);
                return;
            }
            
            if (!serviceId || !specialistId || !date || !time) {
                Modal.showError("Заполните все поля", "timeError");
                return;
            }

            const originalText = bookAppointmentBtn.textContent;
            bookAppointmentBtn.disabled = true;
            bookAppointmentBtn.textContent = 'Запись...';

            API.bookAppointment(clientId, serviceId, specialistId, date, time)
                .then(data => {
                    if (data.success) {
                        alert("✅ Запись успешно создана!");
                        Modal.close();
                    } else {
                        Modal.showError(data.message || "Ошибка при записи", "timeError");
                    }
                })
                .catch(error => {
                    console.error("Ошибка:", error);
                    Modal.showError("Произошла ошибка при записи. Попробуйте позже.", "timeError");
                })
                .finally(() => {
                    bookAppointmentBtn.disabled = false;
                    bookAppointmentBtn.textContent = originalText;
                });
        });
    }

    // При изменении услуги
    const serviceSelect = document.getElementById('serviceSelect');
    if (serviceSelect) {
        serviceSelect.addEventListener('change', function () {
            const serviceId = this.value;
            const specialistSelect = document.getElementById('specialistSelect');

            if (!serviceId) {
                specialistSelect.innerHTML = '<option value="">-- Сначала выберите услугу --</option>';
                return;
            }

            specialistSelect.innerHTML = '<option value="">Загрузка специалистов...</option>';

            API.getSpecialists(serviceId)
                .then(data => {
                    specialistSelect.innerHTML = '<option value="">-- Выберите специалиста --</option>';
                    data.forEach(specialist => {
                        const option = document.createElement('option');
                        option.value = specialist.id;
                        option.textContent = specialist.full_name;
                        specialistSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    specialistSelect.innerHTML = '<option value="">Ошибка загрузки</option>';
                });
        });
    }

    // При изменении специалиста
    const specialistSelect = document.getElementById('specialistSelect');
    if (specialistSelect) {
        specialistSelect.addEventListener('change', function () {
            selectedSpecialistId = this.value;

            if (window.flatpickrInstance) {
                window.flatpickrInstance.clear();
            }

            const timeSlots = document.getElementById('timeSlots');
            if (timeSlots) {
                timeSlots.innerHTML = '<div class="loading-slots">Выберите дату</div>';
            }

            document.getElementById('appointmentTime').value = '';
            selectedDate = null;
            selectedTime = null;

            Modal.initDatePicker();
        });
    }

    // Восстановление данных клиента при загрузке
    const savedClient = sessionStorage.getItem('currentClient');
    if (savedClient) {
        const client = JSON.parse(savedClient);
        document.getElementById('clientId').value = client.id;
        document.getElementById('phone').value = client.phone;
        if (client.name) {
            document.getElementById('fullName').value = client.name;
        }
    }
});