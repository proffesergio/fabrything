from rest_framework import serializers
from fabrythingapp.models import (
    Cart, CartItem, OrderNotification, OrderStatus, Product, Category, Brand, ProductReview, 
    CartOrder, CartOrderItems, ShippingMethod, UserPreferences, Wishlist, Address, ProductImages
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

# class CartOrderItemsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CartOrderItems
#         fields = [
#             'id', 'order', 'invoice', 'product_status',
#             'item', 'image', 'quantity', 'price', 'total'
#         ]
#         read_only_fields = ['id', 'invoice', 'total']

# class CartOrderSerializer(serializers.ModelSerializer):
#     items = CartOrderItemsSerializer(
#         source='cartorderitems_set',
#         many=True,
#         read_only=True
#     )
#     user_email = serializers.EmailField(source='user.email', read_only=True)
    
#     class Meta:
#         model = CartOrder
#         fields = [
#             'id', 'user', 'user_email', 'price', 'paid_status',
#             'order_date', 'product_status', 'items'
#         ]
#         read_only_fields = ['id', 'order_date']

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.CharField(write_only=True, source='product.pid')
    
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_id', 'date']
        read_only_fields = ['id', 'date']

# class AddressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Address
#         fields = ['id', 'user', 'address', 'status']
#         read_only_fields = ['id', 'user']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone']
        read_only_fields = ['id']

# ============================================================================
# RECOMMENDATION SERIALIZERS
# ============================================================================
# These serializers are optimized for recommendation API responses
# Returning minimal data for fast rendering

class RecommendationProductSerializer(serializers.ModelSerializer):
    """
    Minimal product serializer for recommendation cards.
    
    Optimized for performance:
    - Only essential fields needed for display
    - No heavy relationships
    - Includes discount percentage for deal display
    
    Example response:
    {
        "pid": "prod123",
        "title": "Blue Cotton T-Shirt",
        "price": "29.99",
        "old_price": "49.99",
        "discount_percent": 40,
        "image": "https://cdn.example.com/products/blue-tshirt.jpg",
        "average_rating": 4.5,
        "review_count": 12,
        "in_stock": true
    }
    """
    average_rating = serializers.SerializerMethodField(read_only=True)
    review_count = serializers.SerializerMethodField(read_only=True)
    discount_percent = serializers.SerializerMethodField(read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)
    brand_title = serializers.CharField(source='brand.title', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'pid',
            'title',
            'image',
            'price',
            'old_price',
            'discount_percent',
            'average_rating',
            'review_count',
            'category_title',
            'brand_title',
            'in_stock',
            'featured'
        ]
        read_only_fields = fields
    
    def get_average_rating(self, obj):
        """Calculate average rating from reviews"""
        reviews = obj.reviews.all()
        if reviews.exists():
            total = sum(r.rating for r in reviews)
            return round(total / reviews.count(), 1)
        return 0
    
    def get_review_count(self, obj):
        """Get count of reviews"""
        return obj.reviews.count()
    
    def get_discount_percent(self, obj):
        """Calculate discount percentage"""
        if obj.old_price and obj.old_price > 0:
            percent = ((obj.old_price - obj.price) / obj.old_price) * 100
            return int(percent)
        return 0


class RecommendationListSerializer(serializers.Serializer):
    """
    Container for list of recommendations with metadata.
    
    Includes cache information and user segment for personalized messaging.
    """
    products = RecommendationProductSerializer(many=True, read_only=True)
    user_segment = serializers.CharField(read_only=True, allow_null=True)
    total_count = serializers.IntegerField(read_only=True)
    cached = serializers.BooleanField(read_only=True)
    cache_expires_in_minutes = serializers.IntegerField(read_only=True, allow_null=True)


class UserPreferencesSerializer(serializers.ModelSerializer):
    """
    User preferences for personalized recommendations.
    
    Allows users to set favorite categories, brands, and price range.
    
    Example:
    {
        "preferred_categories": [1, 3, 5],
        "preferred_brands": [2, 4],
        "min_price": "10.00",
        "max_price": "100.00"
    }
    """
    preferred_categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        required=False,
        help_text="IDs of favorite categories"
    )
    preferred_brands = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Brand.objects.all(),
        required=False,
        help_text="IDs of favorite brands"
    )
    preferred_categories_data = serializers.SerializerMethodField(read_only=True)
    preferred_brands_data = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = UserPreferences
        fields = [
            'preferred_categories',
            'preferred_categories_data',
            'preferred_brands',
            'preferred_brands_data',
            'min_price',
            'max_price'
        ]
    
    def get_preferred_categories_data(self, obj):
        """Include category data for display"""
        return CategorySerializer(
            obj.preferred_categories.all(),
            many=True
        ).data
    
    def get_preferred_brands_data(self, obj):
        """Include brand data for display"""
        return BrandSerializer(
            obj.preferred_brands.all(),
            many=True
        ).data


