# apps/users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


SOURCE_CHOICES = \
    [
        ("admin", "Créé via Admin"),
        ("tmdb", "Importé depuis TMDb")
    ]


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('auteur', 'Auteur'),
        ('spectateur', 'Spectateur'),
        ('admin', 'Administrateur'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)



