from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    L'auteur a tous les droits sur l'objet, les autres utilisateurs peuvent seulement le lire.
    """

    def has_object_permission(self, request, view, obj):
        # Les requêtes GET, HEAD et OPTIONS sont toujours autorisées
        if request.method in permissions.SAFE_METHODS:
            return True
        # Seul l'auteur de la ressource peut la modifier/supprimer
        return obj.author == request.user
