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
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'author']  # Remplace par tes champs réels

# Serializer pour le modèle Contributor
class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project', 'role']  # Remplace par tes champs réels

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
