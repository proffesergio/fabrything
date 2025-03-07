from django.contrib import admin
from fabrythingapp.models import Product, Category, Vendor, CartOrder, CartOrderItems, Wishlist, ProductImages, ProductReview, Address, Brand


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