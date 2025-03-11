import uuid
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, transaction


# 1. USER MODEL (AUTHENTIFICATION)
class User(AbstractUser):
    """
    Modèle personnalisé pour les utilisateurs.
    - Utilise un UUID comme clé primaire.
    - Inclut des champs supplémentaires pour l'âge, les préférences de contact et le partage de données.
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )  # UUID comme clé primaire
    age = models.PositiveIntegerField()  # Âge de l'utilisateur
    can_be_contacted = models.BooleanField(
        default=False
    )  # L'utilisateur peut être contacté
    can_data_be_shared = models.BooleanField(
        default=False
    )  # Les données de l'utilisateur peuvent être partagées
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False
    )  # Date de création

    # Éviter les conflits avec les groupes et permissions par défaut
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="softdesk_users",  # Nom personnalisé pour éviter les conflits
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="softdesk_users_permissions",  # Nom personnalisé pour éviter les conflits
        blank=True,
    )

    def __str__(self):
        """
        Représentation en chaîne de caractères de l'utilisateur.
        """
        return self.username


# 2. PROJECT MODEL
class Project(models.Model):
    """
    Modèle pour les projets.
    - Un projet a un nom, une description, un type et un auteur.
    - Les contributeurs sont gérés via le modèle Contributor.
    """

    BACKEND = "backend"
    FRONTEND = "frontend"
    IOS = "ios"
    ANDROID = "android"

    PROJECT_TYPES = [
        (BACKEND, "Back-end"),
        (FRONTEND, "Front-end"),
        (IOS, "iOS"),
        (ANDROID, "Android"),
    ]

    name = models.CharField(max_length=255)  # Nom du projet
    description = models.TextField(null=True, blank=True)  # Description du projet
    type = models.CharField(max_length=10, choices=PROJECT_TYPES)  # Type de projet
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_projects"
    )  # Auteur du projet
    contributors = models.ManyToManyField(
        User, through="Contributor", related_name="projects"
    )  # Contributeurs du projet
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création

    class Meta:
        ordering = ["-created_at"]  # Tri par date de création décroissante

    def __str__(self):
        """
        Représentation en chaîne de caractères du projet.
        """
        return self.name


# 3. CONTRIBUTOR MODEL
class Contributor(models.Model):
    """
    Modèle pour les contributeurs d'un projet.
    - Un contributeur est un utilisateur associé à un projet avec un rôle spécifique.
    """

    CONTRIBUTOR = "contributor"
    AUTHOR = "author"

    ROLE_CHOICES = [(CONTRIBUTOR, "Contributor"), (AUTHOR, "Author")]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Utilisateur contributeur
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="contributor_set"
    )  # Projet associé
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default=CONTRIBUTOR
    )  # Rôle du contributeur

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "project"], name="unique_contributor"
            )  # Contrainte d'unicité
        ]

    def __str__(self):
        """
        Représentation en chaîne de caractères du contributeur.
        """
        return f"{self.user.username} - {self.project.name} ({self.role})"


# 4. ISSUE MODEL
class Issue(models.Model):
    """
    Modèle pour les issues (problèmes) d'un projet.
    - Une issue a un titre, une description, une priorité, un tag, un statut, un assigné et un auteur.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    PRIORITY_CHOICES = [(LOW, "Low"), (MEDIUM, "Medium"), (HIGH, "High")]

    BUG = "BUG"
    FEATURE = "FEATURE"
    TASK = "TASK"
    TAG_CHOICES = [(BUG, "Bug"), (FEATURE, "Feature"), (TASK, "Task")]

    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    FINISHED = "Finished"
    STATUS_CHOICES = [
        (TODO, "To Do"),
        (IN_PROGRESS, "In Progress"),
        (FINISHED, "Finished"),
    ]

    title = models.CharField(max_length=255)  # Titre de l'issue
    description = models.TextField(null=True, blank=True)  # Description de l'issue
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default=LOW
    )  # Priorité de l'issue
    tag = models.CharField(
        max_length=10, choices=TAG_CHOICES, default=TASK
    )  # Tag de l'issue
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default=TODO
    )  # Statut de l'issue
    assignee = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_issues",
    )  # Assigné de l'issue
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="issues"
    )  # Projet associé
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Auteur de l'issue
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création

    def __str__(self):
        """
        Représentation en chaîne de caractères de l'issue.
        """
        return self.title


# 5. COMMENT MODEL
class Comment(models.Model):
    """
    Modèle pour les commentaires sur une issue.
    - Un commentaire a un contenu, une issue associée et un auteur.
    """

    content = models.TextField()  # Contenu du commentaire
    issue = models.ForeignKey(
        Issue, on_delete=models.CASCADE, related_name="comments"
    )  # Issue associée
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Auteur du commentaire
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création

    def __str__(self):
        """
        Représentation en chaîne de caractères du commentaire.
        """
        return f"Comment by {self.author} on {self.issue}"
