from rest_framework import serializers
from fabrythingapp.models import (
    Product, Category, Brand, ProductReview, 
    CartOrder, CartOrderItems, Wishlist, Address, ProductImages
)
from userauthapp.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['cid', 'title', 'image']
        read_only_fields = ['cid']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['bid', 'title', 'image']
        read_only_fields = ['bid']

class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ['id', 'images', 'date']
        read_only_fields = ['id', 'date']

class ProductSerializer(serializers.ModelSerializer):
    product_images = ProductImagesSerializer(many=True, read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)
    brand_title = serializers.CharField(source='brand.title', read_only=True)
    discount_amount = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'pid', 'title', 'image', 'product_images', 'description',
            'category', 'category_title', 'brand', 'brand_title',
            'price', 'old_price', 'discount_amount', 'discount_percent',
            'type', 'stock_count', 'sizes', 'product_status',
            'status', 'in_stock', 'featured', 'sku', 'date', 'updated'
        ]
        read_only_fields = ['pid', 'sku', 'date', 'updated']
    
    def get_discount_amount(self, obj):
        return obj.get_discount()
    
    def get_discount_percent(self, obj):
        if obj.old_price > 0:
            percent = ((obj.old_price - obj.price) / obj.old_price) * 100
            return round(percent, 2)
        return 0

class ProductDetailSerializer(ProductSerializer):
    reviews = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        return ProductReviewSerializer(reviews, many=True).data
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            total = sum(r.rating for r in reviews)
            return round(total / reviews.count(), 1)
        return 0
    
    def get_review_count(self, obj):
        return obj.reviews.count()

class ProductReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'user', 'user_name', 'user_email', 'product',
            'product_title', 'review_heading', 'review', 'rating', 'date'
        ]
        read_only_fields = ['id', 'user', 'date']

class CartOrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartOrderItems
        fields = [
            'id', 'order', 'invoice', 'product_status',
            'item', 'image', 'quantity', 'price', 'total'
        ]
        read_only_fields = ['id', 'invoice', 'total']

class CartOrderSerializer(serializers.ModelSerializer):
    items = CartOrderItemsSerializer(
        source='cartorderitems_set',
        many=True,
        read_only=True
    )
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = CartOrder
        fields = [
            'id', 'user', 'user_email', 'price', 'paid_status',
            'order_date', 'product_status', 'items'
        ]
        read_only_fields = ['id', 'order_date']

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.CharField(write_only=True, source='product.pid')
    
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_id', 'date']
        read_only_fields = ['id', 'date']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'address', 'status']
        read_only_fields = ['id', 'user']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone']
        read_only_fields = ['id']