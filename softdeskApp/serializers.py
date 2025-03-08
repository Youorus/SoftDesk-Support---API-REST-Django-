from rest_framework import serializers
from .models import Project, Contributor, Issue, Comment, User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'age', 'can_be_contacted', 'can_data_be_shared', 'created_at']

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Le nom d'utilisateur doit contenir au moins 3 caractères.")
        return value

    def validate_age(self, value):
        if value < 15:
            raise serializers.ValidationError("L'utilisateur doit avoir plus de 15 ans pour consentir à la collecte des données.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        return value

    def create(self, validated_data):
        # Hash the password before saving the user
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)  # Set password hash
        user.save()
        return user


# Serializer pour le modèle Project
class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    # Validation du nom
    name = serializers.CharField(
        min_length=3,
        max_length=100,
        error_messages={
            'min_length': "Le nom du projet doit contenir au moins 3 caractères.",
            'max_length': "Le nom du projet ne doit pas dépasser 100 caractères."
        }
    )

    # Validation du type avec une liste restreinte de choix
    TYPE_CHOICES = ['Back-end', 'Front-end', 'iOS', 'Android']
    type = serializers.ChoiceField(
        choices=TYPE_CHOICES,
        error_messages={'invalid_choice': "Le type doit être 'Back-end', 'Front-end', 'iOS' ou 'Android'."}
    )

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    # Validation personnalisée du nom pour éviter les noms vides ou avec juste des espaces
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Le nom du projet ne peut pas être vide ou composé uniquement d'espaces.")
        return value

class ContributorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project', 'role']
        read_only_fields = ['id']

    def validate_user(self, value):
        """ Vérifie qu'un utilisateur ne peut pas être contributeur deux fois pour le même projet. """
        project = self.initial_data.get('project')
        if Contributor.objects.filter(user=value, project=project).exists():
            raise serializers.ValidationError("Cet utilisateur est déjà contributeur de ce projet.")
        return value


# Serializer pour le modèle Issue
class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'status', 'created_at', 'updated_at', 'assigned_to', 'project']  # Remplace par tes champs réels

# Serializer pour le modèle Comment
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'updated_at', 'author', 'issue']  # Remplace par tes champs réels
