import logging
from django.db import IntegrityError
from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.http import JsonResponse
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
import openpyxl
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.core.exceptions import ValidationError
import json
import pytz
from datetime import *


# Настройка логера
logger = logging.getLogger(__name__)

def home(request):
    services = Service.objects.all()
    for service in services:
        service.hours = service.duration // 60
        service.minutes = service.duration % 60
    
    return render(request, 'crm/index.html', {
        'services': services,
        'specialists': Personal.objects.all()
    })
    

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return JsonResponse({'success': True})
            except ValidationError as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
            return JsonResponse({'error': 'Ошибка валидации формы', 'details': errors}, status=400)
    
    return render(request, 'crm/index.html', {
        'services': services,
        'specialists': specialists,
        'form': form
    })
    

def work_schedule_view(request, personal_id):
    return render(request, 'admin/work_schedule.html', {'personal_id': personal_id})
    
@csrf_exempt
def check_phone(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone', '').strip()

            # Проверка длины телефона
            if len(phone) < 11:
                return JsonResponse({'exists': False, 'error': 'Неверная длина номера'}, status=400)

            allowed_prefixes = ['+37544', '+37533', '+37529']
            if phone[:6] not in allowed_prefixes:
                return JsonResponse({'exists': False, 'error': 'Недопустимый префикс'}, status=400)

            # Проверяем клиента
            try:
                client = Client.objects.get(phone=phone)
                return JsonResponse({
                    'exists': True,
                    'client_id': client.id,
                    'full_name': client.full_name
                })
            except Client.DoesNotExist:
                return JsonResponse({'exists': False})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@csrf_exempt
def create_client(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        full_name = data.get('full_name')
        birth_date = data.get('birth_date')
        phone = data.get('phone')

        if not all([full_name, birth_date, phone]):
            return JsonResponse({'success': False, 'error': 'Недостаточно данных'}, status=400)

        client = Client.objects.create(
            full_name=full_name,
            birth_date=birth_date,
            phone=phone
        )

        return JsonResponse({
            'success': True,
            'client_id': client.id  # ✅ Важно: возвращаем ID клиента
        })

    return JsonResponse({'success': False, 'error': 'Метод не поддерживается'}, status=405)
        
@csrf_exempt
def book_appointment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received data:", data) 
            # Проверка обязательных полей
            required_fields = ['client_id', 'service_id', 'personal_id', 'date', 'time']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({
                        'success': False,
                        'message': f'Не заполнено поле: {field}'
                    }, status=400)
            
            # Создаем объект записи (без сохранения)
            appointment = Appointment(
                client_id=data['client_id'],
                personal_id=data['personal_id'],
                service_id=data['service_id'],
                appointment_date=data['date'],
                appointment_time=data['time']
            )
            
            # Валидация
            try:
                appointment.full_clean()
            except ValidationError as e:
                # Преобразуем ошибки валидации в читаемый формат
                error_messages = []
                for field, errors in e.message_dict.items():
                    for error in errors:
                        error_messages.append(error)
                
                return JsonResponse({
                    'success': False,
                    'message': ' | '.join(error_messages)
                }, status=400)
            
            # Сохраняем запись
            appointment.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Ошибка сервера: {str(e)}'
            }, status=500)


@csrf_exempt
def available_time_slots(request):
    try:
        specialist_id = request.GET.get('specialist_id')
        date_str = request.GET.get('date')
        service_id = request.GET.get('service_id')
        duration = int(request.GET.get('duration', 30))

        if not all([specialist_id, date_str]):
            return JsonResponse({'available_slots': []}, safe=False)

        try:
            schedule = WorkSchedule.objects.get(personal_id=specialist_id, date=date_str)
            start_time = schedule.start_time
            end_time = schedule.end_time or time(18, 0)
        except WorkSchedule.DoesNotExist:
            start_time = time(9, 0)
            end_time = time(18, 0)

        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        base_start = datetime.combine(date_obj, start_time)
        base_end = datetime.combine(date_obj, end_time)
        existing_appointments = Appointment.objects.filter(
            personal_id=specialist_id,
            appointment_date=date_str
        ).exclude(
            status='отклонено'  
        ).select_related('service')

        slots = []
        current_time = base_start

        while current_time + timedelta(minutes=duration) <= base_end:
            slot_time = current_time.strftime('%H:%M')
            is_available = True

            for appt in existing_appointments:
                appt_start = datetime.combine(
                    appt.appointment_date, 
                    appt.appointment_time
                )
                appt_end = appt_start + timedelta(minutes=appt.service.duration)

                if current_time < appt_end and current_time + timedelta(minutes=duration) > appt_start:
                    is_available = False
                    break

            slots.append({
                'time': slot_time,
                'available': is_available
            })

            current_time += timedelta(minutes=30)

        return JsonResponse({'available_slots': slots}, safe=False)

    except Exception as e:
        logger.exception(f"Ошибка получения слотов: {e}")
        return JsonResponse({'error': str(e)}, status=500)
   
