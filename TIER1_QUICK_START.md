# TIER 1 - QUICK REFERENCE & GIT WORKFLOW

## 📚 Documentation Files Created

| File | Purpose | Status |
|------|---------|--------|
| `TIER1_IMPLEMENTATION_ROADMAP.md` | Complete 4-week implementation plan | ✅ Ready |
| `TIER1_WEEK1_GUIDE.md` | Backend implementation (migrations, serializers, viewsets) | ✅ Ready |
| `TIER1_WEEK1_REACT.md` | React components and hooks | ✅ Ready |
| `static/css/tier1-cart-checkout.css` | Complete styling (mobile-responsive) | ✅ Ready |
| `TIER1_QUICK_START.md` | This file - Quick start commands | ✅ Ready |

---

## 🚀 QUICK START (Copy & Paste Commands)

### Day 1: Setup Environment
```bash
cd /home/billsbro/Music/fabrything/fabrything

# Test Python environment
python --version  # Should be 3.12+
python -m pip list | grep -E "django|rest_framework"

# Create migrations for all new models
python manage.py makemigrations fabrythingapp

# Review migration file (check for issues)
ls -la fabrythingapp/migrations/ | tail -1

# Apply migrations to database
python manage.py migrate

# Create cache table (for session management)
python manage.py createcachetable

# Test models in Django shell
python manage.py shell << 'EOF'
from fabrythingapp.models import ShippingMethod, OrderStatus, CartOrder, Address, OrderNotification
print("✓ ShippingMethod:", ShippingMethod._meta.db_table)
print("✓ OrderStatus:", OrderStatus._meta.db_table)
print("✓ CartOrder:", CartOrder._meta.db_table)
print("✓ Address:", Address._meta.db_table)
print("✓ OrderNotification:", OrderNotification._meta.db_table)
print("\n✅ All models created successfully!")
exit()
EOF
```

---

## 📝 Implementation Checklist

### Week 1: Backend (Cart & Serializers)

#### Day 1-2: Database Layer
- [ ] Run migrations (all 5 commands above)
- [ ] Verify all models in database
- [ ] Create ShippingMethod test data
  ```python
  python manage.py shell
  from fabrythingapp.models import ShippingMethod
  ShippingMethod.objects.create(
      name='Standard', cost=5.00, delivery_days=3, is_active=True
  )
  ShippingMethod.objects.create(
      name='Express', cost=15.00, delivery_days=1, is_active=True
  )
  exit()
  ```

#### Day 2: Serializers
- [ ] Copy serializer code from TIER1_WEEK1_GUIDE.md
- [ ] Paste into `fabrythingapp/serializers.py`
- [ ] Test import: `python -c "from fabrythingapp.serializers import CartOrderSerializer"`
- [ ] No errors should appear

#### Day 3: Admin Setup
- [ ] Add admin classes for new models
- [ ] Test: `python manage.py shell`
  ```python
  from django.contrib.admin import site
  from fabrythingapp.models import ShippingMethod
  print(site.get_app_list(None))  # Check all models registered
  exit()
  ```

#### Day 3-4: ViewSets
- [ ] Copy CartViewSet from TIER1_WEEK1_GUIDE.md
- [ ] Copy CheckoutViewSet from TIER1_WEEK1_GUIDE.md
- [ ] Copy OrderHistoryViewSet from TIER1_WEEK1_GUIDE.md
- [ ] Add to `fabrythingapp/views.py`
- [ ] Update `fabrythingapp/api_urls.py` with router registration

#### Day 5: Testing
- [ ] Start development server: `python manage.py runserver`
- [ ] Test API endpoints with cURL:

```bash
# Get JWT token (replace with your actual credentials)
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' | jq -r '.access')

# Get current cart
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/cart/current_cart/

# Add item
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":"prod123","quantity":1}' \
  http://localhost:8000/api/v1/cart/add_item/

# View orders
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/orders/
```

---

### Week 2: Frontend (React Components)

#### Day 1: React Setup
```bash
cd /static
npm init -y
npm install react react-dom framer-motion
```

#### Day 2: Create Hooks
- [ ] Copy `useCart.js` from TIER1_WEEK1_REACT.md
- [ ] Copy `useCheckout.js` from TIER1_WEEK1_REACT.md
- [ ] Copy `useAddresses.js` from TIER1_WEEK1_REACT.md
- [ ] Place in `/static/js/react/hooks/`

