import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

# 1. USER MODEL (AUTHENTIFICATION)
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID uniquement pour l'user
    age = models.PositiveIntegerField()
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Ajoute ces lignes pour éviter les conflits
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="softdesk_users",  # Change ici pour éviter le conflit
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="softdesk_users_permissions",  # Change ici aussi
        blank=True
    )

    def save(self, *args, **kwargs):
        if self.age < 15:
            raise ValueError("L'utilisateur doit avoir plus de 15 ans pour consentir à la collecte des données.")
        super().save(*args, **kwargs)


# 2. PROJECT MODEL
class Project(models.Model):
    BACKEND = 'backend'
    FRONTEND = 'frontend'
    IOS = 'ios'
    ANDROID = 'android'

    PROJECT_TYPES = [
        (BACKEND, 'Back-end'),
        (FRONTEND, 'Front-end'),
        (IOS, 'iOS'),
        (ANDROID, 'Android'),
    ]

    id = models.AutoField(primary_key=True)  # AutoField pour générer un id automatiquement
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=10, choices=PROJECT_TYPES)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_projects")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 3. CONTRIBUTOR MODEL
class Contributor(models.Model):
    CONTRIBUTOR = 'contributor'
    ROLE_CHOICES = [(CONTRIBUTOR, 'Contributor')]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="contributors")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CONTRIBUTOR)

    class Meta:
        unique_together = ('user', 'project')

# 4. ISSUE MODEL
class Issue(models.Model):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    PRIORITY_CHOICES = [(LOW, 'Low'), (MEDIUM, 'Medium'), (HIGH, 'High')]

    BUG = 'BUG'
    FEATURE = 'FEATURE'
    TASK = 'TASK'
    TAG_CHOICES = [(BUG, 'Bug'), (FEATURE, 'Feature'), (TASK, 'Task')]

    TODO = 'To Do'
    IN_PROGRESS = 'In Progress'
    FINISHED = 'Finished'
    STATUS_CHOICES = [(TODO, 'To Do'), (IN_PROGRESS, 'In Progress'), (FINISHED, 'Finished')]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=LOW)
    tag = models.CharField(max_length=10, choices=TAG_CHOICES, default=TASK)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=TODO)
    assignee = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_issues")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issues")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 5. COMMENT MODEL
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.issue}"
