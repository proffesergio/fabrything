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
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name='brand')
    Vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)

    price = models.DecimalField(max_digits=999999999999, decimal_places=2, default="1.00")
    old_price = models.DecimalField(max_digits=999999999999, decimal_places=2, default="0.00")

    specs = CKEditor5Field(null=True, blank=True)
    type = models.CharField(max_length=100, default="100% Cotton", null=True, blank=True)
    stock_count = models.CharField(max_length=100, default="10", null=True, blank=True)
    sizes = models.CharField(choices=SIZES, max_length=10, default="L", null=True, blank=True)
    # tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True)
    rating = models.CharField(choices=RATING, max_length=100, default=str(4), null=True, blank=True)
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
        verbose_name_plural = "Product Reviews"

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
    
    def get_rating(self):
        return self.rating
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Addresses"

    def get_address (self):
        return self.address 