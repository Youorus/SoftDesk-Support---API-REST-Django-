
from rest_framework import viewsets, generics, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from softdeskApp.models import Project, User, Contributor, Issue
from softdeskApp.serializers import ProjectSerializer, UserSerializer, ContributorSerializer, IssueSerializer


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
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Récupère l'ID du projet à partir de l'URL (project_pk est le paramètre dans l'URL)
        project_id = self.kwargs.get('project_pk')  # Assure-toi que l'URL utilise ce paramètre
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                context['project'] = project  # Ajoute le projet au contexte
            except Project.DoesNotExist:
                raise ValidationError("Le projet spécifié n'existe pas.")
        return context

    def create(self, request, *args, **kwargs):
        project = self.get_serializer_context().get('project')
        user = request.data.get('user')

        # Vérifier si cet utilisateur est déjà un contributeur du projet
        if Contributor.objects.filter(user=user, project=project).exists():
            return Response(
                {"detail": "Cet utilisateur est déjà un contributeur pour ce projet."}
            )

        # Si ce n'est pas le cas, procéder à la création du contributeur
        return super().create(request, *args, **kwargs)


    def perform_destroy(self, instance):
        """ Supprimer le projet et retourner un message """
        instance.delete()
        return Response({"detail": "Project successfully deleted."})


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # Seul un utilisateur authentifié peut accéder aux utilisateurs
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ContributorViewSet(viewsets.ModelViewSet):
    """
    API CRUD pour gérer les contributeurs d'un projet.
    Seul l’auteur d’un projet peut ajouter ou retirer des contributeurs.
    """
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Un utilisateur peut voir uniquement les contributeurs des projets où il est impliqué.
        """
        user = self.request.user
        return Contributor.objects.filter(project__contributors__user=user)

    def perform_create(self, serializer):
        """
        Seul l’auteur d’un projet peut ajouter un contributeur.
        """
        project = serializer.validated_data['project']
        if project.author != self.request.user:
            raise serializers.ValidationError("Seul l'auteur du projet peut ajouter un contributeur.")
        serializer.save()


class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]  # Limiter l'accès aux utilisateurs authentifiés

    def get_queryset(self):
        """
        Personnaliser la méthode pour filtrer les issues en fonction de l'utilisateur authentifié.
        Un utilisateur peut voir uniquement ses issues ou celles de ses projets.
        """
        user = self.request.user
        # Filtrer les issues assignées à l'utilisateur ou issues des projets auxquels l'utilisateur appartient
        return Issue.objects.filter(
            assignee=user
        ) | Issue.objects.filter(project__contributors__user=user)

    def perform_create(self, serializer):
        """
        Personnaliser la création de l'issue pour lier correctement les données du projet et de l'utilisateur.
        """
        project = self.request.data.get('project')
        if project:
            # Associer l'issue au projet et à l'utilisateur actuel (si nécessaire)
            serializer.save(author=self.request.user, project_id=project)
        else:
            raise serializers.ValidationError("Le projet est requis pour créer une issue.")