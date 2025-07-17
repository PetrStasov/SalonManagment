document.addEventListener('DOMContentLoaded', function() {
    const adminButton = document.getElementById('admin-button'); 
    adminButton.addEventListener('click', function() { 
        window.location.href = '/crm/personal/';
    });

    const personalIdElement = document.getElementById('personal-id');
    if (!personalIdElement) {
        console.error("Элемент с ID 'personal-id' не найден!");
        return;
    }
    const personalId = personalIdElement.value;

    const url = `/crm/api/work_schedule/${personalId}/`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Ошибка сети: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(events => {
            // Преобразование времени событий в локальное время
            events = events.map(event => {
                event.start = moment.utc(event.start).local().format();
                event.end = event.end ? moment.utc(event.end).local().format() : null;
                return event;
            });

            var calendarEl = document.getElementById('calendar');
            var calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'dayGridMonth',
                editable: true,
                events: events,
                timeZone: 'UTC',
                eventContent: function(arg) {
                    let title = arg.event.title;
                    if (arg.event.allDay) {
                        title = 'Выходной';
                    }
                    return {
                        html: `<div class="event-item" data-id="${arg.event.id}">${title}</div>`
                    };
                },
                dateClick: function(info) {
                    Swal.fire({
                        title: 'Добавить событие',
                        html: `
                            <label for="start_time">Время начала:</label>
                            <input type="time" id="start_time" value="09:00"><br>
                            <label for="end_time">Время окончания:</label>
                            <input type="time" id="end_time" value="21:00"><br>
                            <label for="is_day_off">Выходной:</label>
                            <input type="checkbox" id="is_day_off">
                        `,
                        focusConfirm: false,
                        preConfirm: () => {
                            const startTime = document.getElementById('start_time').value;
                            const endTime = document.getElementById('end_time').value;
                            const isDayOff = document.getElementById('is_day_off').checked;

                            if (!isDayOff && (!startTime || !endTime)) {
                                Swal.showValidationMessage('Пожалуйста, заполните все поля!');
                                return false;
                            }

                            return { startTime, endTime, isDayOff };
                        },
                        confirmButtonText: 'Сохранить',
                    }).then((result) => {
                        if (result.isConfirmed) {
                            const { startTime, endTime, isDayOff } = result.value;
                            const eventData = {
                                title: isDayOff ? 'Выходной' : `${startTime} - ${endTime}`,
                                start: isDayOff ? moment(info.dateStr).local().format() : moment(info.dateStr + 'T' + startTime).local().format(),
                                end: isDayOff ? null : moment(info.dateStr + 'T' + endTime).local().format(),
                                personal_id: personalId,
                                allDay: isDayOff
                            };

                            fetch(url, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': getCookie('csrftoken')
                                },
                                body: JSON.stringify(eventData)
                            })
                            .then(response => {
                                if (!response.ok) {
                                    if (response.status === 400) {
                                        return response.json().then(errorData => {
                                            Swal.fire({
                                                icon: 'error',
                                                title: 'Ошибка',
                                                text: errorData.error || 'Ошибка при создании события. Проверьте данные.'
                                            });
                                            throw new Error(`Плохой запрос: ${JSON.stringify(errorData)}`);
                                        });
                                    } else {
                                        return Promise.reject(new Error(`Ошибка HTTP! Статус: ${response.status} ${response.statusText}`));
                                    }
                                }
                                return response.json();
                            })
                            .then(data => {
                                if (data && data[0]) {
                                    calendar.addEvent({
                                        id: data[0].id,
                                        title: data[0].allDay ? 'Выходной' : data[0].title,
                                        start: moment.utc(data[0].start).local().format(),
                                        end: data[0].end ? moment.utc(data[0].end).local().format() : null,
                                        allDay: data[0].allDay
                                    });
                                    Swal.fire({
                                        icon: 'success',
                                        title: 'Успех!',
                                        text: 'Событие успешно создано.'
                                    });
                                } else {
                                    console.error('Unexpected response data:', data);
                                    Swal.fire({
                                        icon: 'error',
                                        title: 'Ошибка',
                                        text: 'Не удалось создать событие. Некорректный ответ от сервера.'
                                    });
                                }
                            })
                            .catch(error => {
                                console.error('Ошибка:', error);
                                Swal.fire({
                                    icon: 'error',
                                    title: 'Ошибка',
                                    text: 'Не удалось создать событие. Проверьте данные и логи сервера.'
                                });
                            });
                        }
                    });
                },
                eventDrop: function(info) {
                    updateEvent(info.event);
                },
                eventResize: function(info) {
                    updateEvent(info.event);
                }
            });

           
            calendarEl.addEventListener('mousedown', function(ev) {
                if (ev.button === 2) { // Правая кнопка мыши
                    const eventElement = ev.target.closest('.fc-event, .event-item');
                    if (eventElement) {
                        const eventId = eventElement.getAttribute('data-id');
                        const event = calendar.getEventById(eventId);
                        if (event) {
                            document.oncontextmenu = function (){return false};// Отключение контекстного меню
                            ev.stopPropagation();
                            Swal.fire({
                                 title: 'Вы уверены?',
                                 text: 'Это действие необратимо!',
                                 icon: 'warning',
                                 showCancelButton: true,
                                 confirmButtonColor: '#3085d6',
                                 cancelButtonColor: '#d33',
                                 confirmButtonText: 'Да, удалить!',
                                 cancelButtonText: 'Отмена'
                            }).then((result) => {
                                 if (result.isConfirmed) {
                                     deleteEvent(event); // Вызов функции удаления
                                 }
                            });
                         }
                      }
                   }
               });


            calendar.render(); 

        })
        .catch(error => {
            console.error('Ошибка при загрузке событий:', error);
            Swal.fire({
                icon: 'error',
                title: 'Ошибка',
                text: 'Не удалось загрузить события. Проверьте подключение к серверу.'
            });
        });

    function updateEvent(event) {
        const eventData = {
            id: event.id,
            title: event.allDay ? 'Выходной' : event.title,
            start: moment(event.start).utc().format(),
            end: event.end ? moment(event.end).utc().format() : null,
            personal_id: personalId,
            allDay: event.allDay
        };

        fetch(url, {
            method: 'PUT',  
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(eventData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    Swal.fire({
                        icon: 'error',
                        title: 'Ошибка',
                        text: errorData.error || 'Ошибка при обновлении события. Проверьте данные.'
                    });
                    throw new Error(`Плохой запрос: ${JSON.stringify(errorData)}`);
                });
            }
            return response.json();
        })
        .then(data => {
            Swal.fire({
                icon: 'success',
                title: 'Успех!',
                text: 'Событие успешно обновлено.'
            });
        })
        .catch(error => {
            console.error('Ошибка:', error);
            Swal.fire({
                icon: 'error',
                title: 'Ошибка',
                text: 'Не удалось обновить событие. Проверьте данные и логи сервера.'
            });
        });
    }

    function deleteEvent(event) {
        const eventData = {
            id: event.id
        };

        fetch(url, {
            method: 'DELETE',  // Используем метод DELETE для удаления события
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(eventData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    Swal.fire({
                        icon: 'error',
                        title: 'Ошибка',
                        text: errorData.error || 'Ошибка при удалении события. Проверьте данные.'
                    });
                    throw new Error(`Плохой запрос: ${JSON.stringify(errorData)}`);
                });
            }
            event.remove(); // Удаление события из календаря
            Swal.fire({
                icon: 'success',
                title: 'Успех!',
                text: 'Событие успешно удалено.'
            });
        })
        .catch(error => {
            console.error('Ошибка:', error);
            Swal.fire({
                icon: 'error',
                title: 'Ошибка',
                text: 'Не удалось удалить событие. Проверьте данные и логи сервера.'
            });
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});