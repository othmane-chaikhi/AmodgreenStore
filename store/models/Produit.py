import os
import logging
from django.db import models
from django.urls import reverse
from PIL import Image
from django.core.exceptions import ValidationError
from django.utils import timezone

logger = logging.getLogger(__name__)


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom", db_index=True)
    name_ar = models.CharField(max_length=100, blank=True, verbose_name="Nom (Arabe)")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    name_ar = models.CharField(max_length=200, blank=True, verbose_name="Nom (Arabe)")
    description = models.TextField(verbose_name="Description")
    description_ar = models.TextField(blank=True, verbose_name="Description (Arabe)")
    ingredients = models.TextField(blank=True, verbose_name="Ingrédients")
    ingredients_ar = models.TextField(blank=True, verbose_name="Ingrédients (Arabe)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix (MAD)")
    image = models.ImageField(upload_to='products/', verbose_name="Image principale")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Catégorie", related_name='products')
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    default_variant = models.ForeignKey(
        'ProductVariant',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='default_for_products',
        verbose_name="Variante par défaut"
    )

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})

    def clean(self):
        if self.default_variant and self.default_variant.product != self:
            raise ValidationError("La variante par défaut doit appartenir à ce produit")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Optimize image once after ensuring file exists
        if self.image and os.path.isfile(self.image.path):
            self._optimize_image(self.image.path)

    def _optimize_image(self, path):
        try:
            img = Image.open(path)
            max_size = (800, 800)
            img.thumbnail(max_size)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(path, format='JPEG', quality=70, optimize=True)
        except Exception as e:
            logger.error(f"Erreur d'optimisation d'image: {e}")

    def delete(self, *args, **kwargs):
        """Supprimer aussi le fichier image principale lors de la suppression du produit."""
        if self.image and os.path.isfile(self.image.path):
            try:
                os.remove(self.image.path)
            except FileNotFoundError:
                pass
        super().delete(*args, **kwargs)

    def average_rating(self):
        from django.db.models import Avg
        return self.community_posts.filter(
            rating__isnull=False,
            is_approved=True
        ).aggregate(Avg('rating'))['rating__avg'] or 0

    def review_count(self):
        return self.community_posts.filter(is_approved=True).count()

    def get_default_variant_price(self):
        return self.default_variant.price if self.default_variant else self.price

    def available_variants(self):
        return self.variants.all()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/additional/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Image supplémentaire"
        verbose_name_plural = "Images supplémentaires"
        ordering = ['uploaded_at']

    def __str__(self):
        return f"Image supplémentaire pour {self.product.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            self._optimize_image()

    def _optimize_image(self):
        try:
            img = Image.open(self.image.path)
            max_size = (800, 800)
            img.thumbnail(max_size)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(self.image.path, format='JPEG', quality=70, optimize=True)
        except Exception as e:
            logger.error(f"Erreur d'optimisation d'image supplémentaire: {e}")

    def delete(self, *args, **kwargs):
        """Supprimer le fichier image quand l’objet est supprimé."""
        if self.image and os.path.isfile(self.image.path):
            try:
                os.remove(self.image.path)
            except FileNotFoundError:
                pass
        super().delete(*args, **kwargs)


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=50, verbose_name="Nom de la variante")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix (MAD)")
    is_default = models.BooleanField(default=False, verbose_name="Variante par défaut")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Variante de produit"
        verbose_name_plural = "Variantes de produit"
        ordering = ['-is_default', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'name'],
                name='unique_variant_name_per_product'
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.name} ({self.price} MAD)"

    def clean(self):
        if self.is_default:
            existing_default = ProductVariant.objects.filter(
                product=self.product,
                is_default=True
            ).exclude(pk=self.pk).first()
            if existing_default:
                raise ValidationError("Il y a déjà une variante par défaut pour ce produit")

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.is_default:
            if not self.pk:
                super().save(*args, **kwargs)

            ProductVariant.objects.filter(
                product=self.product
            ).exclude(pk=self.pk).update(is_default=False)

            self.product.default_variant = self
            self.product.save(update_fields=['default_variant'])

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        was_default = self.is_default
        product = self.product
        super().delete(*args, **kwargs)

        if was_default and product:
            new_default = product.variants.first()
            if new_default:
                new_default.is_default = True
                new_default.save()
