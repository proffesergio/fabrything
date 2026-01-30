from django.contrib import admin
from fabrythingapp.models import Product, Category, Vendor, CartOrder, CartOrderItems, Wishlist, ProductImages, ProductReview, Address, Brand, ProductView, UserPreferences, RecommendationCache


# Register your models here.
class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductImagesAdmin
    ]
    list_display = [
        'user', 'title', 'image', 'price', 'category', 'featured', 'product_status'
    ]

class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'image'
    ]

class BrandAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'image'
    ]

class VendorAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'image'
    ]

class CartOrderAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'price', 'paid_status', 'order_date', 'product_status'
    ]

class CartOrderItemsAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'invoice', 'item', 'image', 'quantity', 'price', 'total'
    ]

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'product', 'review', 'rating'
    ]

class WishlistAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'product', 'date'
    ]

class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'address', 'status'
    ]   


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderItems, CartOrderItemsAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Brand, BrandAdmin)

@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    """Admin interface for ProductView tracking"""
    list_display = ['user', 'product', 'viewed_at']
    list_filter = ['viewed_at', 'product__category']
    search_fields = ['user__email', 'product__title']
    readonly_fields = ['viewed_at']
    date_hierarchy = 'viewed_at'
    
    def has_add_permission(self, request):
        """Prevent manual adding - only created by system"""
        return False


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """Admin interface for user preferences"""
    list_display = ['user', 'created_at', 'updated_at']
    filter_horizontal = ['preferred_categories', 'preferred_brands']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RecommendationCache)
class RecommendationCacheAdmin(admin.ModelAdmin):
    """Admin interface for recommendation caching"""
    list_display = ['cache_type', 'user', 'generated_at', 'expires_at', 'hit_count']
    list_filter = ['cache_type', 'generated_at', 'expires_at']
    search_fields = ['cache_key', 'user__email']
    readonly_fields = ['generated_at', 'cache_key', 'recommendations_data']
    
    def has_add_permission(self, request):
        """Prevent manual adding - only created by system"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion to clear expired caches"""
        return True