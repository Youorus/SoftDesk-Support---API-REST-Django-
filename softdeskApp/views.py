from django.shortcuts import render
from rest_framework import viewsets

from softdeskApp.models import Project
from softdeskApp.serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def list(self, request, *args, **kwargs):
        # Test en imprimant les données reçues
        print("Request to list projects received!")

        # Appeler la méthode par défaut pour obtenir la liste des objets
        response = super().list(request, *args, **kwargs)

        # Afficher la réponse dans la console
        print("Response data:", response.data)

        return response