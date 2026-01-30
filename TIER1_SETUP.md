# TIER 1 Implementation Setup Guide

## Step 1: Create Migrations

```bash
cd /home/billsbro/Music/fabrything/fabrything

# Generate migration files from model changes
python manage.py makemigrations fabrythingapp

# Review the migration file that was created
cat fabrythingapp/migrations/00XX_auto_YYYY_MM_DD_HHMM.py

# Apply migrations to database
python manage.py migrate

# Verify models are created
python manage.py shell
from fabrythingapp.models import ShippingMethod, OrderStatus, OrderNotification
print("Models created successfully!")
exit()
```

## Step 2: Update Requirements

Add these packages to requirements.txt:

```
# Already installed but ensure versions:
Django==4.2.19
djangorestframework==3.14.0
rest-framework-simplejwt==5.3.2

# Email notifications
django-celery-beat==2.5.0
django-celery-results==2.5.1
celery==5.3.4

# Task management & scheduling
python-dateutil==2.8.2
kombu==5.3.4

# Email backend
django-anymail==10.2

# Payment gateway (future, but add now for structure)
razorpay==1.3.0
stripe==7.10.0

# SMS notifications (future)
twilio==9.0.4
```

```bash
pip install -r requirements.txt
```

## Step 3: Update Settings

Add to `shopfabrything/settings.py`:

```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='your-email@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='your-app-password')

# Payment Methods Configuration
PAYMENT_METHODS = {
    'cod': {
        'name': 'Cash on Delivery',
        'enabled': True,
        'description': 'Pay when you receive your order'
    },
    'bkash': {
        'name': 'bKash',
        'enabled': False,
        'api_key': config('BKASH_API_KEY', default=''),
    },
    'nagad': {
        'name': 'Nagad',
        'enabled': False,
        'merchant_id': config('NAGAD_MERCHANT_ID', default=''),
    },
    'stripe': {
        'name': 'Credit Card (Stripe)',
        'enabled': False,
        'api_key': config('STRIPE_API_KEY', default=''),
        'publishable_key': config('STRIPE_PUBLISHABLE_KEY', default=''),
    },
}

# Order Configuration
ORDER_CONFIG = {
    'pending_expiry_hours': 24,  # Auto-cancel if payment not received
    'cancellation_allowed_statuses': ['pending', 'processing'],
    'return_window_days': 30,
}
```

## Step 4: Create Admin Customizations

Register models in admin.py with proper display

## Step 5: Create Serializers & APIs

Create CartOrderSerializer, AddressSerializer, ShippingMethodSerializer, etc.

## Step 6: Create React Components

Cart, Checkout, OrderTracking components

## Step 7: Create Email Templates

Order confirmation, status updates, etc.

## Step 8: Test Everything

Run tests to verify implementation

---

## Database Schema Changes

### CartOrder Table Changes:
- Added: `subtotal`, `shipping_cost`, `discount_applied`, `taxes` (for detailed pricing)
- Added: `payment_method` (COD, bKash, etc.)
- Added: `shipping_method_id` (FK to ShippingMethod)
- Added: `shipping_address_id` (FK to Address)
- Added: `coupon_code`, `notes` (for special handling)
- Added: `created_at`, `updated_at` (for tracking)

### CartOrderItems Table Changes:
- Added: `product_id` (FK instead of string "item")
- Added: `size`, `color` (for clothing specifics)
- Added: `created_at` (for historical tracking)

### Address Table Enhancements:
- Added: `address_type` (home, work, other)
- Added: `full_name`, `phone_number` (required for shipping)
- Added: `city`, `state`, `postal_code`, `country`
- Added: `is_default` (default shipping address)
- Added: `created_at`, `updated_at`

### New Tables:
- `ShippingMethod` - Shipping options with costs
- `OrderStatus` - Status history tracking
- `OrderNotification` - Notification audit trail

---

## Next Steps After Setup

1. ✅ Models created
2. → Create serializers (Step 5 in this guide)
3. → Create API endpoints
4. → Build React components
5. → Create email templates
6. → Test thoroughly
7. → Deploy to staging

