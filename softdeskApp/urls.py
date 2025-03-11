from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views

# Importation des ViewSets pour les modèles
from .views import (
    UserViewSet,
    ProjectViewSet,
    IssueViewSet,
    ContributorViewSet,
    register,
    CommentViewSet,
)

# Désactiver l'ajout automatique du slash final
router = DefaultRouter(trailing_slash=False)

# Enregistrement des ViewSets pour chaque modèle
router.register(r"users", UserViewSet, basename="user")  # Gestion des utilisateurs
router.register(r"projects", ProjectViewSet, basename="project")  # Gestion des projets
router.register(
    r"projects/(?P<project_id>\d+)/issues", IssueViewSet, basename="issue"
)  # Gestion des issues
router.register(
    r"issues/(?P<issue_id>\d+)/comments", CommentViewSet, basename="comment"
)  # Gestion des commentaires

# Définition des URL patterns
urlpatterns = [
    # Route pour l'inscription des utilisateurs
    path("register/", register, name="register"),
    # Routes pour l'authentification JWT
    path(
        "token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),  # Obtention du token JWT
    path(
        "token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"
    ),  # Rafraîchissement du token JWT
] + router.urls  # Inclure les routes du routeur pour les projets et utilisateurs
