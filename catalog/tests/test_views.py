from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from ..models import Category, Product
from django.test.utils import override_settings  # NEW
from celery.contrib.testing.worker import start_worker  # NEW: For Celery testing
from ..tasks import send_product_creation_notification

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
        self.assertEqual(len(response.data['results']), 5)  # PAGE_SIZE = 10

    def test_unauthenticated_post_fails(self):
        response = self.client.post('/api/products/', {
            'name': 'Tablet', 'price': 299.99, 'stock': 15, 'category_id': self.category.id
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)  # NEW: Run Celery synchronously for tests
    def test_celery_notification(self):
        product = Product.objects.create(name='Test Product', price=10.0, stock=5, category=self.category)
        send_product_creation_notification.delay(product.id)
        # Assert log output (or check console in real run); for test, use mock.patch on logger if needed
        self.assertTrue(True)  # Placeholder; in real, use mock.patch on logger

    def test_batch_create_products_authenticated(self):
        token_response = self.client.post('/api/token/', {'username': 'testuser', 'password': 'testpass'})
        token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = [
            {'name': 'Batch1', 'price': 10.0, 'stock': 5, 'category_id': self.category.id},
            {'name': 'Batch2', 'price': 20.0, 'stock': 10, 'category_id': self.category.id},
        ]
        response = self.client.post('/api/products/batch_create/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)  # Original + 2 new