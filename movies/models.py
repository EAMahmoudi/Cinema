
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
        return f"{self.nom}"

