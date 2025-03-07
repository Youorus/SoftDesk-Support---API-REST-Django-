from rest_framework import serializers
from .models import Project, Contributor, Issue, Comment

# Serializer pour le modèle Project
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'author']  # Remplace par tes champs réels

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
