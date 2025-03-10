from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views

# Importation des ViewSets pour tes modèles
from .views import UserViewSet, ProjectViewSet, IssueViewSet, ContributorViewSet, register

# Désactiver l'ajout automatique du slash final
router = DefaultRouter(trailing_slash=False)

# Enregistrement des ViewSets pour chaque modèle
router.register(r'users', UserViewSet, basename='user')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'issues', IssueViewSet, basename='issue')
router.register(r'contributors', ContributorViewSet, basename='contributor')


urlpatterns = [
    path('register/', register, name='register'),
    # Enregistrement des routes API pour les JWT
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls  # Inclure les routes du routeur pour les projets et utilisateurs
