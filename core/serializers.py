from .models import CustomUser

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()


class CustomUserReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name",
            "role", "is_active", "is_staff",
            "date_joined", "last_login",
        )
        read_only_fields = (
            "id", "is_active", "is_staff",
            "date_joined", "last_login",
        )


class CustomUserWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Ce nom d'utilisateur est déjà pris.")]
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Cet email est déjà utilisé.")]
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role", "password")
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        if hasattr(user, "role") and not user.role:
            user.role = "spectateur"
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
