# catalog/tasks.py
from celery import shared_task
from postmarker.core import PostmarkClient
import os

@shared_task
def send_product_creation_email(product_id):
    # Placeholder: Replace with your actual product model import
    from .models import Product

    product = Product.objects.get(id=product_id)
    api_key = os.environ.get('POSTMARK_API_TOKEN', '')
    sender = os.environ.get('POSTMARK_SENDER_EMAIL', 'no-reply@your-domain.com')
    recipient = 'admin@example.com'  # Change to dynamic recipient if needed

    client = PostmarkClient(api_key)
    client.emails.send(
        From=sender,
        To=recipient,
        Subject=f"New Product Created: {product.name}",
        HtmlBody=f"<h1>New Product Alert!</h1><p>A new product '{product.name}' with price ${product.price} has been created.</p>",
        TextBody=f"New Product Alert!\nA new product '{product.name}' with price ${product.price} has been created."
    )