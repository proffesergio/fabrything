from django.db import models

from ProductServices.models import Products
from userauthapp.models import User

# Create your models here.
class Warehouse(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    manager_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    capacity = models.IntegerField()
    additional_info = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    added_by_user_id = models.IntegerField(null=True, blank=True)
    domain_user_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pass

class RackAndShelvesAndFloors(models.Model):
    id = models.AutoField(primary_key=True)
    warehouse_id = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='rack_and_shelves_and_floors')
    name = models.CharField(max_length=100)
    rack = models.CharField(max_length=100, null=True, blank=True)
    shelf = models.CharField(max_length=100, null=True, blank=True)
    floor = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=20, choices=[('rack', 'Rack'), ('shelf', 'Shelf'), ('floor', 'Floor')])
    capacity = models.IntegerField()
    additional_info = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    added_by_user_id = models.IntegerField(null=True, blank=True)
    domain_user_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pass

class Inventory(models.Model):
    id = models.AutoField(primary_key=True)
    purchase_order_id = models.ForeignKey('OrderServices.PurchaseOrder', on_delete=models.CASCADE, related_name='inventories')
    purchase_order_item_id = models.ForeignKey('OrderServices.PurchaseOrderItems', on_delete=models.CASCADE, related_name='inventories')
    purchase_order_inwarded_item_id = models.ForeignKey('OrderServices.PurchaseOrderItemInwardedLog', on_delete=models.CASCADE, related_name='inventories')

    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='inventories')
    warehouse_id = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventories')
    rack_and_shelf_and_floor_id = models.ForeignKey(RackAndShelvesAndFloors, on_delete=models.CASCADE, related_name='inventories')
    quantity = models.IntegerField()
    mrp = models.CharField(max_length=20, null=True, blank=True)
    batch_number = models.CharField(max_length=100, null=True, blank=True)
    discount_type = models.CharField(max_length=20, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed')], null=True, blank=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sr_no = models.CharField(max_length=100, null=True, blank=True)
    mfg_date = models.DateField(null=True, blank=True)
    exp_date = models.DateField(null=True, blank=True)
    uom = models.CharField(max_length=50, null=True, blank=True)
    ptr = models.CharField(max_length=10, null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    quantity_inwarded = models.IntegerField(null=True, blank=True)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    inward_type = models.CharField(max_length=20, choices=[
        ('purchase', 'Purchase'), 
        ('return', 'Return'), ('transfer', 'Transfer')], null=True, blank=True)
    stock_status = models.CharField(
        max_length=20, 
        choices=[
            ('in_stock', 'In Stock'), 
            ('out_of_stock', 'Out of Stock'), 
            ('low_stock', 'Low Stock'),
            ('damaged', 'Damaged'),
            ('reserved', 'Reserved'),
            ('lost', 'Lost'),
            ], default='in_stock')
    additional_info = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    added_by_user_id = models.IntegerField(null=True, blank=True)
    domain_user_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class InventoryLogs(models.Model):
    id = models.AutoField(primary_key=True)
    inventory_id = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='logs')
    purchase_order_id = models.ForeignKey('OrderServices.PurchaseOrder', on_delete=models.CASCADE, related_name='inventory_logs')
    sales_order_id = models.ForeignKey('OrderServices.SalesOrder', on_delete=models.CASCADE, related_name='inventory_logs', null=True, blank=True)
    warehouse_id = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventory_logs')
    rack_shelf_floor_id = models.ForeignKey(RackAndShelvesAndFloors, on_delete=models.CASCADE, related_name='inventory_logs')
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=[
        ('added', 'Added'), 
        ('removed', 'Removed'), 
        ('moved', 'Moved'), 
        ('expired', 'Expired'), 
        ('damaged', 'Damaged'), 
        ('reserved', 'Reserved'), 
        ('lost', 'Lost'),
        ('warehouse transfer', 'Warehouse Transfer'),
        ('adjusted', 'Adjusted')], null=True, blank=True)
    action = models.CharField(max_length=100)
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_logs')
    performed_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)
    added_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='added_inventory_logs')

    additional_info = models.JSONField(null=True, blank=True)
    domain_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now=True)