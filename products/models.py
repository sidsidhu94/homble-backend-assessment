from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator



class Product(models.Model):
    """
    Very basic structure. To be further built up.
    """

    name = models.CharField(
        _("display name"),
        max_length=150,
        unique=True,
        help_text=_("This will be displayed to user as-is"),
    )
    price = models.PositiveSmallIntegerField(
        _("selling price (Rs.)"),
        help_text=_("Price payable by customer (Rs.)"),
    )
    description = models.TextField(
        _("descriptive write-up"),
        unique=True,
        help_text=_("Few sentences that showcase the appeal of the product"),
    )
    ingredients = models.CharField(
        _("ingredients"),
        max_length=500,
        help_text=_("ingredients present in the product"),
        null=True,
        blank=True,
    )
    is_refrigerated = models.BooleanField(
        help_text=_("Whether the product needs to be refrigerated"),
        default=False,
    )
    category = models.ForeignKey(
        "categories.Category",
        related_name="products",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    managed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="managed_products",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.name = self.name.strip().title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (Rs. {self.price})"

    class Meta:
        # Just to be explicit.
        db_table = "product"
        ordering = []
        verbose_name = "Product"
        verbose_name_plural = "Products"



class Sku(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.PositiveSmallIntegerField(unique=False, validators=[MinValueValidator(1)])
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.size} gm"
    
    