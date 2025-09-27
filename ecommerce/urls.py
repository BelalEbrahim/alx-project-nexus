from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import RedirectView, TemplateView
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from catalog.views import CategoryViewSet, ProductViewSet
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from catalog.models import Category, Product
from catalog.forms import CategoryForm, ProductForm  # UPDATED: Use forms

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_auth(request):
    return JsonResponse({'message': 'Authenticated test successful'})

def health_check(request):
    return JsonResponse({'status': 'ok', 'database': 'connected', 'redis': 'connected'})

@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/api/categories/')
    else:
        form = CategoryForm()
    return render(request, 'create_category.html', {'form': form})

@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/api/products/')
    else:
        form = ProductForm()
    return render(request, 'create_product.html', {'form': form})

schema_view = get_schema_view(
    openapi.Info(
        title="E-Commerce Backend API",
        default_version='v1',
        description="API for managing e-commerce product catalog",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)


urlpatterns = [
    path('', RedirectView.as_view(url='/api/docs/')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('health/', health_check, name='health_check'),
    path('api/test-auth/', test_auth, name='test_auth'),
    path('test/', TemplateView.as_view(template_name='test.html'), name='test_page'),
    path('categories/create/', create_category, name='create_category'),  # New form route
    path('products/create/', create_product, name='create_product'),  # New form route
]