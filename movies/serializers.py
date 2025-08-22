from rest_framework import serializers
from .models import AuteurProfile,Film,SpectateurProfile,NotationFilm,NotationAuteur
from core.serializers import CustomUserReadSerializer
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

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



class FilmListSerializer(serializers.ModelSerializer):


    class Meta:
        model = Film
        fields = ("id", "titre", "description", "evaluation","statut")

class FilmDetailSerializer(serializers.ModelSerializer):
    auteurs = AuteurListSerializer(many=True, read_only=True)
    class Meta:
        model = Film
        fields = ("id", "titre", "description", "evaluation","statut",'auteurs')

class FilmModifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = ("id", "titre", "description", "evaluation","statut",'auteurs')

class FavoriFilmAddSerializer(serializers.Serializer):
    film_id = serializers.IntegerField()

class SpectateurReadSerializer(serializers.ModelSerializer):
    user = CustomUserReadSerializer(read_only=True)

    favoris_films = FilmListSerializer(many=True, read_only=True)
    favoris_auteurs = AuteurListSerializer(many=True, read_only=True)

    class Meta:
        model = SpectateurProfile
        fields = ("id", "user", "bio", "avatar", "favoris_films", "favoris_auteurs")

class SpectateurSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Nom d'utilisateur déjà pris.")]
    )
    email = serializers.EmailField(
        required=False, allow_blank=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email déjà utilisé.")]
    )
    bio = serializers.CharField(
        required=False, allow_blank=True,
    )
    class Meta:
        model = User
        fields = ("id", "username", "email", "password",'bio')

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        bio = ""
        if 'bio' in validated_data:
            bio = validated_data.pop("bio")
        user = User(**validated_data)

        if hasattr(user, "role"):
            user.role = "spectateur"
        user.set_password(password)
        user.save()
        SpectateurProfile.objects.create(user=user,bio=bio)
        return user

    def to_representation(self, instance):

        return {
            "id": instance.id,
            "username": instance.username,
            "email": instance.email,
            "bio": instance.spectateur_profile.bio,
            "role": getattr(instance, "role", None),
        }

class RateFilmSerializer(serializers.ModelSerializer):
    film = serializers.PrimaryKeyRelatedField(queryset=Film.objects.all())

    class Meta:
        model = NotationFilm
        fields = ("film", "note", "commentaire")
        extra_kwargs = {
            "note": {"min_value": 1, "max_value": 5}
        }

    def validate(self, attrs):
        req = self.context.get("request")
        try:
            spectateur = SpectateurProfile.objects.get(user=req.user)
        except SpectateurProfile.DoesNotExist:
            raise serializers.ValidationError("Profil spectateur introuvable.")

        film = attrs["film"]
        if NotationFilm.objects.filter(spectateur=spectateur, film=film).exists():
            raise serializers.ValidationError("Vous avez déjà noté ce film.")
        attrs["spectateur"] = spectateur
        return attrs

    # def create(self, validated_data):
    #     spectateur = validated_data.pop("spectateur")
    #     film = validated_data["film"]
    #     note = validated_data.get("note")
    #     commentaire = validated_data.get("commentaire")
    #     instance, _ = NotationFilm.objects.update_or_create(
    #         spectateur=spectateur,
    #         film=film,
    #         defaults={"note": note, "commentaire": commentaire},
    #     )
    #     return instance

class NotationAuteurSerializer(serializers.ModelSerializer):
    auteur = serializers.PrimaryKeyRelatedField(queryset=AuteurProfile.objects.all())

    class Meta:
        model = NotationAuteur
        fields = ("auteur", "note", "commentaire")
        extra_kwargs = {
            "note": {"min_value": 1, "max_value": 5}
        }

    def validate(self, attrs):
        req = self.context.get("request")
        try:
            spectateur = SpectateurProfile.objects.get(user=req.user)
        except SpectateurProfile.DoesNotExist:
            raise serializers.ValidationError("Profil spectateur introuvable.")

        auteur = attrs["auteur"]
        if NotationAuteur.objects.filter(spectateur=spectateur, auteur=auteur).exists():
            raise serializers.ValidationError("Vous avez déjà noté cette auteur.")
        attrs["spectateur"] = spectateur
        return attrs
