# SoftDeskSupport/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/', include('softdeskApp.urls')),  # Assure-toi d'inclure 'softdeskApp.urls'
]
