# softdeskApp/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')  # Assure-toi que 'projects' est enregistré ici

urlpatterns = router.urls  # Inclut les routes générées automatiquement par le router
