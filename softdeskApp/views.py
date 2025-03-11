from django.db.models import Q
from rest_framework import viewsets, serializers
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from softdeskApp.models import Project, User, Contributor, Issue, Comment
from softdeskApp.permissions import IsAuthorOrContributorOrReadOnly
from softdeskApp.serializers import (
    ProjectSerializer,
    UserSerializer,
    ContributorSerializer,
    IssueSerializer,
    CommentSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les utilisateurs.
    - Un utilisateur peut récupérer son propre profil.
    - Un admin peut voir et gérer tous les utilisateurs.
    - Un utilisateur peut mettre à jour ou supprimer uniquement son propre profil.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Un utilisateur voit uniquement son propre profil sauf s'il est admin.
        """
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        """
        Seul l'utilisateur concerné ou un admin peut modifier le profil.
        """
        user = self.get_object()
        if user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Vous ne pouvez modifier que votre propre profil.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Seul l'utilisateur concerné ou un admin peut supprimer un compte.
        """
        if instance != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Vous ne pouvez supprimer que votre propre compte.")
        instance.delete()


@api_view(["POST"])
@permission_classes(
    [AllowAny]
)  # Permet à tout utilisateur, même non authentifié, d'enregistrer un nouvel utilisateur
def register(request):
    if request.method == "POST":
        # Utilisation du serializer pour valider les données reçues dans la requête
        print(request.data)
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
    """
    ViewSet pour gérer les projets.
    - L'auteur peut modifier ou supprimer le projet.
    - Les contributeurs peuvent lire les ressources du projet.
    - Les autres utilisateurs ne peuvent pas accéder aux ressources.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrContributorOrReadOnly]

    def get_queryset(self):
        """
        Filtre les projets pour ne renvoyer que ceux où l'utilisateur est l'auteur ou un contributeur.
        """
        user = self.request.user
        return Project.objects.filter(Q(author=user) | Q(contributors=user)).distinct()

    def perform_create(self, serializer):
        """
        Crée un projet et définit automatiquement l'auteur.
        """
        user = self.request.user
        serializer.save(author=user)

    @action(detail=True, methods=["get"])
    def contributors(self, request, pk=None):
        """
        Récupère tous les contributeurs d'un projet spécifique.
        """
        project = self.get_object()
        contributors = project.contributor_set.all()
        serializer = ContributorSerializer(contributors, many=True)
        return Response(serializer.data)


class ContributorViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les contributeurs d'un projet.
    - Seul l’auteur d’un projet peut ajouter ou retirer des contributeurs.
    """

    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrContributorOrReadOnly]

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
        project = serializer.validated_data["project"]
        if project.author != self.request.user:
            raise ValidationError(
                "Seul l'auteur du projet peut ajouter un contributeur."
            )
        serializer.save()


class IssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les issues.
    - L'auteur peut modifier ou supprimer l'issue.
    - Les contributeurs peuvent lire les issues.
    - Les autres utilisateurs ne peuvent pas accéder aux issues.
    """

    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrContributorOrReadOnly]

    def get_queryset(self):
        """
        Filtre les issues pour ne renvoyer que celles des projets où l'utilisateur est l'auteur ou un contributeur.
        """
        user = self.request.user
        return Issue.objects.filter(
            Q(project__author=user) | Q(project__contributors__user=user)
        ).distinct()

    def perform_create(self, serializer):
        """
        Crée une issue et définit automatiquement l'auteur et le projet.
        - Vérifie que l'assignee est un contributeur du projet.
        """
        project_id = self.kwargs.get("project_id")
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise NotFound("Le projet spécifié n'existe pas.")

        user = self.request.user

        # Vérifier que l'assignee est un contributeur du projet
        assignee = serializer.validated_data.get("assignee")
        if (
            assignee
            and not Contributor.objects.filter(user=assignee, project=project).exists()
        ):
            raise ValidationError("L'assignee doit être un contributeur du projet.")

        # Définir l'auteur et le projet
        serializer.save(author=user, project=project)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les commentaires.
    - L'auteur peut modifier ou supprimer le commentaire.
    - Les contributeurs peuvent lire les commentaires.
    - Les autres utilisateurs ne peuvent pas accéder aux commentaires.
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrContributorOrReadOnly]

    def get_queryset(self):
        """
        Filtre les commentaires pour ne renvoyer que ceux des issues des projets où l'utilisateur est l'auteur ou un contributeur.
        """
        user = self.request.user
        return Comment.objects.filter(
            Q(issue__project__author=user) | Q(issue__project__contributors__user=user)
        ).distinct()

    def perform_create(self, serializer):
        """
        Crée un commentaire et définit automatiquement l'auteur et l'issue.
        - Vérifie que l'utilisateur est un contributeur du projet associé à l'issue.
        """
        issue_id = self.kwargs.get("issue_id")
        try:
            issue = Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            raise NotFound("L'issue spécifiée n'existe pas.")

        user = self.request.user

        # Vérifier que l'utilisateur est un contributeur du projet associé à l'issue
        project = issue.project
        if not Contributor.objects.filter(user=user, project=project).exists():
            raise ValidationError(
                "Vous n'êtes pas un contributeur du projet associé à cette issue."
            )

        # Définir l'auteur et l'issue
        serializer.save(author=user, issue=issue)
