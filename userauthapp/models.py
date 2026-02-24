from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.contrib.auth.hashers import make_password

# Create your models here.
# class User(AbstractUser):
#     email = models.EmailField(unique=True)
#     username = models.CharField(max_length=10)
#     bio = models.CharField(max_length=100)
#     user_address = models.CharField(max_length=100, null=True, blank=True)
#     phone = models.CharField(max_length=20, null=True, blank=True)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

#     def __str__(self):
#         return self.email

#
class User(AbstractUser):
    name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=10)
    password = models.CharField(max_length=128)
    bio = models.CharField(max_length=100)
    address = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    postalcode = models.CharField(max_length=20, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    account_status = models.CharField(max_length=20, blank=True, null=True, choices=[('active', 'Active'), ('inactive', 'Inactive')])
    role = models.CharField(max_length=20, blank=True, null=True, 
                            choices=[
                                ('customer', 'Customer'), 
                                ('admin', 'Admin'), 
                                ('super admin', 'Super Admin'),
                                ('vendor', 'Vendor'), 
                                ('delivery', 'Delivery'), 
                                ('support', 'Support'),
                                ('manager', 'Manager'),
                                ('staff', 'Staff'),
                                ('superadmin', 'Super Admin'),
                                ('manager', 'Manager'),
                                ('supplier', 'Supplier'),
                                ])
    social_links = models.JSONField(null=True, blank=True)
    additional_info = models.JSONField(null=True, blank=True)
    department = models.CharField(max_length=50, null=True, blank=True, choices=[
        ('sales', 'Sales'),
        ('marketing', 'Marketing'),
        ('engineering', 'Engineering'),
        ('hr', 'Human Resources'),
        ('finance', 'Finance'),
        ('operations', 'Operations'),
        ('customer_support', 'Customer Support'),
        ('it', 'IT'),
        ('legal', 'Legal'),
        ('product_management', 'Product Management'),

    ])
    designation = models.CharField(max_length=50, null=True, blank=True, choices = [
        ('manager', 'Manager'),
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('analyst', 'Analyst'),
        ('consultant', 'Consultant'),
        ('intern', 'Intern'),
        ('ceo', 'CEO'),
        ('cto', 'CTO'),
        ('cfo', 'CFO'),
        ('coo', 'COO'), 
        ('cmo', 'CMO'),
        ('hr_manager', 'HR Manager'),
        ('sales_representative', 'Sales Representative'),
        ('customer_support_agent', 'Customer Support Agent'),
        ('data_scientist', 'Data Scientist'),
        ('product_manager', 'Product Manager'),

    ])
    last_login = models.DateTimeField(null=True, blank=True)
    last_device = models.CharField(max_length=100, null=True, blank=True)
    last_ip = models.GenericIPAddressField(null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True, choices=[
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('TaKa', 'TK'),
    ])
    domain_user_id=models.ForeignKey('self',on_delete=models.CASCADE,blank=True,null=True,related_name='domain_user_id_user')
    domain_name = models.CharField(max_length=100, null=True, blank=True)
    plan_type = models.CharField(max_length=20, null=True, blank=True, choices=[
        ('free', 'Free'),
        ('basic', 'Basic'), 
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ])

    dob = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
    def defaultkey():
        return 'username'
    
    def save(self, *args, **kwargs):
        if not self.domain_user_id and self.id:
            self.domain_user_id=User.objects.get(id=self.id)

        # Remove custom password hashing - Django's AbstractUser handles this correctly
        # via set_password() and create_user() methods
        super().save(*args, **kwargs)

class Modules(models.Model):
    id=models.AutoField(primary_key=True)
    module_name=models.CharField(max_length=50,unique=True)
    module_icon=models.CharField(null=True,blank=True,max_length=50)
    is_menu=models.BooleanField(default=True)
    is_active=models.BooleanField(default=True)
    module_url=models.CharField(null=True,blank=True,max_length=50)
    parent_id=models.ForeignKey('self',on_delete=models.CASCADE,blank=True,null=True)
    display_order=models.IntegerField(default=0)
    module_description=models.CharField(null=True,blank=True,max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.module_name   

class ModuleUrls(models.Model):
    id=models.AutoField(primary_key=True)
    module=models.ForeignKey(Modules,on_delete=models.CASCADE,blank=True,null=True)
    url=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class UserPermissions(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions')
    module = models.ForeignKey(Modules, on_delete=models.CASCADE, related_name='permissions')
    can_view = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    domain_user_id = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.module.name}"

class UserhippingAddress(models.Model):
    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    address_type = models.CharField(max_length=20, choices=[('home', 'Home'), ('work', 'Work'), ('other', 'Other')], default='home')
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.country}"
    
class ActivityLog(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_info = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.action} at {self.timestamp}" 
    
    
