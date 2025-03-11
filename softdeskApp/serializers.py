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

    def validate_age(self, value):
        """
        Valide que l'âge de l'utilisateur ne soit pas inferieur  à 15 ans.
        """
        if value < 15:
            raise serializers.ValidationError("L'âge ne peut pas être inferieur à 15 ans.")
        return value

    def update(self, instance, validated_data):
        """ Empêche la validation des champs non modifiés """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


    def create(self, validated_data):
        """
        Crée un utilisateur et chiffre le mot de passe.
        """

        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Chiffre le mot de passe
        user.save()
        return user

# 3️⃣ CONTRIBUTOR SERIALIZER
class ContributorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Utiliser PrimaryKeyRelatedField
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())  # Utiliser PrimaryKeyRelatedField

    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project', 'role']
        extra_kwargs = {
            'role': {'read_only': True},  # Le rôle est défini automatiquement
        }

    def create(self, validated_data):
        """
        Crée un contributeur avec le rôle par défaut "contributor" ou "author".
        """
        user = validated_data.get('user')
        project = validated_data.get('project')

        # Vérifier si ce contributeur existe déjà pour ce projet
        if Contributor.objects.filter(user=user, project=project).exists():
            raise ValidationError("Cet utilisateur est déjà un contributeur pour ce projet.")

        # Créer un contributeur si il n'existe pas déjà
        validated_data['role'] = Contributor.CONTRIBUTOR  # ou Contributor.AUTHOR selon le contexte
        return super().create(validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')  # Afficher le nom de l'auteur
    contributors = ContributorSerializer(source='contributor_set', many=True, read_only=True)  # Utiliser le related_name

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author', 'contributors', 'created_at']
        read_only_fields = ['author', 'created_at', 'contributors']

    # Validation pour le nom du projet (doit être unique)
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Le nom du projet ne peut pas être vide.")
        if Project.objects.filter(name=value).exists():
            raise serializers.ValidationError("Un projet avec ce nom existe déjà.")
        return value

    # Validation pour la description (si elle est nécessaire)
    def validate_description(self, value):
        if not value:
            raise serializers.ValidationError("La description du projet est requise.")
        return value

    # Validation pour le type du projet (doit être l'un des choix)
    def validate_type(self, value):
        valid_types = [Project.BACKEND, Project.FRONTEND, Project.IOS, Project.ANDROID]
        if value not in valid_types:
            raise serializers.ValidationError(f"Le type doit être l'un des suivants : {', '.join(valid_types)}.")
        return value

    def create(self, validated_data):
        """
        Lorsqu'un utilisateur crée un projet :
        - Il devient **l'auteur**
        - Il est automatiquement **ajouté comme contributeur** (s'il n'existe pas déjà)
        """
        user = self.context['request'].user  # Récupérer l'utilisateur actuel
        validated_data['author'] = user  # Assigner l'auteur

        # Créer le projet
        project = Project.objects.create(**validated_data)

        # Ajouter l'auteur comme contributeur (s'il n'existe pas déjà)
        Contributor.objects.get_or_create(user=user, project=project, defaults={'role': Contributor.AUTHOR})

        return project


class IssueSerializer(serializers.ModelSerializer):
    assignee_username = serializers.CharField(source='assignee.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'priority', 'tag', 'status',
            'assignee', 'assignee_username', 'project', 'project_name',
            'author', 'author_username', 'created_at'
        ]
        read_only_fields = ['author', 'created_at', 'assignee_username', 'project_name', 'author_username']

    def validate_assignee(self, value):
        """
        Valide que l'assignee est un contributeur du projet.
        """
        if value:
            project = self.context.get('project')
            if project and not Contributor.objects.filter(user=value, project=project).exists():
                raise serializers.ValidationError("L'assignee doit être un contributeur du projet.")
        return value

    def validate_project(self, value):
        """
        Valide que le projet existe.
        """
        if not Project.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Le projet spécifié n'existe pas.")
        return value


# Serializer pour le modèle Comment
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'updated_at', 'author', 'issue']  # Remplace par tes champs réels
