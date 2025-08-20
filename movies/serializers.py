from rest_framework import serializers
from .models import AuteurProfile,Film

class AuteurListSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField()
    nom = serializers.CharField()

    class Meta:
        model = AuteurProfile
        fields = ("id", "username", "email", "nom", "date_naissance", "source")

class FilmMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = ("id", "titre", "date_sortie")

class AuteurDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(read_only=True)
    nom = serializers.CharField(read_only=True)

    films = FilmMiniSerializer(many=True, read_only=True)

    class Meta:
        model = AuteurProfile
        fields = ("id", "username", "email", "nom", "date_naissance", "source", "films")

class AuteurModifSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuteurProfile
        fields = ("id", "nom",'email', "date_naissance", "source")