#### Day 3-4: Create Components
- [ ] Copy `CartPage.jsx` from TIER1_WEEK1_REACT.md
- [ ] Copy `CheckoutFlow.jsx` from TIER1_WEEK1_REACT.md
- [ ] Place in `/static/js/react/components/`

#### Day 5: Styling
- [ ] CSS file already created: `static/css/tier1-cart-checkout.css`
- [ ] Test responsive on different screen sizes

---

### Week 3: Order Management

#### Day 1-2: Order Tracking
- [ ] Create `/static/js/react/components/OrderTracking.jsx`
- [ ] Create `/static/js/react/components/OrderHistory.jsx`

#### Day 3-4: Notifications
- [ ] Setup Celery tasks in `fabrythingapp/tasks.py`
- [ ] Create email templates in `templates/emails/`
- [ ] Configure Redis connection

#### Day 5: Admin Dashboard
- [ ] Create `/static/js/react/pages/AdminDashboard.jsx`
- [ ] Add admin order update endpoints

---

### Week 4: Deployment

#### Day 1-2: Security
- [ ] Email verification system
- [ ] Password reset system
- [ ] Security headers in settings.py

#### Day 3-4: Mobile Optimization
- [ ] Test on iPhone (375px)
- [ ] Test on Android (360px)
- [ ] Run Lighthouse audit

#### Day 5: Deploy
- [ ] Choose hosting platform (Railway recommended)
- [ ] Setup PostgreSQL
- [ ] Configure environment variables
- [ ] Deploy with `git push`

---

## 🔗 GIT WORKFLOW

### Commit Template
```bash
git config commit.template <<'EOF'
[TIER 1] [Week X] [Category] - Brief description

Detailed description of changes:
- What was added/modified
- Why this change was needed
- Any important notes

Related endpoints/features: /api/v1/cart/, /api/v1/checkout/
Files modified: fabrythingapp/serializers.py, fabrythingapp/views.py
EOF
```

### Daily Commits
```bash
# Day 1: Migrations
git add fabrythingapp/migrations/
git commit -m "[TIER 1] [Week 1 Day 1] Database - Created migrations for 5 new models"
git push origin main

# Day 2: Serializers
git add fabrythingapp/serializers.py
git commit -m "[TIER 1] [Week 1 Day 2] Serializers - Added 8 serializers for cart and order"
git push origin main

# Day 3: ViewSets
git add fabrythingapp/views.py fabrythingapp/api_urls.py
git commit -m "[TIER 1] [Week 1 Day 3] APIs - Created CartViewSet and CheckoutViewSet endpoints"
git push origin main

# Day 4: Testing
git add tests/ requirements.txt
git commit -m "[TIER 1] [Week 1 Day 4] Tests - Added API integration tests"
git push origin main

# Day 5: React Components
git add static/js/react/ static/css/tier1-cart-checkout.css
git commit -m "[TIER 1] [Week 2 Day 5] Frontend - Added React cart and checkout components"
git push origin main
```

### Final TIER 1 Commit
```bash
git add --all
git commit -m "[TIER 1] COMPLETE - Full shopping cart, checkout, and order management

New Features:
- Shopping cart with add/remove/update functionality
- 4-step checkout flow (address → shipping → review → confirm)
- Order placement with COD payment method
- Order tracking and history
- Admin order management dashboard
- Email notifications framework
- Mobile-responsive design (tested on 360px-1400px)
- JWT authentication and security hardening

Database Models:
- Enhanced: CartOrder, CartOrderItems, Address
- New: ShippingMethod, OrderStatus, OrderNotification

API Endpoints (15 new):
- Cart management: add_item, remove_item, update_item, clear, current_cart
- Checkout: validate, confirm
- Order history: list, retrieve, track, cancel
- Admin: update_status, generate_invoice

Files Added/Modified:
- Backend: serializers.py, views.py, api_urls.py, models.py, admin.py, tasks.py
- Frontend: 5 React components, 3 custom hooks, 1 CSS file
- Config: requirements.txt, settings.py, celery.py
- Docs: 5 implementation guides

Tests: 40+ test cases pass
Performance: Lighthouse score 85+
Mobile: Responsive down to 320px

Time Invested: ~120-160 hours
Status: Production Ready ✅"

git push origin main
```

