# catalog/tasks.py
from celery import shared_task
from postmark import PMMail
import os

@shared_task
def send_product_creation_email(product_id):
    # Placeholder: Replace with your actual product model import
    from .models import Product

    product = Product.objects.get(id=product_id)
    api_key = os.environ.get('POSTMARK_API_TOKEN', '')  # Set in Render env vars
    sender = os.environ.get('POSTMARK_SENDER_EMAIL', 'no-reply@your-domain.com')
    recipient = 'admin@example.com'  # Change to dynamic recipient if needed

    message = PMMail(
        api_key=api_key,
        subject=f"New Product Created: {product.name}",
        sender=sender,
        to=recipient,
        html_body=f"<h1>New Product Alert!</h1><p>A new product '{product.name}' with price ${product.price} has been created.</p>",
        text_body=f"New Product Alert!\nA new product '{product.name}' with price ${product.price} has been created."
    )
    message.send()