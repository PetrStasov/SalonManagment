document.addEventListener('DOMContentLoaded', function() {
    const serviceSelect = document.getElementById('id_service');
    const personalSelect = document.getElementById('id_personal');

    serviceSelect.addEventListener('change', function() {
        const serviceId = this.value;
        
        // ������� ������ �����������
        personalSelect.innerHTML = '<option value="">---------</option>';

        if (serviceId) {
            // AJAX-������ ��� ��������� ������ �����������
            fetch(`/get-service-personal/${serviceId}/`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(employee => {
                        const option = document.createElement('option');
                        option.value = employee.id;
                        option.textContent = employee.name;
                        personalSelect.appendChild(option);
                    });
                });
        }
    });
});