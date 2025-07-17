from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import *
from django.forms import DateInput, TimeInput
from django.core.exceptions import ValidationError



class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].label = "ФИО"
        self.fields['birth_date'].label = "Дата рождения"
class PersonalForm(forms.ModelForm):
    class Meta:
        model = Personal
        fields = '__all__'
        widgets = {
            'date_of_employment': DateInput(attrs={'type': 'date', 'format':'yyyy-MM-dd'})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk: # Проверка на существование записи

            # Установка начального значения даты
            if self.instance.date_of_employment:
                self.initial['date_of_employment'] = self.instance.date_of_employment.strftime('%Y-%m-%d')

            # Установка начального значения времени
            self.fields['date_of_employment'].initial = self.instance.date_of_employment

class AppointmentForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        label='Услуга',
        empty_label='Выберите услугу',
        widget=forms.Select(attrs={'onchange': 'updatePersonalList(this.value)'}) # Добавлено
    )
    personal = forms.ModelChoiceField(
        queryset=Personal.objects.none(),
        label='Сотрудник',
        required=True,
        widget=forms.Select(attrs={'id': 'id_personal'}) # Добавлено id
    )

    class Meta:
        model = Appointment
        fields = ['client', 'service', 'personal', 'appointment_date', 'appointment_time']
        widgets = {
            'appointment_date': DateInput(attrs={'type': 'date', 'format':'yyyy-MM-dd'}),
            'appointment_time': TimeInput(attrs={'type': 'time'}),
            'service': forms.Select(attrs={'id': 'id_service', 'onchange': 'updatePersonalList(this.value)'}),
            'personal': forms.Select(attrs={'id': 'id_personal'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk: # Проверка на существование записи
            if self.instance.service:
                self.fields['personal'].queryset = self.instance.service.personal.all()
                self.fields['personal'].initial = self.instance.personal # Установка начального значения сотрудника

            # Установка начального значения даты
            if self.instance.appointment_date:
                self.initial['appointment_date'] = self.instance.appointment_date.strftime('%Y-%m-%d')

            # Установка начального значения времени
            self.fields['appointment_time'].initial = self.instance.appointment_time

        if 'service' in self.data:
            try:
                service = Service.objects.get(pk=self.data['service'])
                self.fields['personal'].queryset = service.personal.all()
            except (ValueError, Service.DoesNotExist):
                self.fields['personal'].queryset = Personal.objects.none()
                self.add_error('service', 'Услуга не найдена.')

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        personal = cleaned_data.get('personal')

        if not service:
            raise forms.ValidationError("Необходимо выбрать услугу.")
        if not personal:
            raise forms.ValidationError("Необходимо выбрать сотрудника.")
        if personal not in service.personal.all():
            raise forms.ValidationError("Выбранный сотрудник не оказывает эту услугу.")
        
        return cleaned_data



class ReportForm(forms.Form):
    year = forms.ChoiceField(
        choices=[(year, year) for year in range(2020, 2031)],
        label="Год",
        required=True  # Сделаем поле обязательным
    )
    month = forms.ChoiceField(
        choices=[
            (1, "Январь"), (2, "Февраль"), (3, "Март"), (4, "Апрель"),
            (5, "Май"), (6, "Июнь"), (7, "Июль"), (8, "Август"),
            (9, "Сентябрь"), (10, "Октябрь"), (11, "Ноябрь"), (12, "Декабрь")
        ],
        label="Месяц",
        required=True  # Сделаем поле обязательным
    )

class DateRangeForm(forms.Form):
    start_date = forms.DateField(label=_("Дата начала"), widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label=_("Дата окончания"), widget=forms.DateInput(attrs={'type': 'date'}))

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if not start_date or not end_date:
            raise forms.ValidationError(_("Пожалуйста, выберите обе даты."))
        if end_date < start_date:
            raise forms.ValidationError(_("Дата окончания не может быть раньше даты начала."))

        return cleaned_data
