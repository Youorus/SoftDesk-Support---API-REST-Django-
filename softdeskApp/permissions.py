from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour vérifier si l'utilisateur est l'auteur de la ressource.
    - Si l'utilisateur est l'auteur, il peut modifier ou supprimer la ressource.
    - Sinon, l'utilisateur peut seulement lire la ressource (GET).
    """
    def has_object_permission(self, request, view, obj):
        # Vérifie si l'objet (ressource) a un attribut 'author'
        if request.method in permissions.SAFE_METHODS:
            return True  # Les méthodes sécurisées (GET, HEAD, OPTIONS) sont autorisées pour tous
        return obj.author == request.user  # L'utilisateur peut modifier ou supprimer seulement s'il est l'auteur
