from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers
from .models import User


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ("id", "email", "username", "password", "display_name")


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = [
            "id",
            "email",
            "username",
            "display_name",
            "is_active",
            "is_admin",
            "is_staff",
            "is_superuser",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_active",
            "is_admin",
            "is_staff",
            "is_superuser",
            "created_at",
            "updated_at",
        ]