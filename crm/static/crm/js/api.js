function getCSRFToken() {
    const cookieValue = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
    return cookieValue ? cookieValue.pop() : '';
}

const API = {
    checkPhone: function(phone) {
        return fetch('/api/check-phone/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ phone: phone })
        }).then(response => response.json());
    },
    
    createClient: function(fullName, phone, birthDate) {
        return fetch('/api/create-client/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                full_name: fullName,
                phone: phone,
                birth_date: birthDate
            })
        }).then(response => response.json());
    },
    
    getSpecialists: function(serviceId) {
        return fetch(`/get-service-personal/${serviceId}/`)
            .then(response => response.json());
    },
    
    getAvailableTimeSlots: function(specialistId, date, serviceId, serviceDuration) {
        return fetch(`/api/available-time-slots/?specialist_id=${specialistId}&date=${date}&service_id=${serviceId}&duration=${serviceDuration}`)
            .then(response => response.json());
    },
	getAvailableDates: function(personalId) {
        return fetch(`/api/available-dates/?personal_id=${personalId}`)
            .then(response => response.json())
            .catch(error => {
                console.error("Ошибка загрузки доступных дат:", error);
                return { available_dates: [] };
            });
    },
    
    bookAppointment: function(clientId, serviceId, specialistId, date, time) {
        return fetch('/api/book-appointment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                client_id: clientId,
                service_id: serviceId,
                personal_id: specialistId,
                date: date,
                time: time
            })
        }).then(response => response.json());
    }
};