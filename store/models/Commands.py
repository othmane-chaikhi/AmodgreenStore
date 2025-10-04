from django.db import models


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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de commande")
    estimated_delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de livraison estimée"
    )

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande #{self.id} - {self.full_name}"

    @property
    def total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())

    def delete(self, *args, **kwargs):
        # If you want to soft delete instead of wiping data:
        self.is_deleted = True
        self.save()
        # If you still want to delete related items, uncomment:
        # self.items.all().delete()
        # super().delete(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    variant = models.ForeignKey(
        'store.ProductVariant',
        related_name='order_items',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.variant.product.name} ({self.variant.name}) x{self.quantity}"
