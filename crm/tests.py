from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Client, Personal, Service, Appointment, WorkSchedule
from datetime import date, time, timedelta

class ValidationTest(TestCase):
    def setUp(self):
        self.valid_phone = '+375441234567'
        self.client_data = {
            'full_name': 'Тестовый клиент',
            'birth_date': date(2000, 1, 1),
            'phone': self.valid_phone
        }
        
        # Создаем сотрудника с обязательными полями
        self.personal = Personal.objects.create(
            full_name='Тестовый сотрудник',
            post='Мастер',
            date_of_employment=date.today(),
            status='работает'
        )
        
        # Создаем услугу согласно вашей модели
        self.service = Service.objects.create(
            title='Тестовая услуга',
            duration=30,  # в минутах
            price=5000,   # в копейках или рублях (уточните формат)
            is_active=True
        )
        self.service.personal.add(self.personal)
        
        # Создаем рабочий график
        WorkSchedule.objects.create(
            personal=self.personal,
            date=date.today(),
            start_time=time(9, 0),
            end_time=time(18, 0),
            is_day_off=False
        )

    def test_phone_validation_invalid_numbers(self):
        """Тестирование невалидных номеров телефонов"""
        invalid_phones = [
            '37544123456',     # Слишком короткий
            '+375551234567',   # Неправильный префикс (55)
            '+3754412345678',  # Слишком длинный
            '+37544123abc',    # Содержит буквы
            '+37544 123456',   # Содержит пробел
            '+37544-123456',   # Содержит дефис
            '+380441234567',   # Украинский код
            '80291234567',     # Локальный формат
            '+375991234567',   # Неправильный код (99)
        ]
        
        for phone in invalid_phones:
            with self.subTest(phone=phone):
                client = Client(
                    full_name="Тестовый клиент",
                    birth_date=date(2000, 1, 1),
                    phone=phone
                )
                with self.assertRaises(ValidationError):
                    client.full_clean()
                    client.save()
                    
    def test_phone_validation_valid_numbers(self):
        """Тестирование валидных номеров телефонов"""
        valid_phones = [
            '+375291234567',  # velcom
            '+375331234567',  # МТС
            '+375441234567',  # A1
            '+375251234567',  # life:)
        ]
        
        for phone in valid_phones:
            with self.subTest(phone=phone):
                try:
                    client = Client(
                        full_name="Тестовый клиент",
                        birth_date=date(2000, 1, 1),
                        phone=phone
                    )
                    client.full_clean()
                    client.save()
                except ValidationError:
                    self.fail(f"Валидный номер {phone} вызвал ошибку валидации")

class ViewsTest(TestCase):
    def setUp(self):
        self.client_data = {
            'full_name': 'Тестовый клиент',
            'birth_date': '2000-01-01',
            'phone': '+375441234567'
        }
        
        # Создаем сотрудника
        self.personal = Personal.objects.create(
            full_name='Тестовый сотрудник',
            post='Мастер',
            date_of_employment=date.today(),
            status='работает'
        )
        
        # Создаем услугу
        self.service = Service.objects.create(
            title='Тестовая услуга',
            duration=30,
            price=5000,
            is_active=True
        )
        self.service.personal.add(self.personal)
        
        # Создаем рабочий график
        WorkSchedule.objects.create(
            personal=self.personal,
            date=date(2023, 1, 10),  # Конкретная дата для тестов
            start_time=time(9, 0),
            end_time=time(18, 0),
            is_day_off=False
        )

    def test_check_phone_exists(self):
        """Тест проверки существующего телефона"""
        Client.objects.create(**{
            'full_name': 'Тестовый клиент',
            'birth_date': date(2000, 1, 1),
            'phone': '+375441234567'
        })
        response = self.client.post(
            '/api/check-phone/',
            {'phone': '+375441234567'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['exists'])

    def test_create_client(self):
        """Тест создания клиента"""
        response = self.client.post(
            '/api/create-client/',
            self.client_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Client.objects.count(), 1)

    def test_book_appointment(self):
        """Тест записи на прием"""
        client = Client.objects.create(**{
            'full_name': 'Тестовый клиент',
            'birth_date': date(2000, 1, 1),
            'phone': '+375441234567'
        })
        data = {
            'client_id': client.id,
            'service_id': self.service.id,
            'personal_id': self.personal.id,
            'date': '2023-01-10',
            'time': '10:00'
        }
        response = self.client.post(
            '/api/book-appointment/',
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Appointment.objects.count(), 1)