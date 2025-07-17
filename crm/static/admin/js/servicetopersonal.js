document.addEventListener('DOMContentLoaded', function () {
    const serviceSelect = document.getElementById('id_service');
    const personalSelect = document.getElementById('id_personal');

    window.updatePersonalList = function (serviceId) {
        if (!serviceId) {
            personalSelect.innerHTML = '<option value="">Выберите услугу</option>';
            return;
        }

        const url = `/get-service-personal/${serviceId}/`;

        fetch(url)
            .then(response => {
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('Ошибка: Ответ не является JSON');
                }
                return response.json();
            })
            .then(data => {
                const selectedPersonal = personalSelect.value;
                personalSelect.innerHTML = '<option value="">Выберите мастера</option>';

                if (data.length === 0) {
                    personalSelect.innerHTML += '<option value="">Нет доступных мастеров</option>';
                    return;
                }

                data.forEach(person => {
                    const option = document.createElement('option');
                    option.value = person.id;
                    option.textContent = person.full_name;
                    personalSelect.appendChild(option);
                });

                personalSelect.value = selectedPersonal;
            })
            .catch(error => {
                console.error('Ошибка загрузки мастеров:', error);
                personalSelect.innerHTML = '<option value="">Ошибка загрузки</option>';
            });
    };

    if (serviceSelect) {
        serviceSelect.addEventListener('change', function () {
            if (this.value) window.updatePersonalList(this.value);
        });

        if (serviceSelect.value) window.updatePersonalList(serviceSelect.value);
    }
});