from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response  # NEW: For batch response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action  # NEW: For custom action
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .tasks import send_product_creation_notification  # UPDATED: Renamed for clarity
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated  # FIXED: Added IsAuthenticated




class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']

    @method_decorator(cache_page(60*15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['category', 'name', 'price']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['name']

    @method_decorator(cache_page(60*15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        product = serializer.save()
        send_product_creation_notification.delay(product.id)  # UPDATED: Use logging task

    # NEW: Batch create endpoint for multiple products (demonstrates multiple Celery tasks)
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def batch_create(self, request):
        """Endpoint to create multiple products in batch, queuing notifications."""
        serializer = ProductSerializer(data=request.data, many=True)  # Expect list of dicts
        if serializer.is_valid():
            products = serializer.save()
            for product in products:
                send_product_creation_notification.delay(product.id)  # Queue multiple tasks
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)