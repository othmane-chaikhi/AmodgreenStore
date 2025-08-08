from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.contrib.auth import get_user_model
from PIL import Image

# =========================
# Utilisateur personnalisé
# =========================

class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biographie")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

# =========================
# Catégories & Produits
# =========================

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
            post_type='review',
            rating__isnull=False,
            is_approved=True
        ).aggregate(Avg('rating'))['rating__avg']

    def review_count(self):
        return self.communitypost_set.filter(
            post_type='review',
            is_approved=True
        ).count()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 600 or img.width > 600:
                img.thumbnail((600, 600))
                img.save(self.image.path)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='productimage_set')

    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"Image for {self.product.name}"

# =========================
# Commandes
# =========================

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('contacted', 'Client contacté'),
        ('confirmed', 'Confirmée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]

    is_deleted = models.BooleanField(default=False)
    full_name = models.CharField(max_length=200, verbose_name="Nom complet")
    phone = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    city = models.CharField(max_length=100, verbose_name="Ville")
    address = models.TextField(verbose_name="Adresse complète")
    notes = models.TextField(blank=True, verbose_name="Remarques")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de commande")
    estimated_delivery_date = models.DateField(null=True, blank=True, verbose_name="Date de livraison estimée")

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande #{self.id} - {self.full_name}"

    @property
    def total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())

    def get_whatsapp_message(self):
        message = (
            f"🌿 *Nouvelle commande AmodIgren* 🌿\n\n"
            f"👤 *Client:* {self.full_name}\n"
            f"📱 *Téléphone:* {self.phone}\n"
            f"🏙️ *Ville:* {self.city}\n"
            f"📍 *Adresse:* {self.address}\n\n"
            f"🛒 *Produits commandés:*\n"
        )
        for item in self.items.all():
            message += f"• {item.product.name} x{item.quantity} ({item.price} MAD)\n"
        message += (
            f"\n💰 *Prix total:* {self.total_price} MAD\n"
            f"📝 *Remarques:* {self.notes if self.notes else 'Aucune'}\n"
            f"_Commande #{self.id} - {self.created_at.strftime('%d/%m/%Y à %H:%M')}_"
        )
        return message

    def delete(self, *args, **kwargs):
        self.items.all().delete()
        super().delete(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

# =========================
# Panier
# =========================

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Panier de {self.user.username}" if self.user else f"Panier session {self.session_key}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

# =========================
# Communauté
# =========================

class CommunityPost(models.Model):
    POST_TYPES = [
        ('review', 'Avis produit'),
        ('testimonial', 'Témoignage'),
        ('discussion', 'Discussion'),
    ]

    RATING_CHOICES = [
        (5, '★★★★★ - Excellent'),
        (4, '★★★★☆ - Très bon'),
        (3, '★★★☆☆ - Bon'),
        (2, '★★☆☆☆ - Moyen'),
        (1, '★☆☆☆☆ - Décevant'),
    ]

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Auteur")
    title = models.CharField(max_length=200, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='discussion', verbose_name="Type de post")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Produit lié")
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, null=True, blank=True, verbose_name="Note")
    is_approved = models.BooleanField(default=True, verbose_name="Approuvé")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Post communauté"
        verbose_name_plural = "Posts communauté"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.author.username}"

    def get_absolute_url(self):
        return reverse('community') + f'#post-{self.id}'

    def get_rating_stars(self):
        full_stars = '★' * self.rating if self.rating else ''
        empty_stars = '☆' * (5 - self.rating) if self.rating else '☆☆☆☆☆'
        return f'<span class="text-yellow-500">{full_stars}{empty_stars}</span>'

class Comment(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments', verbose_name="Post")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Auteur")
    content = models.TextField(verbose_name="Commentaire")
    is_approved = models.BooleanField(default=False, verbose_name="Approuvé")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['created_at']

    def __str__(self):
        return f"Commentaire de {self.author.username} sur {self.post.title}"
