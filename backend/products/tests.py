from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Product, VariantType, VariantOption, Combination, Order

class ECommerceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Init base product and variants
        self.product = Product.objects.create(name="Test Shirt", base_price=20.00)
        self.vt = VariantType.objects.create(product=self.product, name="Size")
        self.opt1 = VariantOption.objects.create(variant_type=self.vt, value="S")
        self.opt2 = VariantOption.objects.create(variant_type=self.vt, value="M")
        
        #trigger sync and set mock stock
        self.product.refresh_combinations()
        self.combo = self.product.combinations.first()
        self.combo.stock = 5
        self.combo.save()

    def test_combination_generation(self):
        self.assertEqual(self.product.combinations.count(), 2)

    def test_insufficient_stock_prevention(self):
        url = reverse('place-order')
        data = {'combination_id': self.combo.id, 'quantity': 10}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_successful_order(self):
        url = reverse('place-order')
        data = {'combination_id': self.combo.id, 'quantity': 2}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.combo.refresh_from_db()
        self.assertEqual(self.combo.stock, 3)

    def test_protected_deletion(self):
        Order.objects.create(combination=self.combo, quantity=1, total_price=20.00)
        url = reverse('variant-type-delete', kwargs={'pk': self.product.id, 'vid': self.vt.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_simple_product_order(self):
        simple_product = Product.objects.create(name="Simple Mug", base_price=10.00)
        simple_product.refresh_combinations()
        combo = simple_product.combinations.first()
        combo.stock = 10
        combo.save()
        
        url = reverse('place-order')
        data = {'combination_id': combo.id, 'quantity': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_combination_archiving(self):
        self.opt1.delete()
        self.product.refresh_combinations()
        self.assertEqual(self.product.combinations.count(), 1)

    def test_combination_lookup_and_price_calculation(self):
        # Update combo to test final price calculation
        self.combo.additional_price = 5.00
        self.combo.save()
        
        option_ids = list(self.combo.options.values_list('id', flat=True))
        
        url = reverse('combination-lookup', kwargs={'pk': self.product.id})
        data = {'option_ids': option_ids}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if base_price (20) + additional_price (5) = 25.00
        self.assertEqual(response.data['final_price'], "25.00")
        self.assertEqual(response.data['stock'], 5)