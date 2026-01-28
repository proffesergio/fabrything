import logging
from decimal import Decimal
from django.shortcuts import get_object_or_404
from fabrythingapp.models import CartOrder, CartOrderItems, Product, Wishlist
from userauthapp.models import User

logger = logging.getLogger(__name__)

class CartService:
    """Service layer for Cart and Order operations"""
    
    @staticmethod
    def create_or_get_cart(user_id):
        """Create or get active cart for user"""
        user = get_object_or_404(User, id=user_id)
        cart, created = CartOrder.objects.get_or_create(
            user=user,
            paid_status=False,
            defaults={'price': Decimal('0.00')}
        )
        return cart
    
    @staticmethod
    def add_to_cart(user_id, product_id, quantity=1):
        """Add product to cart"""
        user = get_object_or_404(User, id=user_id)
        product = get_object_or_404(Product, pid=product_id)
        
        cart = CartService.create_or_get_cart(user_id)
        
        # Check if item already in cart
        cart_item = CartOrderItems.objects.filter(
            order=cart,
            item=product.title
        ).first()
        
        if cart_item:
            cart_item.quantity += quantity
            cart_item.total = Decimal(str(cart_item.quantity)) * product.price
            cart_item.save()
            logger.info(f"Updated cart item: {product.title}, new quantity: {cart_item.quantity}")
        else:
            cart_item = CartOrderItems.objects.create(
                order=cart,
                invoice=f"INV-{user_id}-{product.pid}",
                product_status="pending",
                item=product.title,
                image=str(product.image),
                quantity=quantity,
                price=product.price,
                total=Decimal(str(quantity)) * product.price
            )
            logger.info(f"Added to cart: {product.title}")
        
        # Update cart total
        CartService.update_cart_total(cart.id)
        return cart_item
    
    @staticmethod
    def remove_from_cart(user_id, product_title):
        """Remove product from cart"""
        cart = CartService.create_or_get_cart(user_id)
        
        cart_item = CartOrderItems.objects.filter(
            order=cart,
            item=product_title
        ).first()
        
        if cart_item:
            cart_item.delete()
            logger.info(f"Removed from cart: {product_title}")
            CartService.update_cart_total(cart.id)
            return True
        
        return False
    
    @staticmethod
    def update_cart_total(cart_id):
        """Recalculate and update cart total"""
        cart = get_object_or_404(CartOrder, id=cart_id)
        total = sum(item.total for item in cart.cartorderitems_set.all())
        cart.price = total
        cart.save()
        logger.info(f"Updated cart {cart_id} total: {total}")
    
    @staticmethod
    def get_cart_items(user_id):
        """Get all items in user's cart"""
        cart = CartService.create_or_get_cart(user_id)
        return cart.cartorderitems_set.all()
    
    @staticmethod
    def add_to_wishlist(user_id, product_id):
        """Add product to wishlist"""
        user = get_object_or_404(User, id=user_id)
        product = get_object_or_404(Product, pid=product_id)
        
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=user,
            product=product
        )
        
        if created:
            logger.info(f"Added to wishlist: {product.title}")
        
        return wishlist_item, created
    
    @staticmethod
    def remove_from_wishlist(user_id, product_id):
        """Remove product from wishlist"""
        wishlist_item = Wishlist.objects.filter(
            user_id=user_id,
            product__pid=product_id
        ).first()
        
        if wishlist_item:
            wishlist_item.delete()
            logger.info(f"Removed from wishlist: {wishlist_item.product.title}")
            return True
        
        return False
    
    @staticmethod
    def get_wishlist(user_id):
        """Get user's wishlist"""
        return Wishlist.objects.filter(user_id=user_id)