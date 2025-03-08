from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, UserViewSet, CustomTokenObtainPairView, TokenRefreshView, CreateUserView

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')  # Route pour les projets
router.register(r'users', UserViewSet, basename='user')  # Route pour les utilisateurs

urlpatterns = [
    # Authentification : obtenir un access token et un refresh token
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Actualiser l'access token à part du refresh token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Création d'un utilisateur
    path('create_user/', CreateUserView.as_view(), name='create_user'),
] + router.urls  # Inclure les routes du routeur pour les projets et utilisateurs
