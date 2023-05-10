
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admindashboard/', admin.site.urls),
    path('', include('application_01.urls')),
]