class ProductFilterFacetsSerializer(serializers.Serializer):
    """
    Available filter options with counts (for frontend filter UI).
    
    Helps frontend build filter facets for product discovery.
    
    Example response:
    {
        "categories": [
            {"cid": "cat1", "title": "Men's Fashion", "product_count": 45},
            {"cid": "cat2", "title": "Women's Fashion", "product_count": 67}
        ],
        "brands": [
            {"bid": "br1", "title": "Nike", "product_count": 12}
        ],
        "price_ranges": [
            {"min": 0, "max": 50, "count": 30},
            {"min": 50, "max": 100, "count": 45},
            {"min": 100, "max": 500, "count": 89}
        ]
    }
    """
    categories = serializers.SerializerMethodField()
    brands = serializers.SerializerMethodField()
    price_ranges = serializers.SerializerMethodField()
    
    def get_categories(self, obj):
        """Get categories with product counts"""
        from django.db.models import Count
        categories = Category.objects.annotate(
            product_count=Count('category')
        ).values('cid', 'title', 'product_count')
        return list(categories)
    
    def get_brands(self, obj):
        """Get brands with product counts"""
        from django.db.models import Count
        brands = Brand.objects.annotate(
            product_count=Count('brand')
        ).values('bid', 'title', 'product_count')
        return list(brands)
    
    def get_price_ranges(self, obj):
        """Get price range buckets with counts"""
        from django.db.models import Count
        ranges = [
            (0, 50),
            (50, 100),
            (100, 250),
            (250, 500),
            (500, 5000),
        ]
        result = []
        for min_p, max_p in ranges:
            count = Product.objects.filter(
                price__gte=min_p,
                price__lt=max_p,
                status=True,
                product_status='published'
            ).count()
            result.append({
                'min': min_p,
                'max': max_p,
                'count': count
            })
        return result
    
# ============================================================================
#
# ============================================================================
# ============================================================================
# CART & CHECKOUT SERIALIZERS  
# ============================================================================

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart items"""
    product_title = serializers.CharField(
        source='product.title',
        read_only=True
    )
    product_image = serializers.CharField(
        source='product.image',
        read_only=True
    )
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'product_title',
            'product_image',
            'product_price',
            'size',
            'color',
            'quantity',
            'total_price',
        ]
    
    def get_total_price(self, obj):
        return str(obj.total_price)

class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart with items"""
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'subtotal', 'item_count', 'updated_at']
    
    def get_subtotal(self, obj):
        return str(obj.subtotal)
    
    def get_item_count(self, obj):
        return obj.item_count

