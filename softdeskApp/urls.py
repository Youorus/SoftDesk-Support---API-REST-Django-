# softdeskApp/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, UserViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')  # Enregistre les projets
router.register(r'users', UserViewSet, basename='user')  # Enregistre les utilisateurs

urlpatterns = router.urls  # Inclut les routes générées automatiquement par le router
