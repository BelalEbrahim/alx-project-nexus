from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from ..models import Category, Product

class APITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop', price=999.99, stock=10, category=self.category
        )

    def test_get_products(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_product_authenticated(self):
        token_response = self.client.post('/api/token/', {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {
            'name': 'Phone', 'price': 499.99, 'stock': 20, 'category_id': self.category.id
        }
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_token_endpoint(self):
        response = self.client.post('/api/token/', {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_product_filtering_and_sorting(self):
        # Create additional products for sorting test
        Product.objects.create(name='Phone', price=499.99, stock=20, category=self.category)
        Product.objects.create(name='Headphones', price=99.99, stock=50, category=self.category)
        response = self.client.get(f'/api/products/?category={self.category.id}&ordering=price')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertEqual(response.data['results'][0]['name'], 'Headphones')  # Cheapest first

    def test_product_pagination(self):
        for i in range(14):
            Product.objects.create(
                name=f'Product {i}', price=100.0 + i, stock=10, category=self.category
            )
        response = self.client.get('/api/products/?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 6)  # PAGE_SIZE = 10

    def test_unauthenticated_post_fails(self):
        response = self.client.post('/api/products/', {
            'name': 'Tablet', 'price': 299.99, 'stock': 15, 'category_id': self.category.id
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)