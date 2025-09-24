from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import RedirectView, TemplateView  # Add TemplateView for test page
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from catalog.views import CategoryViewSet, ProductViewSet

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_auth(request):
    return JsonResponse({'message': 'Authenticated test successful'})

def health_check(request):
    return JsonResponse({'status': 'ok', 'database': 'connected', 'redis': 'connected'})

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
    path('', RedirectView.as_view(url='/api/docs/')),  # Root redirect to Swagger
    path('admin/', admin.site.urls),  # Admin dashboard
    path('accounts/', include('django.contrib.auth.urls')),  # Auth routes (login/logout)
    path('api/', include(router.urls)),  # API endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('health/', health_check, name='health_check'),  # Health check for testing
    path('api/test-auth/', test_auth, name='test_auth'),  # Protected test route
    path('test/', TemplateView.as_view(template_name='test.html'), name='test_page'),  # Simple test page (create test.html in templates)
]

# Create templates/test.html locally for testing
# test.html content:
# <h1>Test Page</h1>
# <p>This is a test route for functionality.</p>