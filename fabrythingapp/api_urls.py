"""
API URL routing for Fabrything.

Uses DRF's DefaultRouter for automatic endpoint generation from ViewSets.
All routes prefixed with /api/v1/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from fabrythingapp.views import (
    ProductViewSet, CategoryViewSet, BrandViewSet,
    ProductReviewViewSet, CartOrderViewSet, WishlistViewSet,
    AddressViewSet, RecommendationViewSet, SimilarProductsViewSet,
    UserPreferenceViewSet, ProductViewTrackingViewSet, ProductFilterFacetsViewSet
)

# Create router for automatic endpoint registration
router = DefaultRouter()

# Product discovery endpoints
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')

# Review endpoints
router.register(r'reviews', ProductReviewViewSet, basename='review')

# Cart & wishlist endpoints
router.register(r'cart', CartOrderViewSet, basename='cart')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

# User account endpoints
router.register(r'addresses', AddressViewSet, basename='address')
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
]