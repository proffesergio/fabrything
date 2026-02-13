import random
from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauthapp.models import User
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field


# creating tuples
STATUS_CHOICE = (
    ("process", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered")
)
STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)

RATING = (
    (1, "★☆☆☆☆"),
    (2, "★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),
)

# RATING = (
#     ('1', "★☆☆☆☆"),
#     ('2', "★★☆☆☆"),
#     ('3', "★★★☆☆"),
#     ('4', "★★★★☆"),
#     ('5', "★★★★★"),
# )

SIZES = (
    ('S', "Small"),
    ('M', "Medium"),
    ('L', "Large"),
    ('XL', "Extra Large"),
    ('XXL', "Extra X Large"),
    ('XXXL', "Extra XX Large"),
)

def user_directory_path(instance, filename):
    return 'user_{0}/{0}'.format(instance.user.id)

# Create your models here.
class Brand(models.Model):
    bid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="br")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="brands")


    class Meta:
        verbose_name_plural = "Brands"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
    
class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category")


    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
    
class Tags(models.Model):
    pass
    
class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="vend")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to=user_directory_path)
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=100, default="Vendor Address Goes Here")
    contact = models.CharField(max_length=100, default="Phone Number")
    chat_resp_time = models.CharField(max_length=100, default="100")
    shipping_on_time = models.CharField(max_length=100, default="100")
    authentic_rating = models.CharField(max_length=100, default="100")
    days_return = models.CharField(max_length=100, default="100")
    warranty_period = models.CharField(max_length=100, default="100")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Vendors"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
    
class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="prod", alphabet="0123456789abcd")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="products")
    description = CKEditor5Field('Text', config_name='extended', null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='category')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name='brand', blank=True)
    # Vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)

    price = models.DecimalField(max_digits=999999999999, decimal_places=2, default="1.00")
    old_price = models.DecimalField(max_digits=999999999999, decimal_places=2, default="0.00")

    specs = CKEditor5Field(null=True, blank=True)
    type = models.CharField(max_length=100, default="100% Cotton", null=True, blank=True)
    stock_count = models.IntegerField(default=10, help_text="Total units in stock")  # FIXED: Changed from CharField to IntegerField
    sizes = models.CharField(choices=SIZES, max_length=10, default="L", null=True, blank=True)
    # tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True)
    # rating = models.CharField(choices=RATING, max_length=100, default=None, null=True, blank=True)
    product_status = models.CharField(choices=STATUS, max_length=10, default="in_review")
    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    # digital = models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True, length=10, max_length=20, prefix="vend", alphabet="1234567890")
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    tags = TaggableManager(blank=True)

    class Meta:
        verbose_name_plural = "Products"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),           # For sorting by newest first
            models.Index(fields=['category']),       # For category filtering
            models.Index(fields=['brand']),          # For brand filtering
            models.Index(fields=['price']),          # For price range filtering
            models.Index(fields=['featured']),       # For featured products query
            models.Index(fields=['status']),         # For active products filter
            models.Index(fields=['-date', 'status']),  # Composite for homepage queries
        ]

    def product_image(self):
        return mark_safe('<img src="%s" width="500" height="500" />' %(self.image.url))
    
    def __str__(self):
        return self.title
    
    def get_discount(self):
        saved_amount = (self.old_price - self.price)
        return saved_amount
    
    def get_price(self):
        return self.price
    
    def get_average_rating(self):
        """Calculate average rating from product reviews"""
        reviews = self.reviews.all()
        if reviews.exists():
            avg_rating = sum([r.rating for r in reviews]) / reviews.count()
            return round(avg_rating, 1)
        return 0
    
    def get_rating_count(self):
        """Get total number of reviews"""
        return self.reviews.count()
    
    def is_in_stock(self):
        """Check if product has stock available"""
        return self.stock_count > 0 and self.in_stock and self.status
    
