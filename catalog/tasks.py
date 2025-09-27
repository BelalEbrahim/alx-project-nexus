import logging  # NEW: For terminal logging
from celery import shared_task
from .models import Product

logger = logging.getLogger(__name__)  # NEW: Logger for Celery worker terminal

@shared_task
def send_product_creation_notification(product_id):
    """Task to notify on product creation - logs to terminal instead of email."""
    try:
        product = Product.objects.get(id=product_id)
        message = f'New Product Created: {product.name} with price ${product.price} and stock {product.stock}.'
        logger.info(message)  # Logs to Celery worker terminal
        # NEW: Simulate multiple notifications (e.g., if batch, this runs concurrently)
        # For demo, log a follow-up message
        logger.info(f'Notification processed for product ID: {product_id}.')
    except Product.DoesNotExist:
        logger.error(f'Product ID {product_id} not found - notification failed.')