from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.contrib.auth import get_user_model
from PIL import Image
import os
from django.conf import settings
from .Utilisateur import *
from .Produit import *
from .Communaute import *
from .Commands import *


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
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)  # ✅ changé ici
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.variant.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.variant.product.name} ({self.variant.name})"