class ProductImages(models.Model):
    images = models.ImageField(upload_to="product_images", default="product.jpg")
    product = models.ForeignKey(Product, related_name="product_images", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "ProductImages"

# Cart, Order, OrderItems, Address

class CartOrder(models.Model):
    """
    Shopping order/invoice model.
    
    Represents a complete order from checkout to delivery.
    """
    PAYMENT_METHOD_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
        ('visa', 'Visa Card'),
        ('mastercard', 'MasterCard'),
        ('amex', 'American Express'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="Customer who placed order"
    )
    
    # Payment & Pricing
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Subtotal before tax/shipping"
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Shipping cost"
    )
    discount_applied = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Discount from coupon"
    )
    taxes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Tax amount"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Final total price"
    )
    
    # Order Status
    paid_status = models.BooleanField(
        default=False,
        help_text="Whether payment is received"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cod',
        help_text="Payment method used"
    )
    product_status = models.CharField(
        choices=STATUS_CHOICE,
        max_length=30,
        default="processing",
        help_text="Overall order status"
    )
    
    # Shipping
    shipping_method = models.ForeignKey(
        'ShippingMethod',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        help_text="Shipping method selected"
    )
    shipping_address = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        help_text="Shipping address"
    )
    
    # Additional Info
    coupon_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Coupon code if applied"
    )
    notes = models.TextField(
        blank=True,
        help_text="Order notes from customer"
    )
    
    # Timestamps
    order_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When order was placed"
    )
    created_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When order was created"
    )
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last update time"
    )

    class Meta:
        verbose_name_plural = "Cart Orders"
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['user', 'paid_status']),
            models.Index(fields=['-order_date']),
            models.Index(fields=['payment_method']),
        ]
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"
    
    def get_status_display_full(self):
        """Get full status with timestamp"""
        latest_status = self.status_history.first()
        if latest_status:
            return f"{latest_status.get_status_display()} ({latest_status.created_at.strftime('%Y-%m-%d')})"
        return "No status"

    def save(self, *args, **kwargs):
        # Generate order ID if not exists
        if not self.order_id:
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            user_id = self.user.id
            rand_num = random.randint(100, 999)
            self.order_id = f"ORD-{date_str}-{user_id}-{rand_num}"
        
        super().save(*args, **kwargs)

class CartOrderItems(models.Model):
    """
    Individual items in a cart/order.
    
    Stores product details at time of purchase
    (important for historical tracking).
    """
    order = models.ForeignKey(
        CartOrder,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Associated order"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
        help_text="Product ordered"
    )
    
    invoice = models.CharField(
        max_length=200,
        help_text="Invoice/line item number"
    )
    product_status = models.CharField(
        max_length=200,
        help_text="Status of this item"
    )
    
    # Product info (snapshot at purchase time)
    item = models.CharField(
        max_length=200,
        help_text="Product title (snapshot)"
    )
    image = models.CharField(
        max_length=200,
        help_text="Product image URL (snapshot)"
    )
    
    # Sizing & Color
    size = models.CharField(
        max_length=10,
        blank=True,
        help_text="Selected size"
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Selected color"
    )
    
    # Quantity & Pricing
    quantity = models.IntegerField(
        default=1,
        help_text="Quantity ordered"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Price per unit at purchase"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total for this line item"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When item was added to order"
    )

    class Meta:
        verbose_name_plural = "Cart Order Items"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.item} x{self.quantity}"
    
    def order_image(self):
        """Display product image in admin"""
        return mark_safe(f'<img src="{self.image}" width="100" height="100" />')

# Product Review, Wishlist, Address 
class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='reviews')
    review_heading = models.TextField(blank=True, null=True, default='Thanks to Fabrything for this amazing item!')
    review = models.TextField(default=None)
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "ProductReviews"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['product']),        # For product reviews query
            models.Index(fields=['rating']),         # For rating filtering
            models.Index(fields=['user']),           # For user review history
            models.Index(fields=['-date']),          # For recent reviews
            models.Index(fields=['product', 'rating']),  # Composite for avg rating
        ]

    def __str__(self):
        return self.product.title
    
    def get_rating(self):
        return self.rating
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return self.product.title
    
    def get_product_rating(self):
        """Get average rating of the product in this wishlist"""
        reviews = self.product.reviews.all()
        if reviews.exists():
            avg_rating = sum([r.rating for r in reviews]) / reviews.count()
            return round(avg_rating, 1)
        return 0

