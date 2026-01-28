from django.urls import path, include
from rest_framework.routers import DefaultRouter
from fabrythingapp.views import (
    ProductViewSet, CategoryViewSet, BrandViewSet,
    ProductReviewViewSet, CartOrderViewSet, WishlistViewSet,
    AddressViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'reviews', ProductReviewViewSet, basename='review')
router.register(r'cart', CartOrderViewSet, basename='cart')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('', include(router.urls)),
]