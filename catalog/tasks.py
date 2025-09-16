from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_product_creation_email(product_id):
    from .models import Product
    product = Product.objects.get(id=product_id)
    send_mail(
        'New Product Created',
        f'Product {product.name} has been created.',
        'from@example.com',
        ['to@example.com'],
        fail_silently=False,
    )