class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for shipping methods with cost and delivery time"""
    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'cost', 'delivery_days', 'description', 'is_active']
        read_only_fields = ['id']

class AddressSerializer(serializers.ModelSerializer):
    """Complete address serializer for checkout and user profile"""
    country_display = serializers.CharField(source='country', read_only=True)
    
    class Meta:
        model = Address
        fields = [
            'id', 'address_type', 'full_name', 'phone_number',
            'address', 'city', 'state', 'postal_code', 'country',
            'is_default', 'created_at', 'get_full_address'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not value or len(value) < 10:
            raise serializers.ValidationError("Invalid phone number")
        return value
    
    def validate_postal_code(self, value):
        """Validate postal code"""
        if not value or len(value) < 3:
            raise serializers.ValidationError("Invalid postal code")
        return value

class CartOrderItemsSerializer(serializers.ModelSerializer):
    """Individual cart/order items"""
    product_pid = serializers.CharField(source='product.pid', read_only=True)
    product_title = serializers.CharField(source='item', read_only=True)
    
    class Meta:
        model = CartOrderItems
        fields = [
            'id', 'product_pid', 'product_title', 'image',
            'size', 'color', 'quantity', 'price', 'total', 'created_at'
        ]
        read_only_fields = ['id', 'total', 'created_at']

class CartOrderSerializer(serializers.ModelSerializer):
    """
    Complete cart/order serializer with all details.
    Used for cart page and order confirmation.
    """
    items = CartOrderItemsSerializer(many=True, read_only=True)
    shipping_method_details = ShippingMethodSerializer(
        source='shipping_method',
        read_only=True
    )
    shipping_address_details = AddressSerializer(
        source='shipping_address',
        read_only=True
    )
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    product_status_display = serializers.CharField(
        source='get_product_status_display',
        read_only=True
    )
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = CartOrder
        fields = [
            'id', 'user', 'user_email', 'items',
            'subtotal', 'shipping_cost', 'discount_applied', 'taxes', 'price',
            'payment_method', 'payment_method_display',
            'shipping_method', 'shipping_method_details',
            'shipping_address', 'shipping_address_details',
            'coupon_code', 'notes',
            'product_status', 'product_status_display',
            'paid_status', 'order_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'subtotal', 'taxes', 'order_date',
            'created_at', 'updated_at'
        ]

class OrderStatusSerializer(serializers.ModelSerializer):
    """Order status history entry"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = OrderStatus
        fields = ['id', 'status', 'status_display', 'tracking_number', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

class OrderNotificationSerializer(serializers.ModelSerializer):
    """Notification tracking"""
    notification_type_display = serializers.CharField(
        source='get_notification_type_display',
        read_only=True
    )
    
    class Meta:
        model = OrderNotification
        fields = [
            'id', 'notification_type', 'notification_type_display',
            'subject', 'message', 'sent_at', 'is_read'
        ]
        read_only_fields = ['id', 'sent_at']

class CheckoutSerializer(serializers.Serializer):
    """
    Serializer for checkout data (not a model).
    Combines order data with user selections.
    """
    # Existing cart data
    cart_id = serializers.IntegerField()
    
    # Address selection
    shipping_address_id = serializers.IntegerField(required=True)
    
    # Shipping method
    shipping_method_id = serializers.IntegerField(required=True)
    
    # Payment
    payment_method = serializers.ChoiceField(
        choices=[
            ('cod', 'Cash on Delivery'),
            ('bkash', 'bKash'),
            ('nagad', 'Nagad'),
            ('rocket', 'Rocket'),
            ('visa', 'Visa Card'),
            ('mastercard', 'MasterCard'),
        ]
    )
    
    # Optional
    coupon_code = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )
    
    def validate_shipping_address_id(self, value):
        """Verify address belongs to user"""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("User not authenticated")
        
        try:
            Address.objects.get(id=value, user=request.user)
        except Address.DoesNotExist:
            raise serializers.ValidationError("Invalid address")
        
        return value
    
    def validate_shipping_method_id(self, value):
        """Verify shipping method exists and is active"""
        try:
            method = ShippingMethod.objects.get(id=value, is_active=True)
        except ShippingMethod.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive shipping method")
        
        return value

class OrderConfirmationSerializer(serializers.ModelSerializer):

    """Minimal serializer for order confirmation page"""
    items = CartOrderItemsSerializer(many=True, read_only=True)
    shipping_address_details = AddressSerializer(
        source='shipping_address',
        read_only=True
    )
    
    class Meta:
        model = CartOrder
        fields = [
            'id', 'items', 'price', 'payment_method',
            'shipping_address_details', 'order_date',
            'created_at'
        ]
        read_only_fields = fields

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for items in an order"""
    class Meta:
        model = CartOrderItems
        fields = [
            'id',
            'product_name',
            'product_price',
            'size',
            'color',
            'quantity',
            'subtotal',
        ]

class OrderDetailSerializer(serializers.ModelSerializer):
    """Detailed order serializer with items and status history"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    order_status_display = serializers.CharField(
        source='get_order_status_display',
        read_only=True
    )
    
    class Meta:
        model = CartOrder
        fields = [
            'id',
            'order_id',
            'user',
            'items',
            'subtotal',
            'discount_amount',
            'shipping_cost',
            'tax_amount',
            'total_price',
            'shipping_address',
            'payment_method',
            'payment_method_display',
            'order_status',
            'order_status_display',
            'status_history',
            'coupon_code',
            'notes',
            'paid_status',
            'created_at',
            'updated_at',
        ]

class OrderListSerializer(serializers.ModelSerializer):
    """Summary order serializer for lists"""
    items_count = serializers.SerializerMethodField()
    order_status_display = serializers.CharField(
        source='get_order_status_display',
        read_only=True
    )
    
    class Meta:
        model = CartOrder
        fields = [
            'id',
            'order_id',
            'total_price',
            'items_count',
            'order_status',
            'order_status_display',
            'created_at',
        ]
    
    def get_items_count(self, obj):
        return sum(item.quantity for item in obj.items.all())

class CheckoutFormSerializer(serializers.Serializer):
    """Validator for checkout form"""
    shipping_address_id = serializers.IntegerField(required=True)
    shipping_method_id = serializers.IntegerField(required=True)
    payment_method = serializers.ChoiceField(
        choices=['cod', 'bkash', 'nagad', 'rocket', 'visa', 'mastercard', 'stripe']
    )
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)