# ... existing code ...    

class Address(models.Model):
    """
    User delivery addresses.
    
    Supports multiple addresses per user (home, work, etc).
    Used during checkout for shipping destination.
    """
    ADDRESS_TYPE_CHOICES = (
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        help_text="User who owns this address"
    )
    
    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPE_CHOICES,
        default='home',
        help_text="Type of address"
    )
    
    full_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Recipient name"
    )
    
    phone_number = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        help_text="Phone number for delivery"
    )
    
    address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Street address"
    )
    
    city = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="City"
    )
    
    state = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="State/Province"
    )
    
    postal_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Postal/ZIP code"
    )
    
    country = models.CharField(
        max_length=50,
        default='Bangladesh',
        help_text="Country"
    )
    
    is_default = models.BooleanField(
        default=False,
        help_text="Set as default shipping address"
    )
    
    status = models.BooleanField(
        default=True,
        help_text="Active/inactive"
    )
    
    created_at = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text="When address was created"
    )
    
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text="Last update time"
    )

    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.full_name}, {self.city} ({self.get_address_type_display()})"
    
    def get_full_address(self):
        """Format complete address"""
        return f"{self.address}, {self.city}, {self.state} {self.postal_code}, {self.country}"
    
    def get_address(self):
        """Legacy method compatibility"""
        return self.get_full_address() 
    
    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            Address.objects.filter(user=self.user).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
# ============================================================================
# ANALYTICS & RECOMMENDATIONS MODELS
# ============================================================================
# These models support the recommendation engine and user segmentation
# See: fabrythingapp/services/analytics_service.py for usage

class ProductView(models.Model):
    """
    Tracks every time a user views a product.
    
    Used for:
    - Calculating product popularity scores
    - Understanding user browsing behavior
    - Identifying trending products
    
    Example:
        User views "Blue T-Shirt" product → ProductView record created
        Later: ProductView.objects.filter(product=t_shirt).count() → popularity metric
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='product_views',
        help_text="User who viewed the product"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='views',
        help_text="Product that was viewed"
    )
    viewed_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,  # Index for efficient time-range queries
        help_text="Timestamp of the view"
    )
    
    class Meta:
        verbose_name = "Product View"
        verbose_name_plural = "Product Views"
        indexes = [
            models.Index(fields=['product', 'viewed_at']),  # For trending queries
            models.Index(fields=['user', 'viewed_at']),      # For user view history
        ]
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f"{self.user.email} viewed {self.product.title} at {self.viewed_at}"


class UserPreferences(models.Model):
    """
    Stores explicit user preferences for personalized recommendations.
    
    Used for:
    - Storing user's favorite categories and brands
    - Adjusting recommendation algorithm based on preferences
    - Understanding user taste profile
    
    Example:
        User browses "Women's Fashion" & "Shoes" → These preferred categories stored
        Recommendations pulled from these categories first
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferences',
        help_text="User who owns these preferences"
    )
    preferred_categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='preference_users',
        help_text="Categories user is interested in"
    )
    preferred_brands = models.ManyToManyField(
        Brand,
        blank=True,
        related_name='preference_users',
        help_text="Brands user prefers"
    )
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="User's minimum preferred price"
    )
    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="User's maximum preferred price"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Preference"
        verbose_name_plural = "User Preferences"
    
    def __str__(self):
        return f"Preferences for {self.user.email}"


