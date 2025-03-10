
from rest_framework import viewsets, serializers
from rest_framework.decorators import api_view, permission_classes

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from softdeskApp.models import Project, User, Contributor, Issue
from softdeskApp.serializers import ProjectSerializer, UserSerializer, ContributorSerializer, IssueSerializer



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# def get_queryset(self):
    #     """
    #     - Un utilisateur ne peut voir que son propre profil
    #     - Un admin peut voir tous les utilisateurs
    #     """
    #     user = self.request.user
    #     if user.is_staff:
    #         return User.objects.all()
    #     return User.objects.filter(id=user.id)  # Un utilisateur voit uniquement lui-même

    # def perform_update(self, serializer):
    #     """
    #     Seul un utilisateur peut modifier son propre profil.
    #     """
    #     user = self.get_object()
    #     if user != self.request.user and not self.request.user.is_staff:
    #         raise serializers.ValidationError("Vous ne pouvez modifier que votre propre profil.")
    #     serializer.save()

    # def perform_destroy(self, instance):
    #     """
    #     Seul un utilisateur peut supprimer son propre compte .
    #     """
    #     if instance != self.request.user and not self.request.user.is_staff:
    #         raise serializers.ValidationError("Vous ne pouvez supprimer que votre propre compte.")
    #     instance.delete()


@api_view(['POST'])
@permission_classes([AllowAny])  # Permet à tout utilisateur, même non authentifié, d'enregistrer un nouvel utilisateur
def register(request):
    if request.method == 'POST':
        # Utilisation du serializer pour valider les données reçues dans la requête
        serializer = UserSerializer(data=request.data)

        # Vérification de la validité des données
        if serializer.is_valid():
            # Si le serializer est valide, on crée un utilisateur
            serializer.save()
            # Réponse avec les données du nouvel utilisateur (ne contient pas le mot de passe)
            return Response(serializer.data)
        # Si les données ne sont pas valides, on renvoie les erreurs
        return Response(serializer.errors)



class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]  # Seuls les utilisateurs connectés ont accès

    def get_queryset(self):
        """
        L'utilisateur ne peut voir que :
        - Les projets qu'il a créés
        - Les projets auxquels il est contributeur
        """
        user = self.request.user
        return Project.objects.filter(contributors__user=user) | Project.objects.filter(author=user)

    def perform_update(self, serializer):
        """
        Seul l'auteur d'un projet peut le modifier.
        """
        project = self.get_object()
        if project.author != self.request.user:
            raise serializers.ValidationError("Vous ne pouvez modifier que vos propres projets.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Seul l'auteur peut supprimer un projet.
        """
        if instance.author != self.request.user:
            raise serializers.ValidationError("Vous ne pouvez supprimer que vos propres projets.")
        instance.delete()


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