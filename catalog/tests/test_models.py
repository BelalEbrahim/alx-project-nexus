from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Category, Product

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop', price=999.99, stock=10, category=self.category
        )

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Electronics')

    def test_product_str(self):
        self.assertEqual(str(self.product), 'Laptop')

    def test_product_category_relation(self):
        self.assertEqual(self.product.category.name, 'Electronics')