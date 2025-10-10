from django.db import models
from django.conf import settings
from PIL import Image
import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


class CommunityPost(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name="Auteur"
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    product = models.ForeignKey(
        'store.Product', 
        on_delete=models.CASCADE, 
        verbose_name="Produit lié",
        related_name='community_posts'
    )
    rating = models.PositiveSmallIntegerField(
        choices=[
            (5, '★★★★★ - Excellent'),
            (4, '★★★★☆ - Très bon'),
            (3, '★★★☆☆ - Bon'),
            (2, '★★☆☆☆ - Moyen'),
            (1, '★☆☆☆☆ - Décevant'),
        ],
        verbose_name="Note"
    )
    image = models.ImageField(
        upload_to='reviews/', 
        blank=True, 
        null=True, 
        verbose_name="Photo"
    )
    is_approved = models.BooleanField(default=True, verbose_name="Approuvé")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Avis produit"
        verbose_name_plural = "Avis produits"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['product']),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img_path = self.image.path
            img = Image.open(img_path)
            max_size = (800, 800)
            img.thumbnail(max_size)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(img_path, format='JPEG', quality=70, optimize=True)

    def __str__(self):
        return f"{self.title} - {self.author.username}"
