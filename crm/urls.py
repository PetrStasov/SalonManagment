from django.contrib import admin
from django.urls import path
from . import views
from .views import *

admin.site.site_header = "Административная панель - ГУ Борисовский ФОЦ"
admin.site.site_title = "Админка"
admin.site.index_title = "Добро пожаловать в интерфейс администратора!"

urlpatterns = [
        path('', views.home, name='home'),
    path('api/check-phone/', views.check_phone, name='check_phone'),
    path('api/create-client/', views.create_client, name='create_client'),
    path('api/book-appointment/', views.book_appointment, name='book_appointment'),
    path('get-client/', views.get_client, name='get_client'),
    path('get-service-personal/<int:service_id>/', views.get_service_personal, name='get_service_personal'),
    path('api/available-time-slots/', views.available_time_slots, name='available_time_slots'),
    path('api/available-dates/', views.get_available_dates, name='get_available_dates'),
    path('financial_report/', financial_report, name='financial_report'),
    path('crm/api/work_schedule/<int:personal_id>/', views.work_schedule_api, name='work_schedule_api'),
    path('work_schedule/<int:personal_id>/', views.work_schedule_view, name='work_schedule'), 
    path('admin', admin.site.urls),
]