---

## 🐛 TROUBLESHOOTING

### Issue: Migration Errors
```bash
# Solution 1: Check migration status
python manage.py showmigrations

# Solution 2: Reset and re-migrate (dev only!)
python manage.py migrate fabrythingapp zero
python manage.py makemigrations
python manage.py migrate

# Solution 3: Check for syntax errors
python -m py_compile fabrythingapp/models.py
```

### Issue: Import Errors
```bash
# Solution: Add to fabrythingapp/views.py top:
import logging
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from fabrythingapp.models import CartOrder, CartOrderItems, ShippingMethod, OrderStatus
from fabrythingapp.serializers import CartOrderSerializer, CheckoutSerializer

logger = logging.getLogger(__name__)
```

### Issue: CartService Not Found
```bash
# Make sure CartService exists in fabrythingapp/services/cart_service.py
# If not, add this placeholder:
class CartService:
    @staticmethod
    def update_cart_total(cart_id):
        from fabrythingapp.models import CartOrder
        cart = CartOrder.objects.get(id=cart_id)
        total = sum(item.total for item in cart.items.all())
        cart.subtotal = total
        cart.save()
        return cart
```

### Issue: React Components Not Loading
```bash
# Solution: Include this in your HTML template:
<script>
  const API_BASE = '/api/v1';
  const TOKEN = localStorage.getItem('access_token');
</script>

# Then import React component:
<div id="cart-app"></div>
<script type="module">
  import CartPage from '/static/js/react/components/CartPage.jsx';
  ReactDOM.render(<CartPage />, document.getElementById('cart-app'));
</script>
```

---

## 📦 REQUIRED PACKAGES

```bash
# Backend packages (already in requirements.txt)
pip install Django==4.2.19
pip install djangorestframework==3.16.1
pip install djangorestframework-simplejwt==5.5.1
pip install django-filter==24.1
pip install celery==5.3.4
pip install redis==5.0.1

# Frontend packages (install in /static/)
npm install react@18
npm install react-dom@18
npm install framer-motion@10
npm install axios  # optional, for API calls

# Email/Notification packages (already in requirements.txt)
pip install django-anymail==10.2
pip install twilio==9.0.4
```

---

## 💾 DATABASE BACKUP

```bash
# Backup SQLite database before migrations
cp db.sqlite3 db.sqlite3.backup

# Or export PostgreSQL:
pg_dump dbname > backup.sql

# Restore from backup:
psql dbname < backup.sql
```

---

## 🎯 DAILY STANDUP TEMPLATE

Use this to track daily progress:

```markdown
# Week 1 Day 1 - Standup

## What I Did
- [x] Created migrations for 5 new models
- [x] Applied migrations to database
- [x] Created cache table
- [x] Verified all models in Django shell

## What I'm Doing Next
- [ ] Create 8 serializers for cart/order
- [ ] Add admin classes for models
- [ ] Test serializer import

## Blockers
- None

## Time Spent
- 3 hours

## Confidence
- 95% on track for Week 1 completion
```

---

## 📞 TESTING ENDPOINTS (Postman Collection)

```json
{
  "info": {
    "name": "TIER 1 API Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Cart",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/api/v1/cart/current_cart/"
      }
    },
    {
      "name": "Add Item",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/api/v1/cart/add_item/",
        "body": {"product_id": "prod123", "quantity": 1}
      }
    }
  ]
}
```

---

## 🏆 SUCCESS CRITERIA

**TIER 1 is complete when:**
- ✅ Add product to cart → shows in cart
- ✅ Remove product → removes from cart
- ✅ Update quantity → recalculates total
- ✅ Start checkout → shows 4 steps
- ✅ Complete checkout → creates order
- ✅ View order history → shows all orders
- ✅ Track order → shows status timeline
- ✅ Admin can update status → customer notified
- ✅ Works on mobile (320px-1400px)
- ✅ Deployed to production URL

**When all ✅ are checked, TIER 1 is DONE!**

---

**TIER 1 Status: 🚀 READY FOR IMPLEMENTATION**
