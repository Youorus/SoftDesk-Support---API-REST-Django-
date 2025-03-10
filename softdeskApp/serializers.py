from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Project, Contributor, Issue, Comment, User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'age', 'can_be_contacted', 'can_data_be_shared', 'created_at')
        extra_kwargs = {
            'password': {'write_only': True},  # Le mot de passe ne sera pas retourné
            'created_at': {'read_only': True},  # Empêche la modification
            'age': {'read_only': True},  # Empêche la modification de l'âge
        }

    def validate_username(self, value):
        """ Empêche la validation du username s'il n'a pas changé """
        if self.instance and self.instance.username == value:
            return value  # Retourne l'ancien username sans erreur
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value

    def validate_password(self, value):
        """
        Valide que le mot de passe répond aux critères de sécurité.
        """
        try:
            validate_password(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def update(self, instance, validated_data):
        """ Empêche la validation des champs non modifiés """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def validate_age(self, value):
        """
        Valide que l'âge de l'utilisateur ne soit pas inferieur  à 15 ans.
        """
        if value < 15:
            raise serializers.ValidationError("L'âge ne peut pas être inferieur à 15 ans.")
        return value

    def create(self, validated_data):
        """
        Crée un utilisateur et chiffre le mot de passe.
        """
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Chiffre le mot de passe
        user.save()
        return user


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.id')  # L'auteur est défini automatiquement

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']  # Ces champs ne doivent pas être modifiables

    def validate_name(self, value):
        """ Empêcher les projets avec un nom trop court. """
        if len(value) < 3:
            raise serializers.ValidationError("Le nom du projet doit contenir au moins 3 caractères.")
        return value

    def create(self, validated_data):
        """
        Lorsqu'un projet est créé, l'utilisateur devient automatiquement son auteur
        et est ajouté comme contributeur.
        """
        user = self.context['request'].user
        project = Project.objects.create(author=user, **validated_data)

        # Ajouter l'auteur comme contributeur automatiquement
        Contributor.objects.create(user=user, project=project, role="author")

        return project

# 3️⃣ CONTRIBUTOR SERIALIZER
class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project', 'role']

    def validate(self, data):
        """ Vérifie que l'utilisateur n'est pas déjà contributeur de ce projet """
        if Contributor.objects.filter(user=data['user'], project=data['project']).exists():
            raise serializers.ValidationError("Cet utilisateur est déjà contributeur de ce projet.")
        return data




# Serializer pour le modèle Issue
class IssueSerializer(serializers.ModelSerializer):
    # Sérialisation de l'assignee pour obtenir des informations sur l'utilisateur
    assignee_username = serializers.CharField(source='assignee.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'priority', 'tag', 'status', 'assignee', 'assignee_username', 'project',
                  'project_name', 'created_at']

    def validate_assignee(self, value):
        """
        Valider si l'utilisateur assigné à l'issue est bien un contributeur du projet.
        """
        project = self.initial_data.get('project')
        if project:
            # Vérifier si l'utilisateur est un contributeur du projet
            if not Contributor.objects.filter(user=value, project=project).exists():
                raise serializers.ValidationError("L'utilisateur assigné n'est pas un contributeur de ce projet.")
        return value


# Serializer pour le modèle Comment
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'updated_at', 'author', 'issue']  # Remplace par tes champs réels
