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
    stock_count = models.CharField(max_length=100, default="10", null=True, blank=True)
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
    
class ProductImages(models.Model):
    images = models.ImageField(upload_to="product_images", default="product.jpg")
    product = models.ForeignKey(Product, related_name="product_images", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "ProductImages"

# Cart, Order, OrderItems, Address
class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9999999999, decimal_places=2, default="1.99")
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")

    class Meta:
        verbose_name_plural = "Cart Orders"
        indexes = [
            models.Index(fields=['user', 'paid_status']),  # For user order history
            models.Index(fields=['-order_date']),          # For recent orders
        ]


class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)

    invoice = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=9999999999, decimal_places=2, default="1.99")
    total = models.DecimalField(max_digits=9999999999, decimal_places=2, default="1.99")

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_image(self):
        return mark_safe('<img src="/media/%s" width="500" height="500" />' %(self.image))

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

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Addresses"

    def get_address (self):
        return self.address 
    
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