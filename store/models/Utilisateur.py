from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biographie")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
