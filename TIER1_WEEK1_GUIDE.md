"""
TIER 1 COMPLETE IMPLEMENTATION GUIDE
4-Week Sprint to Production-Ready Shopping Experience

Author: GitHub Copilot
Date: January 2026
Status: READY FOR IMPLEMENTATION
"""

# ============================================================================
# WEEK 1: CART MANAGEMENT & PERSISTENCE
# ============================================================================

"""
Day 1-2: Database & API Layer
Goal: Ensure models are created, serializers are ready, API endpoints work

Day 3-4: Frontend - Cart Component  
Goal: Build React CartComponent with add/remove/update functionality

Day 5: Mobile & Performance
Goal: Responsive design, touch optimization, load testing
"""

# ============================================================================
# STEP 1: CREATE MIGRATIONS (Day 1, 1-2 hours)
# ============================================================================

"""
Execute these commands:

cd /home/billsbro/Music/fabrything/fabrything

# 1. Create migration files from updated models
python manage.py makemigrations fabrythingapp

# 2. Review the migration (check for issues)
# Look at: fabrythingapp/migrations/00XX_auto_YYYY_MM_DD_HHMM.py

# 3. Apply migrations
python manage.py migrate

# 4. Create cache table for sessions
python manage.py createcachetable

# 5. Test models in shell
python manage.py shell

from fabrythingapp.models import ShippingMethod, OrderStatus, CartOrder
from userauthapp.models import User

# Create test data
sm = ShippingMethod.objects.create(
    name='Standard',
    cost=5.00,
    delivery_days=3,
    is_active=True
)
print(f"Created: {sm}")

# Verify Address model changes
from fabrythingapp.models import Address
user = User.objects.first()
if user:
    addr = Address.objects.create(
        user=user,
        full_name="Test User",
        phone_number="01700000000",
        address="123 Main St",
        city="Dhaka",
        state="Dhaka",
        postal_code="1205",
        is_default=True
    )
    print(f"Created address: {addr}")

exit()
"""

# ============================================================================
# STEP 2: CREATE SERIALIZERS (Day 2, 2-3 hours)
# ============================================================================

"""
File: fabrythingapp/serializers.py

Add these serializers at the end of the file:
"""

SERIALIZERS_CODE = '''
# ============================================================================
# TIER 1: CART & ORDER SERIALIZERS
# ============================================================================

class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for shipping methods with cost and delivery time"""
    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'description', 'cost', 'delivery_days']
        read_only_fields = ['id']


class AddressSerializer(serializers.ModelSerializer):
    """Complete address serializer for checkout and user profile"""
    country_display = serializers.CharField(source='country', read_only=True)
    
    class Meta:
        model = Address
        fields = [
            'id', 'address_type', 'full_name', 'phone_number',
            'address', 'city', 'state', 'postal_code', 'country',
            'is_default', 'created_at', 'get_full_address'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not value or len(value) < 10:
            raise serializers.ValidationError("Invalid phone number")
        return value
    
    def validate_postal_code(self, value):
        """Validate postal code"""
        if not value or len(value) < 3:
            raise serializers.ValidationError("Invalid postal code")
        return value


class CartOrderItemsSerializer(serializers.ModelSerializer):
    """Individual cart/order items"""
    product_pid = serializers.CharField(source='product.pid', read_only=True)
    product_title = serializers.CharField(source='item', read_only=True)
    
    class Meta:
        model = CartOrderItems
        fields = [
            'id', 'product_pid', 'product_title', 'image',
            'size', 'color', 'quantity', 'price', 'total', 'created_at'
        ]
        read_only_fields = ['id', 'total', 'created_at']


class CartOrderSerializer(serializers.ModelSerializer):
    """
    Complete cart/order serializer with all details.
    Used for cart page and order confirmation.
    """
    items = CartOrderItemsSerializer(many=True, read_only=True)
    shipping_method_details = ShippingMethodSerializer(
        source='shipping_method',
        read_only=True
    )
    shipping_address_details = AddressSerializer(
        source='shipping_address',
        read_only=True
    )
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    product_status_display = serializers.CharField(
        source='get_product_status_display',
        read_only=True
    )
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = CartOrder
        fields = [
            'id', 'user', 'user_email', 'items',
            'subtotal', 'shipping_cost', 'discount_applied', 'taxes', 'price',
            'payment_method', 'payment_method_display',
            'shipping_method', 'shipping_method_details',
            'shipping_address', 'shipping_address_details',
            'coupon_code', 'notes',
            'product_status', 'product_status_display',
            'paid_status', 'order_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'subtotal', 'taxes', 'order_date',
            'created_at', 'updated_at'
        ]


class OrderStatusSerializer(serializers.ModelSerializer):
    """Order status history entry"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = OrderStatus
        fields = ['id', 'status', 'status_display', 'tracking_number', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderNotificationSerializer(serializers.ModelSerializer):
    """Notification tracking"""
    notification_type_display = serializers.CharField(
        source='get_notification_type_display',
        read_only=True
    )
    
    class Meta:
        model = OrderNotification
        fields = [
            'id', 'notification_type', 'notification_type_display',
            'subject', 'message', 'sent_at', 'is_read'
        ]
        read_only_fields = ['id', 'sent_at']


class CheckoutSerializer(serializers.Serializer):
    """
    Serializer for checkout data (not a model).
    Combines order data with user selections.
    """
    # Existing cart data
    cart_id = serializers.IntegerField()
    
    # Address selection
    shipping_address_id = serializers.IntegerField(required=True)
    
    # Shipping method
    shipping_method_id = serializers.IntegerField(required=True)
    
    # Payment
    payment_method = serializers.ChoiceField(
        choices=[
            ('cod', 'Cash on Delivery'),
            ('bkash', 'bKash'),
            ('nagad', 'Nagad'),
            ('rocket', 'Rocket'),
            ('visa', 'Visa Card'),
            ('mastercard', 'MasterCard'),
        ]
    )
    
    # Optional
    coupon_code = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )
    
    def validate_shipping_address_id(self, value):
        """Verify address belongs to user"""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("User not authenticated")
        
        try:
            Address.objects.get(id=value, user=request.user)
        except Address.DoesNotExist:
            raise serializers.ValidationError("Invalid address")
        
        return value
    
    def validate_shipping_method_id(self, value):
        """Verify shipping method exists and is active"""
        try:
            method = ShippingMethod.objects.get(id=value, is_active=True)
        except ShippingMethod.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive shipping method")
        
        return value


class OrderConfirmationSerializer(serializers.ModelSerializer):
    """Minimal serializer for order confirmation page"""
    items = CartOrderItemsSerializer(many=True, read_only=True)
    shipping_address_details = AddressSerializer(
        source='shipping_address',
        read_only=True
    )
    
    class Meta:
        model = CartOrder
        fields = [
            'id', 'items', 'price', 'payment_method',
            'shipping_address_details', 'order_date',
            'created_at'
        ]
        read_only_fields = fields
'''

