
from django.db import models
from django.conf import settings

SOURCE_CHOICES = \
    [
        ("admin", "Créé via Admin"),
        ("tmdb", "Importé depuis TMDb")
    ]

class AuteurProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="auteur_profile")
    nom = models.CharField(max_length=10, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    date_naissance = models.DateField(blank=True, null=True)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default="admin")

    def __str__(self):
        return self.nom

class Film(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date_sortie = models.DateField()


    auteurs = models.ManyToManyField(AuteurProfile, related_name="films")

    EVALUATION_CHOICES = [("excellent","Excellent"), ("bon","Bon"), ("moyen","Moyen"), ("mauvais","Mauvais")]
    evaluation = models.CharField(max_length=20, choices=EVALUATION_CHOICES, blank=True, null=True)

    STATUT_CHOICES = [("production","En production"), ("salle","En salle"), ("sorti","Sorti")]
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="production")

    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default="admin")

    def __str__(self):
        return self.titre

class SpectateurProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="spectateur_profile")
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    favoris_films = models.ManyToManyField(Film, related_name="favoris_spectateurs", blank=True)
    favoris_auteurs = models.ManyToManyField(AuteurProfile, related_name="favoris_spectateurs", blank=True)

    def __str__(self):
        return self.user.username
