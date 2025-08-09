from django.db import models
from django.urls import reverse
from PIL import Image

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    name_ar = models.CharField(max_length=100, blank=True, verbose_name="Nom (Arabe)")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Catégorie")
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})

    def average_rating(self):
        from django.db.models import Avg
        return self.communitypost_set.filter(
            rating__isnull=False,
            is_approved=True
        ).aggregate(Avg('rating'))['rating__avg']

    def review_count(self):
        return self.communitypost_set.filter(is_approved=True).count()

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

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='productimage_set')
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"Image for {self.product.name}"

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