# ============================================================================
# STEP 3: CREATE API VIEWSETS (Day 2, 3-4 hours)
# ============================================================================

"""
File: fabrythingapp/views.py

Add these ViewSets to the file (at the end):
"""

VIEWSETS_CODE = '''
# ============================================================================
# TIER 1: CART & CHECKOUT VIEWSETS
# ============================================================================

class CartViewSet(viewsets.ViewSet):
    """
    ViewSet for shopping cart operations.
    
    Endpoints:
    - GET /api/v1/cart/ - Get current user's active cart
    - POST /api/v1/cart/add-item/ - Add product to cart
    - POST /api/v1/cart/remove-item/ - Remove item from cart
    - PATCH /api/v1/cart/update-item/ - Update item quantity
    - DELETE /api/v1/cart/clear/ - Clear entire cart
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def current_cart(self, request):
        """Get current user's active cart"""
        try:
            cart, created = CartOrder.objects.get_or_create(
                user=request.user,
                paid_status=False
            )
            serializer = CartOrderSerializer(cart)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting cart: {str(e)}")
            return Response(
                {'detail': 'Error retrieving cart'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Add product to cart or update quantity if exists.
        
        Request body:
        {
            "product_id": "prod123",
            "quantity": 1,
            "size": "M",
            "color": "Blue"
        }
        """
        try:
            product_id = request.data.get('product_id')
            quantity = int(request.data.get('quantity', 1))
            size = request.data.get('size', '')
            color = request.data.get('color', '')
            
            # Validate input
            if not product_id or quantity < 1:
                return Response(
                    {'detail': 'Invalid product_id or quantity'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get product
            product = Product.objects.get(pid=product_id)
            
            # Get or create cart
            cart, _ = CartOrder.objects.get_or_create(
                user=request.user,
                paid_status=False
            )
            
            # Check if item already in cart
            cart_item = CartOrderItems.objects.filter(
                order=cart,
                product=product,
                size=size,
                color=color
            ).first()
            
            if cart_item:
                # Update quantity
                cart_item.quantity += quantity
            else:
                # Create new cart item
                cart_item = CartOrderItems.objects.create(
                    order=cart,
                    product=product,
                    item=product.title,
                    image=str(product.image),
                    size=size,
                    color=color,
                    quantity=quantity,
                    price=product.price,
                    total=quantity * product.price
                )
            
            # Calculate totals
            cart_item.total = cart_item.quantity * product.price
            cart_item.save()
            
            # Update cart total
            CartService.update_cart_total(cart.id)
            
            logger.info(f"Added product {product_id} to cart for user {request.user.id}")
            
            serializer = CartOrderSerializer(cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {'detail': 'Invalid quantity format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error adding to cart: {str(e)}")
            return Response(
                {'detail': 'Error adding item to cart'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from cart"""
        try:
            item_id = request.data.get('item_id')
            
            if not item_id:
                return Response(
                    {'detail': 'item_id required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart_item = CartOrderItems.objects.get(
                id=item_id,
                order__user=request.user,
                order__paid_status=False
            )
            
            cart = cart_item.order
            cart_item.delete()
            
            # Recalculate cart total
            CartService.update_cart_total(cart.id)
            
            logger.info(f"Removed item {item_id} from cart for user {request.user.id}")
            
            serializer = CartOrderSerializer(cart)
            return Response(serializer.data)
            
        except CartOrderItems.DoesNotExist:
            return Response(
                {'detail': 'Item not found in cart'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error removing from cart: {str(e)}")
            return Response(
                {'detail': 'Error removing item'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['patch'])
    def update_item(self, request):
        """Update cart item quantity"""
        try:
            item_id = request.data.get('item_id')
            quantity = int(request.data.get('quantity', 1))
            
            if quantity < 0:
                return Response(
                    {'detail': 'Quantity must be >= 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart_item = CartOrderItems.objects.get(
                id=item_id,
                order__user=request.user,
                order__paid_status=False
            )
            
            if quantity == 0:
                # Remove item if quantity is 0
                cart = cart_item.order
                cart_item.delete()
            else:
                # Update quantity
                cart_item.quantity = quantity
                cart_item.total = quantity * cart_item.price
                cart_item.save()
                cart = cart_item.order
            
            CartService.update_cart_total(cart.id)
            
            serializer = CartOrderSerializer(cart)
            return Response(serializer.data)
            
        except CartOrderItems.DoesNotExist:
            return Response(
                {'detail': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {'detail': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating cart item: {str(e)}")
            return Response(
                {'detail': 'Error updating item'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear entire cart"""
        try:
            cart = CartOrder.objects.get(
                user=request.user,
                paid_status=False
            )
            cart.items.all().delete()
            cart.price = 0
            cart.save()
            
            logger.info(f"Cleared cart for user {request.user.id}")
            
            return Response(
                {'detail': 'Cart cleared successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except CartOrder.DoesNotExist:
            return Response(
                {'detail': 'No active cart'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error clearing cart: {str(e)}")
            return Response(
                {'detail': 'Error clearing cart'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CheckoutViewSet(viewsets.ViewSet):
    """
    ViewSet for checkout process.
    
    Endpoints:
    - POST /api/v1/checkout/validate/ - Validate checkout data
    - POST /api/v1/checkout/confirm/ - Complete checkout and create order
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Validate checkout data before final confirmation"""
        serializer = CheckoutSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get cart
            cart = CartOrder.objects.get(
                id=serializer.validated_data['cart_id'],
                user=request.user,
                paid_status=False
            )
            
            if not cart.items.exists():
                return Response(
                    {'detail': 'Cart is empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get shipping details
            address = Address.objects.get(
                id=serializer.validated_data['shipping_address_id'],
                user=request.user
            )
            shipping_method = ShippingMethod.objects.get(
                id=serializer.validated_data['shipping_method_id'],
                is_active=True
            )
            
            return Response({
                'valid': True,
                'cart': CartOrderSerializer(cart).data,
                'address': AddressSerializer(address).data,
                'shipping_method': ShippingMethodSerializer(shipping_method).data
            })
            
        except CartOrder.DoesNotExist:
            return Response(
                {'detail': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error validating checkout: {str(e)}")
            return Response(
                {'detail': 'Error validating checkout'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def confirm(self, request):
        """
        Complete checkout and create order.
        
        This is the final step that converts cart to order.
        """
        serializer = CheckoutSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get cart
            cart = CartOrder.objects.get(
                id=serializer.validated_data['cart_id'],
                user=request.user,
                paid_status=False
            )
            
            # Get shipping details
            address = Address.objects.get(
                id=serializer.validated_data['shipping_address_id'],
                user=request.user
            )
            shipping_method = ShippingMethod.objects.get(
                id=serializer.validated_data['shipping_method_id'],
                is_active=True
            )
            
            # Calculate totals
            subtotal = sum(item.total for item in cart.items.all())
            taxes = subtotal * 0.05  # 5% tax (configurable)
            shipping_cost = shipping_method.cost
            total = subtotal + taxes + shipping_cost
            
            # Update order
            cart.subtotal = subtotal
            cart.taxes = taxes
            cart.shipping_cost = shipping_cost
            cart.price = total
            cart.shipping_method = shipping_method
            cart.shipping_address = address
            cart.payment_method = serializer.validated_data['payment_method']
            cart.coupon_code = serializer.validated_data.get('coupon_code', '')
            cart.notes = serializer.validated_data.get('notes', '')
            cart.save()
            
            # Create initial status
            OrderStatus.objects.create(
                order=cart,
                status='pending',
                notes='Order placed successfully'
            )
            
            # Send confirmation email (async task via Celery)
            # tasks.send_order_confirmation.delay(cart.id)
            
            logger.info(f"Order created: {cart.id} for user {request.user.id}")
            
            return Response(
                OrderConfirmationSerializer(cart).data,
                status=status.HTTP_201_CREATED
            )
            
        except CartOrder.DoesNotExist:
            return Response(
                {'detail': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Address.DoesNotExist:
            return Response(
                {'detail': 'Shipping address not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ShippingMethod.DoesNotExist:
            return Response(
                {'detail': 'Shipping method not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error confirming checkout: {str(e)}")
            return Response(
                {'detail': 'Error processing order'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing order history.
    
    Endpoints:
    - GET /api/v1/orders/ - List user's orders
    - GET /api/v1/orders/{id}/ - Get order details
    """
    
    serializer_class = CartOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['payment_method', 'product_status']
    ordering = ['-order_date']
    
    def get_queryset(self):
        """Return only current user's orders"""
        return CartOrder.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def track(self, request, pk=None):
        """Get order tracking details"""
        order = self.get_object()
        status_history = order.status_history.all()
        
        return Response({
            'order_id': order.id,
            'current_status': order.get_product_status_display(),
            'status_timeline': OrderStatusSerializer(
                status_history,
                many=True
            ).data,
            'shipping_address': AddressSerializer(order.shipping_address).data,
            'expected_delivery': (
                order.order_date + timedelta(days=order.shipping_method.delivery_days)
            ).strftime('%Y-%m-%d') if order.shipping_method else None
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Request order cancellation (if allowed)"""
        order = self.get_object()
        
        # Check if cancellation is allowed
        if order.product_status not in ['pending', 'processing']:
            return Response(
                {'detail': 'Order cannot be cancelled in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if order.paid_status:
            return Response(
                {'detail': 'Cannot cancel paid orders. Please request refund instead.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status
        order.product_status = 'cancelled'
        order.save()
        
        # Create status entry
        OrderStatus.objects.create(
            order=order,
            status='cancelled',
            notes=f'Cancelled by customer: {request.data.get("reason", "No reason provided")}'
        )
        
        logger.info(f"Order {order.id} cancelled by user {request.user.id}")
        
        return Response(
            {'detail': 'Order cancelled successfully'},
            status=status.HTTP_200_OK
        )
'''