@csrf_exempt
def get_available_dates(request):
    personal_id = request.GET.get('personal_id')
    if not personal_id:
        return JsonResponse({'error': 'Не указан ID специалиста'}, status=400)

    try:
        # Получаем расписание специалиста на 30 дней вперед
        today = date.today()
        available_dates = []

        for i in range(30):  # Проверяем на 30 дней вперед
            current_date = today + timedelta(days=i)
            schedule = WorkSchedule.objects.filter(
                personal_id=personal_id,
                date=current_date,
                is_day_off=False
            ).first()

            if schedule:
                available_dates.append(current_date.strftime('%Y-%m-%d'))

        return JsonResponse({'available_dates': available_dates}, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        
@csrf_exempt
def get_client(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            client_id = data.get('client_id')
            client = Client.objects.get(id=client_id)
            return JsonResponse({
                'id': client.id,
                'full_name': client.full_name,
                'phone': client.phone
            })
        except Client.DoesNotExist:
            return JsonResponse({'error': 'Клиент не найден'}, status=404)
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@csrf_exempt
def work_schedule_api(request, personal_id):
    if request.method == 'GET':
        try:
            personal = Personal.objects.get(pk=personal_id)
            events = WorkSchedule.objects.filter(personal=personal)
            formatted_events = [{
                'id': event.id,
                'title': f"{event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M') if event.end_time else 'Конец дня'}",
                'start': datetime.combine(event.date, event.start_time).isoformat() if event.start_time else None,
                'end': datetime.combine(event.date, event.end_time).isoformat() if event.end_time else None,
                'allDay': event.is_day_off
            } for event in events]

            return JsonResponse(formatted_events, safe=False)
        except Personal.DoesNotExist:
            return JsonResponse({'error': 'Персона не найдена'}, status=404)
        except Exception as e:
            logger.exception(f"Ошибка GET-запроса: {e}")
            return JsonResponse({'error': f'Ошибка сервера: {e}'}, status=500)

    elif request.method == 'POST' or request.method == 'PUT':
        try:
            data = json.loads(request.body)
            personal = Personal.objects.get(pk=personal_id)

            is_day_off = data.get('allDay', False) # Используем allDay из JSON

            if is_day_off:
                # Для выходных дней start_time и end_time устанавливаются условно
                date = datetime.fromisoformat(data['start']).date()
                start_time = datetime.min.time() # 00:00:00
                end_time = datetime.max.time() # 23:59:59
            else:
                date = datetime.fromisoformat(data['start']).date()
                start_time = datetime.fromisoformat(data['start']).time()
                end_time = datetime.fromisoformat(data['end']).time() if 'end' in data and data['end'] else None

            # Проверка времени (только для не выходных дней)
            if not is_day_off and start_time and end_time and start_time >= end_time:
                return JsonResponse({'error': 'Время окончания должно быть позже времени начала'}, status=400)

            if request.method == 'POST':
                new_event = WorkSchedule.objects.create(
                    personal=personal,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    is_day_off=is_day_off
                )
                event = new_event
            elif request.method == 'PUT':
                event_id = data['id']
                event = WorkSchedule.objects.get(id=event_id)
                event.date = date
                event.start_time = start_time
                event.end_time = end_time
                event.is_day_off = is_day_off
                event.save()

            return JsonResponse([{
                'id': event.pk,
                'title': f"{event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M') if event.end_time else ''}",
                'start': datetime.combine(event.date, event.start_time).isoformat(),
                'end': datetime.combine(event.date, event.end_time).isoformat() if event.end_time else None,
                'allDay': event.is_day_off
            }], status=201 if request.method == 'POST' else 200, safe=False)

        except (KeyError, json.JSONDecodeError, ValueError, ValidationError) as e:
            logger.exception(f"Ошибка валидации или обработки данных: {e}")
            return JsonResponse({'error': str(e)}, status=400)
        except (ObjectDoesNotExist, IntegrityError) as e:
            logger.exception(f"Ошибка базы данных: {e}")
            return JsonResponse({'error': str(e)}, status=400) 
        except Exception as e:
            logger.exception(f"Ошибка POST/PUT-запроса: {e}")
            return JsonResponse({'error': f'Ошибка сервера: {e}'}, status=500)

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            event_id = data.get('id')  

            if not event_id:
                return JsonResponse({'error': 'ID события не указан'}, status=400)

            event = WorkSchedule.objects.get(pk=event_id)
            event.delete()
            return JsonResponse({'message': 'Событие успешно удалено'}, status=204)  

        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Ошибка обработки данных'}, status=400)
        except WorkSchedule.DoesNotExist:
            return JsonResponse({'error': 'Событие не найдено'}, status=404)
        except Exception as e:
            logger.exception(f"Ошибка DELETE-запроса: {e}")
            return JsonResponse({'error': f'Ошибка сервера: {e}'}, status=500)

    else:
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)

def get_report_data(appointments):
    services = list(appointments.values_list('service__title', flat=True).distinct())
    summary = {}
    for service in services:
        service_data = appointments.filter(service__title=service).values('personal__full_name').annotate(total_services=Count('id')).order_by('personal__full_name')
        summary[service] = {item['personal__full_name']: item['total_services'] for item in service_data}
    
    earnings = appointments.values('personal__full_name').annotate(total_earnings=Sum('service__price')).order_by('personal__full_name')
    
    return {
        'summary': summary,
        'services': services,
        'earnings': earnings,
    }


def financial_report(request):
    form = ReportForm(request.GET or None)
    report_data = None

    if form.is_valid():
        year = form.cleaned_data.get('year')
        month = form.cleaned_data.get('month')

        appointments = Appointment.objects.filter(
            appointment_date__year=year,
            appointment_date__month=month,
            status='выполнено'
        )

        report_data = get_report_data(appointments)

    return render(request, 'admin/financial_report.html', {'form': form, 'report_data': report_data})

def get_service_personal(request, service_id):
     try:
         service = Service.objects.get(id=service_id)
     
         employees = list(service.personal.values('id', 'full_name'))
        

         return JsonResponse(
             employees, 
             safe=False, 
             json_dumps_params={'ensure_ascii': False}
         )
     except Service.DoesNotExist:
         return JsonResponse([], safe=False)
     except Exception as e:
         import logging
         logger = logging.getLogger(__name__)
         logger.exception(f"Error in get_service_personal: {e}") 
         return JsonResponse({'error': str(e)}, safe=False, status=500)


