from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import viewsets, generics, permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from softdeskApp.models import Project, User, Contributor
from softdeskApp.serializers import ProjectSerializer, UserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]  # Autoriser tout le monde à se connecter

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            raise AuthenticationFailed("Le nom d'utilisateur et le mot de passe sont requis.")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise AuthenticationFailed("L'utilisateur avec ce nom d'utilisateur n'existe pas.")

        if not user.check_password(password):
            raise AuthenticationFailed("Le mot de passe est incorrect.")

        # Si les informations sont correctes, on génère un access et refresh token
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


# Vue de rafraîchissement de token
class TokenRefreshView(APIView):
    permission_classes = [permissions.AllowAny]  # Autoriser tout le monde à actualiser un token

    def post(self, request, *args, **kwargs):
        # Rafraîchissement standard via la vue de simplejwt
        return Response({'detail': 'Refresh token received successfully'})


class CreateUserView(generics.CreateAPIView):
    permission_classes = [AllowAny]  # Autorise tout le monde à créer un compte
    serializer_class = UserSerializer  # Spécifie le sérialiseur pour cette vue

    def perform_create(self, serializer):
        # L'utilisateur sera créé par le sérialiseur automatiquement
        user = serializer.save()
        return Response({"message": "Utilisateur créé avec succès", "username": user.username})


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # Seuls les utilisateurs connectés ont accès
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """ Seuls les contributeurs et l'auteur peuvent voir le projet """
        return Project.objects.filter(contributors=self.request.user) | Project.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        """ L'utilisateur qui crée un projet devient l'auteur et un contributeur """
        # Créer le projet
        project = serializer.save(author=self.request.user)

        # Créer un objet Contributor avec la relation project et l'ajouter au projet
        contributor, created = Contributor.objects.get_or_create(user=self.request.user, project=project)

        # Si le contributeur est nouvellement créé, le sauvegarder
        if created:
            contributor.save()

        # Ajouter le user (pas le Contributor) au projet
        project.contributors.add(self.request.user)  # Ajoute le user directement

        # Sauvegarder le projet avec les contributeurs
        project.save()

    def perform_destroy(self, instance):
        """ Supprimer le projet et retourner un message """
        instance.delete()
        return Response({"detail": "Project successfully deleted."})


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # Seul un utilisateur authentifié peut accéder aux utilisateurs
    queryset = User.objects.all()
    serializer_class = UserSerializer
