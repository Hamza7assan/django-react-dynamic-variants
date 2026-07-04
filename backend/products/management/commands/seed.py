import random
from django.core.management.base import BaseCommand
from products.models import Product, VariantType, VariantOption, Combination, Order
from django.db import transaction
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seeds products, variants, and options. Uses Smart Sync for combinations.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting to seed database...")

        with transaction.atomic():
            # Clean up existing data safely
            # Order is crucial: Delete Orders -> Combinations -> Products to prevent ProtectedError
            Order.objects.all().delete()
            Combination.objects.all().delete()
            Product.objects.all().delete()
            
            self.stdout.write(self.style.WARNING("Successfully cleared old data and historical orders."))

            products_data = [
                {
                    "name": "Premium Hoodie",
                    "description": "High-quality cotton hoodie for winter.",
                    "base_price": Decimal("35.00"),
                    "variants": {
                        "Size": ["S", "M", "L", "XL"],
                        "Color": ["Black", "Gray", "Navy"]
                    }
                },
                {
                    "name": "Classic T-Shirt",
                    "description": "Everyday essential basic tee.",
                    "base_price": Decimal("15.99"),
                    "variants": {
                        "Size": ["S", "M", "L"],
                        "Color": ["White", "Black"]
                    }
                },
                {
                    "name": "Ceramic Coffee Mug",
                    "description": "Simple elegant mug. No variants.",
                    "base_price": Decimal("12.50"),
                    "variants": {} # Simple Product
                },
                {
                    "name": "Gaming Mousepad",
                    "description": "Extra large surface area.",
                    "base_price": Decimal("25.00"),
                    "variants": {
                        "Size": ["Medium", "Large", "Extended"]
                    }
                },
                {
                    "name": "Wireless Headphones",
                    "description": "Noise-cancelling over-ear headphones.",
                    "base_price": Decimal("89.99"),
                    "variants": {
                        "Color": ["Matte Black", "Silver"]
                    }
                }
            ]

            #                      Create products and variants
            for p_data in products_data:
                product = Product.objects.create(
                    name=p_data["name"],
                    description=p_data["description"],
                    base_price=p_data["base_price"]
                )

                # Create variant types and options
                for v_name, v_options in p_data["variants"].items():
                    vt = VariantType.objects.create(product=product, name=v_name)
                    for opt_value in v_options:
                        VariantOption.objects.create(variant_type=vt, value=opt_value)

                # trigger the smart sync architecture
                # This  builds the Cartesian Product combinations perfectly
                product.refresh_combinations()
                
                self.stdout.write(f"Created '{product.name}' with its combinations.")

            combos = Combination.objects.all()
            for combo in combos:
                combo.stock = random.randint(5, 50)
                
                price_bump = random.choice([Decimal("0.00"), Decimal("0.00"), Decimal("2.50"), Decimal("5.00")])
                combo.additional_price = price_bump
                
                combo.save()

        self.stdout.write(self.style.SUCCESS("✅ Database successfully seeded with Enterprise-Grade architecture!"))