class RecommendationCache(models.Model):
    """
    Caches pre-computed recommendations to avoid expensive recalculation.
    
    Why needed:
    - Computing recommendations queries 10+ database tables
    - Without cache: generating recommendations takes 500-2000ms
    - With cache: retrieving recommendations takes <50ms
    
    TTL Strategy (Time-To-Live):
    - Popular products: 24 hours (stable, changes slowly)
    - Trending products: 6 hours (changes daily)
    - Personalized recommendations: 3 hours (user behavior evolves)
    
    Example:
        First request: Generate recommendations for user (slow, 1 second)
        Store in RecommendationCache with 3 hour TTL
        Next 10 requests: Retrieved from cache (fast, <50ms)
        After 3 hours: Cache expires, regenerated on next request
    """
    CACHE_TYPE_CHOICES = (
        ('popular', 'Popular Products'),
        ('trending', 'Trending Products'),
        ('personalized', 'Personalized Recommendations'),
        ('similar', 'Similar Products'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='recommendation_caches',
        help_text="User these recommendations are for (null = global cache)"
    )
    cache_type = models.CharField(
        max_length=20,
        choices=CACHE_TYPE_CHOICES,
        db_index=True,
        help_text="Type of recommendation being cached"
    )
    cache_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Unique identifier for this cache entry"
    )
    recommendations_data = models.JSONField(
        help_text="List of product PIDs in recommendation order"
    )
    generated_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When these recommendations were generated"
    )
    expires_at = models.DateTimeField(
        db_index=True,
        help_text="When this cache entry expires"
    )
    hit_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this cache was accessed"
    )
    
    class Meta:
        verbose_name = "Recommendation Cache"
        verbose_name_plural = "Recommendation Caches"
        indexes = [
            models.Index(fields=['cache_key', 'expires_at']),
            models.Index(fields=['user', 'cache_type']),
        ]
    
    def __str__(self):
        return f"{self.get_cache_type_display()} - {self.cache_key}"
    
    def is_expired(self):
        """Check if cache entry has expired"""
        from django.utils import timezone
        return timezone.now() > self.expires_at


# ============================================================================
# TIER 1: SHOPPING & ORDER MANAGEMENT MODELS
# ============================================================================

# class ShippingMethod(models.Model):
#     """
#     Shipping methods with costs and delivery estimates.
    
#     Used for:
#     - Displaying shipping options during checkout
#     - Calculating shipping cost
#     - Setting delivery expectations
    
#     Example:
#         Standard: $5, 3-5 days
#         Express: $15, 1-2 days
#     """
#     name = models.CharField(
#         max_length=50,
#         unique=True,
#         help_text="E.g., Standard, Express, Overnight"
#     )
#     description = models.CharField(
#         max_length=200,
#         blank=True,
#         help_text="User-facing description"
#     )
#     cost = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         help_text="Shipping cost"
#     )
#     delivery_days = models.IntegerField(
#         help_text="Expected delivery days (e.g., 3 for 3-5 days)"
#     )
#     max_delivery_days = models.IntegerField(
#         default=1,
#         help_text="Maximum delivery days"
#     )
#     is_active = models.BooleanField(
#         default=True,
#         help_text="Enable/disable this shipping option"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         verbose_name = "Shipping Method"
#         verbose_name_plural = "Shipping Methods"
#         ordering = ['delivery_days', 'cost']
    
#     def __str__(self):
#         return f"{self.name} (${self.cost}, {self.delivery_days} days)"


class OrderStatus(models.Model):
    """
    Order status tracking with timestamps.
    
    Allows tracking order progress through stages:
    Pending → Processing → Shipped → Out for Delivery → Delivered
    
    Used for:
    - Real-time order tracking
    - Customer notifications
    - Admin order management
    - Analytics
    """
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    )
    
    order = models.ForeignKey(
        'CartOrder',
        on_delete=models.CASCADE,
        related_name='status_history',
        help_text="Associated order"
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        help_text="Current order status"
    )
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        help_text="Carrier tracking number (optional)"
    )
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this status"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When this status was set"
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Order Status"
        verbose_name_plural = "Order Statuses"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.order.id} - {self.get_status_display()}"


