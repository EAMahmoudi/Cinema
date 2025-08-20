from rest_framework import serializers
from .models import AuteurProfile

class AuteurListSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField()
    nom = serializers.CharField()

    class Meta:
        model = AuteurProfile
        fields = ("id", "username", "email", "nom", "date_naissance", "source")
