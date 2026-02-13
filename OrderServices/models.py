from django.db import models

# from InventoryServices.models import Warehouse, RackAndShelvesAndFloors, Inventory
from userauthapp.models import User
from fabrythingapp.models import Product

# Create your models here.
class PurchaseOrder(models.Model):
    id = models.AutoField(primary_key=True)
    warehouse_id = models.ForeignKey('InventoryServices.Warehouse', on_delete=models.CASCADE)
    order_number = models.CharField(max_length=100, unique=True)
    supplier_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supplier_orders')
    supplier_name = models.CharField(max_length=100)
    purchase_order_code = models.CharField(max_length=100, null=True, blank=True)
    payment_options = models.CharField(max_length=100, null=True, blank=True, choices=[
        ('cash', 'CASH'),
        ('Mobile Banking', 'MOBILE BANKING'),
        ('credit', 'CREDIT'),
        ('cheque', 'CHEQUE'),
    ])


    order_date = models.DateField()
    delivery_date = models.DateField(null=True, blank=True)
    deliver_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD', choices=[
        ('USD', 'USD'),
        ('BDT', 'BDT'),
        ('EUR', 'EUR'),
    ])
    payment_status = models.CharField(max_length=20, choices=[
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ])
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_type = models.CharField(max_length=50, null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    additional_details = models.JSONField(null=True, blank=True)

    items = models.JSONField()  # Store order items as a JSON array
    notes = models.TextField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='po_approved_by')
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_by_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='po_cancelled_by')
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_reason = models.TextField(null=True, blank=True)
    recieved_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='po_received_by')
    recieved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_number
    
class PurchaseOrderItems(models.Model):
    id = models.AutoField(primary_key=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='order_items')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_type = models.CharField(max_length=20, choices=[
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
    ], null=True, blank=True)
    tax_type = models.CharField(max_length=20, choices=[
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
    ], null=True, blank=True)
    additional_info = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('backordered', 'Backordered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ], default='pending')   
    created_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='poi_created_by') 
    updated_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='poi_updated_by')
    domain_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    approved_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='poi_approved_by')
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='poi_cancelled_by')
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_reason = models.TextField(null=True, blank=True)
    recieved_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='poi_received_by')
    recieved_at = models.DateTimeField(null=True, blank=True)

    order_quantity = models.IntegerField()
    received_quantity = models.IntegerField(default=0)
    pending_quantity = models.IntegerField()
    returned_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='poi_returned_by')
    returned_at = models.DateTimeField(null=True, blank=True)
    return_reason = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_name} - {self.quantity}"
    
class PurchaseOrderInwardedLog(models.Model):
    id = models.AutoField(primary_key=True)
    purchase_order_id = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='po_inward_logs')
    invoice_path = models.TextField(max_length=255, null=True, blank=True)
    invoice_number = models.CharField(max_length=100, null=True, blank=True)
    additional_info = models.JSONField(null=True, blank=True)
    domain_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    purchase_order_item = models.ForeignKey(PurchaseOrderItems, on_delete=models.CASCADE, related_name='poinward_logs')
    quantity_received = models.IntegerField()
    received_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poinward_received_by')
    received_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO Item ID: {self.purchase_order_item.id} - Qty Received: {self.quantity_received}"
    
class PurchaseOrderItemInwardedLog(models.Model):
    id = models.AutoField(primary_key=True)
    purchase_order_item_id = models.ForeignKey(PurchaseOrderItems, on_delete=models.CASCADE, related_name='poiinward_logs')
    quantity_received = models.IntegerField()
    received_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poiinward_received_by')
    received_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)
    domain_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    additional_info = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('backordered', 'Backordered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ], default='pending')   

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO Item ID: {self.purchase_order_item_id.id} - Qty Received: {self.quantity_received}"
    
class PurchaseOrderLogs(models.Model):
    id = models.AutoField(primary_key=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='po_logs')
    action = models.CharField(max_length=100)
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='po_action_logs')
    performed_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)
    domain_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO ID: {self.purchase_order.id} - Action: {self.action}"
    