# class OrderNotification(models.Model):
#     """
#     Track notifications sent to customers.
    
#     Notifications about:
#     - Order confirmation
#     - Status updates
#     - Delivery notifications
#     - Return confirmations
#     """
#     NOTIFICATION_TYPE_CHOICES = (
#         ('email', 'Email'),
#         ('sms', 'SMS'),
#         ('push', 'Push Notification'),
#         ('in_app', 'In-App'),
#     )
    
#     order = models.ForeignKey(
#         'CartOrder',
#         on_delete=models.CASCADE,
#         related_name='notifications',
#         help_text="Associated order"
#     )
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='order_notifications',
#         help_text="Recipient user"
#     )
#     notification_type = models.CharField(
#         max_length=20,
#         choices=NOTIFICATION_TYPE_CHOICES,
#         help_text="Type of notification"
#     )
#     subject = models.CharField(
#         max_length=200,
#         help_text="Notification subject/title"
#     )
#     message = models.TextField(
#         help_text="Notification message content"
#     )
#     sent_at = models.DateTimeField(
#         auto_now_add=True,
#         help_text="When notification was sent"
#     )
#     is_read = models.BooleanField(
#         default=False,
#         help_text="Whether user has read notification"
#     )
    
#     class Meta:
#         verbose_name = "Order Notification"
#         verbose_name_plural = "Order Notifications"
#         ordering = ['-sent_at']
#         indexes = [
#             models.Index(fields=['user', '-sent_at']),
#             models.Index(fields=['order', '-sent_at']),
#         ]
    
#     def __str__(self):
#         return f"{self.notification_type.upper()}: {self.subject}"


# Enhance CartOrder model with migration
# Add these fields to CartOrder model via migration:
# - shipping_method (FK to ShippingMethod)
# - payment_method (CharField with choices)
# - shipping_address (FK to Address)
# - notes (TextField)
# - discount_applied (DecimalField)
# - taxes (DecimalField)
# - created_at (DateTimeField)
# - updated_at (DateTimeField)
# - coupon_code (CharField, optional)
# Add these at the end of the file (after all existing models):

# ============================================================================
# CART & ORDER MODELS (TIER 1)
# ============================================================================

