from django.db import models
from django.conf import settings


class Vendor(models.Model):
    """Vendor profile linked to User model"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor'
    )
    business_name = models.CharField(max_length=255)
    business_address = models.TextField()
    phone = models.CharField(max_length=20)
    tax_id = models.CharField(max_length=50, unique=True)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_payout = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.business_name


class VendorRegistration(models.Model):
    """Vendor applications with document handling"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    BUSINESS_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('partnership', 'Partnership'),
        ('company', 'Company'),
        ('corporation', 'Corporation'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_applications'
    )
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES)
    business_address = models.TextField()
    phone = models.CharField(max_length=20)
    tax_id = models.CharField(max_length=50)

    # Document fields
    nid_document = models.FileField(upload_to='vendor_docs/nid/')
    trade_license = models.FileField(upload_to='vendor_docs/trade_license/', blank=True, null=True)
    tin_certificate = models.FileField(upload_to='vendor_docs/tin/', blank=True, null=True)

    # Payout details
    payout_method = models.CharField(max_length=20, choices=[
        ('bank', 'Bank Transfer'),
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
    ])
    payout_account = models.CharField(max_length=50)  # Account number or phone

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_applications'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.business_name} - {self.get_status_display()}"


class VendorPayout(models.Model):
    """Track vendor payouts"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    METHOD_CHOICES = [
        ('bank', 'Bank Transfer'),
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
    ]

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='payouts'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vendor.business_name} - {self.amount} ({self.get_status_display()})"
