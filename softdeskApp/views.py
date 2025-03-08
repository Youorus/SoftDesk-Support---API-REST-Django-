from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from softdeskApp.models import Project, User
from softdeskApp.serializers import ProjectSerializer, UserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Récupérer les informations d'identification envoyées
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            raise AuthenticationFailed("Le nom d'utilisateur et le mot de passe sont requis.")

        try:
            # Chercher l'utilisateur par son nom d'utilisateur
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Si l'utilisateur n'existe pas, retourne un message spécifique
            raise AuthenticationFailed("L'utilisateur avec ce nom d'utilisateur n'existe pas")

        # Vérifier si le mot de passe est correct
        if not user.check_password(password):
            # Si le mot de passe est incorrect
            raise AuthenticationFailed("Le mot de passe est incorrect")

        # Si tout est correct, on génère les tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Retourner les tokens
        return Response({
            'access': access_token,
            'refresh': str(refresh),
        })

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

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer