# softdeskApp/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, UserViewSet, CustomTokenObtainPairView
from rest_framework_simplejwt import views as jwt_views

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')  # Enregistre les projets
router.register(r'users', UserViewSet, basename='user')  # Enregistre les utilisateurs

# Ajouter les endpoints pour l'authentification JWT
urlpatterns = [
    # Authentification : obtenir un access token et un refresh token
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Actualiser l'access token à part du refresh token
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls  # Inclure les routes du routeur
