
from rest_framework import viewsets, serializers
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import PermissionDenied

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from softdeskApp.models import Project, User, Contributor, Issue
from softdeskApp.permissions import IsAuthorOrReadOnly
from softdeskApp.serializers import ProjectSerializer, UserSerializer, ContributorSerializer, IssueSerializer



class UserViewSet(viewsets.ModelViewSet):
    """
    - Un utilisateur peut récupérer son propre profil (GET /api/users/{id}/).
    - Un admin peut voir et gérer tous les utilisateurs.
    - Un utilisateur peut mettre à jour ou supprimer uniquement son propre profil.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Tout le monde doit être connecté

    def get_queryset(self):
        """Un utilisateur voit uniquement son propre profil sauf s'il est admin."""
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        """Seul l'utilisateur concerné ou un admin peut modifier le profil."""
        user = self.get_object()
        if user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Vous ne pouvez modifier que votre propre profil.")
        serializer.save()

    def perform_destroy(self, instance):
        """Seul l'utilisateur concerné ou un admin peut supprimer un compte."""
        if instance != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Vous ne pouvez supprimer que votre propre compte.")
        instance.delete()


@api_view(['POST'])
@permission_classes([AllowAny])  # Permet à tout utilisateur, même non authentifié, d'enregistrer un nouvel utilisateur
def register(request):
    if request.method == 'POST':
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
    L'auteur peut modifier ou supprimer le projet, les autres utilisateurs ne peuvent que lire.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        """
        Lors de la création d'un projet, on définit l'auteur automatiquement
        et on le lie en tant que contributeur.
        """
        # Afficher les données envoyées dans la requête POST
        print("Données envoyées dans le POST :", self.request.data)

        user = self.request.user

        # Vérification si les données du serializer sont valides
        if serializer.is_valid():
            print("Données validées :", serializer.validated_data)


            serializer.save(author=user)

            print(f"Projet créé avec succès, l'auteur {user.username} a été ajouté comme contributeur.")
        else:
            print("Erreurs de validation : ", serializer.errors)

    @action(detail=True, methods=['get'])
    def contributors(self, request, pk=None):
        """
        Récupère tous les contributeurs d'un projet spécifique.
        """
        project = self.get_object()
        contributors = project.contributor_set.all()
        serializer = ContributorSerializer(contributors, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        La logique de mise à jour peut rester simple car la permission gère déjà
        la vérification de l'auteur.
        """
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        La logique de suppression peut rester simple car la permission gère déjà
        la vérification de l'auteur.
        """
        return super().destroy(request, *args, **kwargs)




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