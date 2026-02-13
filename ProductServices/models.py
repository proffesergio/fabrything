from django.db import models

# from fabrything.UserServices.models import Users
from userauthapp.models import User
# Create your models here.
class Categories(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    parent_id = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    image_url = models.TextField(max_length=255, null=True, blank=True)
    display_order = models.IntegerField(default=0)
    domain_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    added_by_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='added_categories')


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Products(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image = models.JSONField(null=True, blank=True)  # Store multiple image URLs as a JSON array
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name='products')
    image_url = models.TextField(max_length=255, null=True, blank=True)
    stock_quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    specifications = models.JSONField(null=True, blank=True)  # Store specifications as a JSON object
    html_description = models.TextField(null=True, blank=True)
    highlighted_features = models.JSONField(null=True, blank=True)  # Store highlighted features as a JSON array
    sku = models.CharField(max_length=100, null=True, blank=True)
    initial_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    updated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField(max_length=100, null=True, blank=True)
    units_of_measure = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    material = models.CharField(max_length=100, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True, choices=[
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    ])
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    seo_keywords = models.CharField(max_length=255, null=True, blank=True)

    additional_info = models.JSONField(null=True, blank=True)  # Store any additional information as a JSON object

    domain_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    added_by_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='added_products')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class ProductQuestions(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='questions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_questions')
    question = models.TextField()
    answer = models.TextField(null=True, blank=True)
    is_answered = models.BooleanField(default=False)
    added_by_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='added_product_questions')
    asked_by_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='asked_product_questions')
    answered_by_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='answered_product_questions')

    domain_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Question by {self.user.email} on {self.product.name}"
    
class ProductReviews(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='reviews')
    images = models.JSONField(null=True, blank=True)  # Store multiple image URLs as a JSON array
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.IntegerField()
    review = models.TextField(null=True, blank=True)
    added_by_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='added_product_reviews')
    domain_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ])
    reviewed_by_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reviewed_product_reviews')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.email} on {self.product.name}"