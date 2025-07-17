from django.contrib import admin
from django.urls import path, include
from crm import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('/crm', include('crm.urls')),
    

 
 
]