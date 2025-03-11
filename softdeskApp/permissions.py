from rest_framework import permissions
from .models import Contributor

class IsAuthorOrContributorOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour vérifier si l'utilisateur est l'auteur ou un contributeur du projet.
    - L'auteur peut modifier ou supprimer le projet.
    - Les contributeurs peuvent lire les ressources du projet.
    - Les autres utilisateurs ne peuvent pas accéder aux ressources.
    """
    def has_object_permission(self, request, view, obj):
        # Autoriser les méthodes sécurisées (GET, HEAD, OPTIONS) pour les contributeurs
        if request.method in permissions.SAFE_METHODS:
            # Vérifier si l'utilisateur est un contributeur du projet
            return Contributor.objects.filter(user=request.user, project=obj).exists()

        # Vérifier si l'utilisateur est l'auteur du projet pour les méthodes non sécurisées (POST, PUT, PATCH, DELETE)
        return obj.author == request.user