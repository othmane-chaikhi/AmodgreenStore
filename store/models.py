from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from PIL import Image


class CustomUser(AbstractUser):
    """Modèle utilisateur personnalisé avec bio"""
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biographie")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"


class Category(models.Model):
    """Catégorie de produits"""
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
    """Modèle produit"""
    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    name_ar = models.CharField(max_length=200, blank=True, verbose_name="Nom (Arabe)")
    description = models.TextField(verbose_name="Description")
    description_ar = models.TextField(blank=True, verbose_name="Description (Arabe)")
    ingredients = models.TextField(blank=True, verbose_name="Ingrédients")
    ingredients_ar = models.TextField(blank=True, verbose_name="Ingrédients (Arabe)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix (MAD)")
    image = models.ImageField(upload_to='products/', verbose_name="Image")
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
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Redimensionner l'image si elle est trop grande
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 600 or img.width > 600:
                output_size = (600, 600)
                img.thumbnail(output_size)
                img.save(self.image.path)


class Order(models.Model):
    """Modèle commande"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('contacted', 'Client contacté'),
        ('confirmed', 'Confirmée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]
    
    full_name = models.CharField(max_length=200, verbose_name="Nom complet")
    phone = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    city = models.CharField(max_length=100, verbose_name="Ville")
    address = models.TextField(verbose_name="Adresse complète")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantité")
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
        return self.product.price * self.quantity
    
    def get_whatsapp_message(self):
        """Génère le message WhatsApp pour la commande"""
        message = f"""🌿 *Nouvelle commande AmodGreen* 🌿

👤 *Client:* {self.full_name}
📱 *Téléphone:* {self.phone}
🏙️ *Ville:* {self.city}
📍 *Adresse:* {self.address}

🛒 *Produit:* {self.product.name}
📦 *Quantité:* {self.quantity}
💰 *Prix total:* {self.total_price} MAD

📝 *Remarques:* {self.notes if self.notes else 'Aucune'}

_Commande #_{self.id} - {self.created_at.strftime('%d/%m/%Y à %H:%M')}_"""
        return message


class CommunityPost(models.Model):
    """Posts de la communauté"""
    POST_TYPES = [
        ('review', 'Avis produit'),
        ('testimonial', 'Témoignage'),
        ('discussion', 'Discussion'),
    ]
    
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Auteur")
    title = models.CharField(max_length=200, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='discussion', verbose_name="Type de post")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Produit lié")
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


class Comment(models.Model):
    """Commentaires sur les posts"""
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