# ============================================================================
# STEP 4: REGISTER ROUTES (Day 2, 1 hour)
# ============================================================================

"""
File: fabrythingapp/api_urls.py

Update router registration:
"""

URLS_UPDATE = '''
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from fabrythingapp.views import (
    # ... existing imports ...
    CartViewSet, CheckoutViewSet, OrderHistoryViewSet
)

router = DefaultRouter()
# ... existing registrations ...
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'checkout', CheckoutViewSet, basename='checkout')
router.register(r'orders', OrderHistoryViewSet, basename='order-history')

urlpatterns = [
    path('', include(router.urls)),
]
'''

# ============================================================================
# NEXT STEPS
# ============================================================================

print("""
✅ WEEK 1 IMPLEMENTATION CHECKLIST:

Step 1: Create Migrations
  [ ] Run: python manage.py makemigrations
  [ ] Review migration file
  [ ] Run: python manage.py migrate
  [ ] Test in shell

Step 2: Create Serializers
  [ ] Add ShippingMethodSerializer
  [ ] Add AddressSerializer
  [ ] Add CartOrderSerializer
  [ ] Add CheckoutSerializer
  [ ] Add OrderConfirmationSerializer

Step 3: Create ViewSets
  [ ] Add CartViewSet (add_item, remove_item, update_item, clear)
  [ ] Add CheckoutViewSet (validate, confirm)
  [ ] Add OrderHistoryViewSet (list, retrieve, track, cancel)

Step 4: Register Routes
  [ ] Update api_urls.py with new routes

Step 5: Test APIs
  [ ] POST /api/v1/cart/add-item/ - Add product
  [ ] GET /api/v1/cart/ - View cart
  [ ] POST /api/v1/checkout/validate/ - Validate checkout
  [ ] POST /api/v1/checkout/confirm/ - Create order
  [ ] GET /api/v1/orders/ - View orders
  [ ] GET /api/v1/orders/{id}/track/ - Track order

WEEK 1 TIME ESTIMATE: 30-40 hours
Days 1-2: Models & Serializers (12-16 hours)
Days 3-4: ViewSets & APIs (12-16 hours)
Day 5: Testing & Polish (6-8 hours)

STATUS: Code examples provided above, ready to implement
""")