# Sales Order models.
class SalesOrder(models.Model):
    id = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=100, unique=True)
    customer_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_sales_orders')
    sales_order_code = models.CharField(max_length=100, null=True, blank=True)
    payment_options = models.CharField(max_length=100, null=True, blank=True, choices=[
        ('cash', 'CASH'),
        ('Mobile Banking', 'MOBILE BANKING'),
        ('credit', 'CREDIT'),
        ('cheque', 'CHEQUE'),
    ])
    order_date = models.DateField()
    delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD', choices=[
        ('USD', 'USD'),
        ('BDT', 'BDT'),
        ('EUR', 'EUR'),
    ])
    payment_status = models.CharField(max_length=20, choices=[
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ])
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_type = models.CharField(max_length=50, null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    additional_details = models.JSONField(null=True, blank=True)

    items = models.JSONField()  # Store order items as a JSON array
    notes = models.TextField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='so_approved_by')
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_by_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='so_cancelled_by')
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_reason = models.TextField(null=True, blank=True)
    recieved_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='so_received_by')
    recieved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_number
    
class SalesOrderItems(models.Model):
    id = models.AutoField(primary_key=True)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='order_items')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_type = models.CharField(max_length=20, choices=[
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
    ], null=True, blank=True)
    tax_type = models.CharField(max_length=20, choices=[
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
    ], null=True, blank=True)
    additional_info = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('backordered', 'Backordered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ], default='pending')   
    created_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='soi_created_by') 
    updated_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='soi_updated_by')
    domain_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    approved_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='soi_approved_by')
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='soi_cancelled_by')
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_reason = models.TextField(null=True, blank=True)
    shipped_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='soi_shipped_by')
    shipped_at = models.DateTimeField(null=True, blank=True)

    quantity_ordered = models.IntegerField()
    quantity_delivered = models.IntegerField(default=0)
    quantity_cancelled = models.IntegerField(default=0)
    quantity_returned = models.IntegerField(default=0)
    received_quantity = models.IntegerField(default=0)
    pending_quantity = models.IntegerField()
    returned_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='soi_returned_by')
    returned_at = models.DateTimeField(null=True, blank=True)
    return_reason = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_name} - {self.quantity}"
    
class SalesOrderOutwardedLog(models.Model):
    id = models.AutoField(primary_key=True)
    sales_order_id = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='so_outward_logs')
    invoice_path = models.TextField(max_length=255, null=True, blank=True)
    invoice_number = models.CharField(max_length=100, null=True, blank=True)
    additional_info = models.JSONField(null=True, blank=True)
    domain_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    sales_order_item = models.ForeignKey(SalesOrderItems, on_delete=models.CASCADE, related_name='sooutward_logs')
    quantity_received = models.IntegerField()
    received_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sooutward_received_by')
    received_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)
    outwarded_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sooutward_by')
    outwarded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('partial received', 'Partial Received'),
        ('backordered', 'Backordered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ], default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SO Item ID: {self.sales_order_item.id} - Qty Received: {self.quantity_received}"
    
class SalesOrderItemOutwardedLog(models.Model):
    id = models.AutoField(primary_key=True)
    sales_order_item_id = models.ForeignKey(SalesOrderItems, on_delete=models.CASCADE, related_name='soioutward_logs')
    quantity_received = models.IntegerField()
    received_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='soioutward_received_by')
    received_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)
    domain_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    outwarded_quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    additional_info = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('partial delivered', 'Partial Delivered'),
        ('received', 'Received'),
        ('backordered', 'Backordered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ], default='pending')   

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SO Item ID: {self.sales_order_item_id.id} - Qty Outwarded: {self.outwarded_quantity}"
    
class SalesOrderLogs(models.Model):
    id = models.AutoField(primary_key=True)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='so_logs')
    action = models.CharField(max_length=100)
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='so_action_logs')
    performed_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)
    domain_user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SO ID: {self.sales_order.id} - Action: {self.action}"
