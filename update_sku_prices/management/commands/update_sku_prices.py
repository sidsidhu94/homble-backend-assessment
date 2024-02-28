from django.core.management.base import BaseCommand
from products.models import Sku, Product
from django.db.models import F, ExpressionWrapper, DecimalField
from decimal import Decimal


def transfer_price_to_selling_price():
    if not hasattr(Product, "price"):
        return
    for product in Product.objects.all():
        sku, created = Sku.objects.get_or_create(
            product=product,
            size=0,
            defaults={"selling_price": 0.0, "platform_commission": 0, "cost_price": 0},
        )
        sku.selling_price = product.price
        sku.save()


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        transfer_price_to_selling_price()
        self.stdout.write(
            self.style.SUCCESS("transfer price to selling price updated successfully")
        )

        Sku.objects.update(
            platform_commission=F("selling_price") * Decimal("0.25"),
            cost_price=ExpressionWrapper(
                F("selling_price") - (F("selling_price") * Decimal("0.25")),
                output_field=DecimalField(),
            ),
        )

        self.stdout.write(self.style.SUCCESS("Prices updated successfully"))
