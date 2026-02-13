from django.urls import path, include
from userauthapp.Controllers.DynamicFormController import DynamicFormController
from userauthapp.Controllers.AuthController import LoginAPIView, RegisterApiView
from userauthapp.views import CustomTokenObtainPairView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .Helpers import getDynamicFormFields

from fabrythingapp.views import (
    ProductViewSet, CategoryViewSet, BrandViewSet,
    ProductReviewViewSet, CartOrderViewSet, WishlistViewSet, CartViewSet,
    AddressViewSet, CheckoutViewSet, OrderViewSet, 
    CheckoutViewSet, OrderHistoryViewSet,
    AddressViewSet, RecommendationViewSet, SimilarProductsViewSet,
    UserPreferenceViewSet, ProductViewTrackingViewSet, ProductFilterFacetsViewSet
)



# Create router for automatic endpoint registration
router = DefaultRouter()

# Cart endpoints
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'checkout', CheckoutViewSet, basename='checkout')
router.register(r'addresses', AddressViewSet, basename='address')


# Wishlist endpoints
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

# Product discovery endpoints
router.register(r'products', ProductViewSet, basename='products')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')

# Review endpoints
router.register(r'reviews', ProductReviewViewSet, basename='review')

# Order endpoints
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'orders', OrderHistoryViewSet, basename='order-history')

# User account endpoints
router.register(r'user/preferences', UserPreferenceViewSet, basename='user-preferences')

# Recommendation endpoints (NEW for Phase 3)
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')

# Filter facets endpoint (NEW for Phase 3)
router.register(r'products/facets', ProductFilterFacetsViewSet, basename='product-facets')

urlpatterns = [
    path('', include(router.urls)),
    
    # Custom endpoints for complex operations
    path('products/<str:product_id>/similar/', 
         SimilarProductsViewSet.as_view({'get': 'similar'}),
         name='similar-products'),
    
    path('products/<str:product_id>/view/',
         ProductViewTrackingViewSet.as_view({'post': 'track_view'}),
         name='track-product-view'),
     # JWT Token endpoints
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Auth endpoints using APIView classes
    path('register/', RegisterApiView.as_view(), name='register'),
    path('signin/', LoginAPIView.as_view(), name='login'),
    path('getForm/<str:modelName>/', DynamicFormController.as_view(), name='getForm'),


]