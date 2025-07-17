import datetime
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError 
from django.core.validators import RegexValidator
from django.db.models import Q

    


# Клиенты
class Client(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="ФИО")
    birth_date = models.DateField(verbose_name="Дата рождения")
    phone = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+375(29|33|44|25)\d{7}$',  # Разрешаем только коды 29, 33, 44, 25
                message="Телефон должен быть формата +375(29|33|44|25)XXXXXXX"
            )
        ]
    )

    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)
        
          
    def __str__(self):
        return f'{self.full_name}\n{self.birth_date}\n{self.phone}'

    class Meta:
        verbose_name = "клиента"
        verbose_name_plural = "Клиенты"

# Сотрудники
class Personal(models.Model):
    # ФИО сотрудника
    full_name = models.CharField(max_length=200, verbose_name="ФИО")
     # Должность
    post = models.CharField(max_length=200, verbose_name="Должность")
    # Дата приема на работу
    date_of_employment = models.DateField(verbose_name="Дата приема")
    # Статус
    status = models.CharField(max_length=20, 
                              choices=[('работает', 'Работает'), ('уволен', 'Уволен')], 
                              default='работает',
                              verbose_name="Статус")  
    def __str__(self):
        return f'{self.full_name}\n{self.post}\n{self.date_of_employment}'

    class Meta:
        verbose_name = "сотрудника"
        verbose_name_plural = "Сотрудники"

# Услуги
class Service(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название")  # Название услуги
    duration = models.IntegerField(verbose_name="Продолжительность (в минутах)")           # Время выполнения
    price = models.PositiveIntegerField(verbose_name="Цена")  # Цена
    personal = models.ManyToManyField(Personal, verbose_name="Сотрудники")  # Сотрудники, оказывающие услугу
    is_active = models.BooleanField(default=True, verbose_name="Активная")# Статус активности

    def __str__(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        return f'{self.title}\n{hours} ч {minutes} мин\n{self.price}'

    class Meta:
        verbose_name = "услугу"
        verbose_name_plural = "Услуги"


# Запись к сотруднику
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('в ожидании', 'В ожидании'),
        ('выполнено', 'Выполнено')
    ]
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="Клиент")
    personal = models.ForeignKey(Personal, on_delete=models.PROTECT, verbose_name="Сотрудник", null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Услуга")  
    appointment_date = models.DateField(verbose_name="Дата записи")
    appointment_time = models.TimeField(verbose_name="Время записи")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES, 
        default='в ожидании', 
        verbose_name="Статус записи"
    )

    def __str__(self):
        return f'Запись: {self.client.full_name} к {self.personal.full_name} на {self.appointment_date} {self.appointment_time}'
    
    # Валидация перед сохранением
    def clean(self):
        if not self.is_time_available():
            raise ValidationError("Время уже занято. Пожалуйста, выберите другое время.")
        
        personal_availability_error = self.is_personal_available()
        if personal_availability_error:
            raise ValidationError(personal_availability_error)

    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)
     
    def is_time_available(self):
        if self.service is None:
            raise ValidationError("Услуга не выбрана. Пожалуйста, выберите услугу.")
        appointment_start = datetime.combine(self.appointment_date, self.appointment_time)
        appointment_end = appointment_start + timedelta(minutes=self.service.duration)

        # Проверяем, есть ли другие записи в это время  
        conflicting_appointments = Appointment.objects.filter(
            personal=self.personal,
            appointment_date=self.appointment_date
        ).exclude(pk=self.pk)


        for existing_appointment in conflicting_appointments:
            existing_start = datetime.combine(existing_appointment.appointment_date, existing_appointment.appointment_time)
            existing_end = existing_start + timedelta(minutes=existing_appointment.service.duration)

            # Проверяем пересечение времени
            if (appointment_start < existing_end and appointment_end > existing_start):
                return False

        return True

    def is_personal_available(self):
        # Проверяем, есть ли расписание для сотрудника на выбранную дату
        try:
            schedule = WorkSchedule.objects.get(personal=self.personal, date=self.appointment_date)
            if schedule.is_day_off:
                raise ValidationError("У сотрудника выходной в этот день.")  # Сотрудник в выходной
            # Проверяем, попадает ли время записи в рабочие часы
            if not (schedule.start_time <= self.appointment_time <= schedule.end_time):
                raise ValidationError("Сотрудник не работает в это время.")  # Время записи вне рабочего времени
        except WorkSchedule.DoesNotExist:
            raise ValidationError("Расписание не найдено, значит, сотрудник не работает.")  # Расписание не найдено

        return None  # Сотрудник доступен

    class Meta:
        verbose_name = "запись"
        verbose_name_plural = "Записи"
        constraints = [
            models.UniqueConstraint(fields=['personal', 'appointment_date', 'appointment_time'], name='unique_appointment')
        ]

# Расписание работы сотрудника
class WorkSchedule(models.Model):
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, verbose_name="Сотрудник")
    date = models.DateField(verbose_name="Дата", null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True, verbose_name="Время начала работы")
    end_time = models.TimeField(null=True, blank=True, verbose_name="Время окончания работы")
    is_day_off = models.BooleanField(default=False, verbose_name="Выходной")

    def __str__(self):
        return f"{self.personal.full_name} - {self.date}"

    def clean(self):
        # Проверка, что время начала не больше времени окончания
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("Время окончания должно быть позже времени начала.")

    def save(self, *args, **kwargs):
        self.clean()  # Выполнить проверку при сохранении
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "график работы"
        verbose_name_plural = "Графики работы"
        unique_together = (('personal', 'date'),)  # Уникальная пара (сотрудник, дата)


class ServiceReport(Appointment):  
    class Meta:
        proxy = True
        verbose_name = 'Отчет по услугам'
        verbose_name_plural = 'Отчеты по услугам'