class ShippingMethod(models.Model):
    """
    Shipping options available to customers.
    
    Examples:
    - Standard Shipping: $5, 5-7 days
    - Express Shipping: $15, 2-3 days
    - Same-day Delivery: $25, same day
    """
    name = models.CharField(
        max_length=100,
        help_text="Display name (Standard, Express, etc)"
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Shipping cost in BDT"
    )
    delivery_days = models.IntegerField(
        help_text="Estimated delivery days"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of shipping method"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this shipping method available?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['cost']
        verbose_name = 'Shipping Method'
        verbose_name_plural = 'Shipping Methods'
    
    def __str__(self):
        return f"{self.name} - ৳{self.cost} ({self.delivery_days} days)"


# class OrderStatus(models.Model):
#     """
#     Track order status changes over time.
    
#     Timeline:
#     Pending → Processing → Shipped → Out for Delivery → Delivered
#     Or: Pending → Cancelled
#     """
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('confirmed', 'Confirmed'),
#         ('processing', 'Processing'),
#         ('packed', 'Packed'),
#         ('shipped', 'Shipped'),
#         ('out_for_delivery', 'Out for Delivery'),
#         ('delivered', 'Delivered'),
#         ('cancelled', 'Cancelled'),
#         ('returned', 'Returned'),
#     ]
    
#     order = models.ForeignKey(
#         'CartOrder',
#         on_delete=models.CASCADE,
#         related_name='status_history'
#     )
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='pending'
#     )
#     status_date = models.DateTimeField(auto_now_add=True)
#     tracking_number = models.CharField(
#         max_length=100,
#         blank=True,
#         help_text="Courier tracking number"
#     )
#     notes = models.TextField(
#         blank=True,
#         help_text="Internal notes about status change"
#     )
#     is_notified = models.BooleanField(
#         default=False,
#         help_text="Customer has been notified"
#     )
    
#     class Meta:
#         ordering = ['-status_date']
#         verbose_name = 'Order Status'
#         verbose_name_plural = 'Order Statuses'
    
#     def __str__(self):
#         return f"{self.order.order_id} - {self.get_status_display()}"


class OrderNotification(models.Model):
    """
    Track notifications sent to customers.
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    order = models.ForeignKey(
        'CartOrder',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='order_notifications'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES
    )
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.notification_type.upper()} to {self.user.email}"


# Enhance existing CartOrder model (modify if exists)
# Add these fields to CartOrder if they don't exist

# class CartOrder(models.Model):
#     """
#     Customer orders - represents a complete purchase.
#     """
#     # Generate order ID like: ORD-2024001-001
#     order_id = models.CharField(
#         max_length=50,
#         unique=True,
#         db_index=True,
#         editable=False
#     )
    
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='orders'
#     )
    
#     # Pricing
#     subtotal = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=0,
#         help_text="Total before discount & shipping"
#     )
#     discount_amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0,
#         help_text="Discount applied (coupon, promotion)"
#     )
#     shipping_cost = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0,
#         help_text="Shipping cost"
#     )
#     tax_amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0,
#         help_text="Tax amount (VAT, etc)"
#     )
#     total_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         help_text="Final total: subtotal - discount + shipping + tax"
#     )
    
#     # Shipping & Delivery
#     shipping_method = models.ForeignKey(
#         ShippingMethod,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True
#     )
#     shipping_address = models.ForeignKey(
#         'Address',
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name='orders_shipped'
#     )
    
#     # Payment
#     payment_method = models.CharField(
#         max_length=50,
#         choices=[
#             ('cod', 'Cash on Delivery'),
#             ('bkash', 'bKash'),
#             ('nagad', 'Nagad'),
#             ('rocket', 'Rocket'),
#             ('visa', 'Visa Card'),
#             ('mastercard', 'Mastercard'),
#             ('stripe', 'Stripe'),
#         ],
#         default='cod'
#     )
#     paid_status = models.BooleanField(
#         default=False,
#         help_text="Whether payment has been received"
#     )
#     payment_date = models.DateTimeField(
#         null=True,
#         blank=True
#     )
    
#     # Status
#     order_status = models.CharField(
#         max_length=20,
#         choices=[
#             ('pending', 'Pending'),
#             ('confirmed', 'Confirmed'),
#             ('processing', 'Processing'),
#             ('packed', 'Packed'),
#             ('shipped', 'Shipped'),
#             ('out_for_delivery', 'Out for Delivery'),
#             ('delivered', 'Delivered'),
#             ('cancelled', 'Cancelled'),
#         ],
#         default='pending'
#     )
    
#     # Metadata
#     coupon_code = models.CharField(
#         max_length=50,
#         blank=True,
#         help_text="Applied coupon code"
#     )
#     notes = models.TextField(
#         blank=True,
#         help_text="Customer notes/special instructions"
#     )
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True, db_index=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = 'Order'
#         verbose_name_plural = 'Orders'
#         indexes = [
#             models.Index(fields=['user', '-created_at']),
#             models.Index(fields=['order_status']),
#             models.Index(fields=['order_id']),
#         ]
    
#     def __str__(self):
#         return f"Order {self.order_id} - {self.user.email}"
    
#     def save(self, *args, **kwargs):
#         # Generate order ID if not exists
#         if not self.order_id:
#             from django.utils import timezone
#             date_str = timezone.now().strftime('%Y%m%d')
#             count = CartOrder.objects.filter(
#                 created_at__date=timezone.now().date()
#             ).count() + 1
#             user_count = CartOrder.objects.filter(user=self.user).count() + 1
#             self.order_id = f"ORD-{date_str}-{user_count:04d}"
        
#         # Recalculate total
#         self.total_price = (
#             self.subtotal - self.discount_amount +
#             self.shipping_cost + self.tax_amount
#         )
        
#         super().save(*args, **kwargs)


# class CartOrderItems(models.Model):
#     """
#     Individual items in an order.
#     Stores product details at time of purchase (price, size, etc).
#     """
#     order = models.ForeignKey(
#         CartOrder,
#         on_delete=models.CASCADE,
#         related_name='items'
#     )
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name='order_items'
#     )
    
#     # Product details at time of purchase
#     product_name = models.CharField(max_length=255)
#     product_price = models.DecimalField(max_digits=12, decimal_places=2)
    
#     # Variant selections
#     size = models.CharField(
#         max_length=50,
#         blank=True,
#         help_text="Selected size (XS, S, M, L, XL, etc)"
#     )
#     color = models.CharField(
#         max_length=50,
#         blank=True,
#         help_text="Selected color"
#     )
    
#     # Quantity & pricing
#     quantity = models.PositiveIntegerField(default=1)
#     subtotal = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         help_text="product_price × quantity"
#     )
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['created_at']
    
#     def __str__(self):
#         return f"{self.product_name} (x{self.quantity})"
    
#     def save(self, *args, **kwargs):
#         self.subtotal = self.product_price * self.quantity
#         super().save(*args, **kwargs)


# Enhance existing Address model

# class Address(models.Model):
#     """
#     User shipping addresses - support multiple addresses per user.
#     """
#     ADDRESS_TYPES = [
#         ('home', 'Home'),
#         ('work', 'Work'),
#         ('other', 'Other'),
#     ]
    
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='addresses'
#     )
    
#     # Address info
#     full_name = models.CharField(
#         max_length=255,
#         help_text="Recipient name"
#     )
#     phone_number = models.CharField(
#         max_length=20,
#         help_text="Contact phone number"
#     )
#     address_type = models.CharField(
#         max_length=10,
#         choices=ADDRESS_TYPES,
#         default='home'
#     )
    
#     # Full address
#     street_address = models.CharField(max_length=255)
#     city = models.CharField(max_length=100)
#     state = models.CharField(max_length=100)
#     postal_code = models.CharField(max_length=20)
#     country = models.CharField(
#         max_length=100,
#         default='Bangladesh'
#     )
    
#     # Default address
#     is_default = models.BooleanField(
#         default=False,
#         help_text="Use as default shipping address"
#     )
    
#     # Status
#     is_active = models.BooleanField(default=True)
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         ordering = ['-is_default', '-created_at']
#         verbose_name_plural = 'Addresses'
    
#     def __str__(self):
#         return f"{self.full_name}, {self.city}"
    
#     def save(self, *args, **kwargs):
#         # Ensure only one default address per user
#         if self.is_default:
#             Address.objects.filter(
#                 user=self.user,
#                 is_default=True
#             ).exclude(pk=self.pk).update(is_default=False)
        
#         super().save(*args, **kwargs)


# ============================================================================
# CART MODEL (Temporary shopping cart - before checkout)
# ============================================================================

class Cart(models.Model):
    """
    Temporary shopping cart - one per user.
    Deleted when order is placed.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Carts'
    
    def __str__(self):
        return f"Cart for {self.user.email}"
    
    @property
    def subtotal(self):
        """Calculate cart subtotal"""
        return sum(
            item.total_price for item in self.items.all()
        )
    
    @property
    def item_count(self):
        """Total number of items in cart"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """
    Individual items in shopping cart.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    
    # Variant selections
    size = models.CharField(
        max_length=50,
        blank=True,
        help_text="Selected size"
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Selected color"
    )
    
    quantity = models.PositiveIntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['cart', 'product', 'size', 'color']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.title} x{self.quantity}"
    
    @property
    def total_price(self):
        """Item total: price × quantity"""
        return self.product.price * self.quantity