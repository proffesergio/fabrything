import logging
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count
from fabrythingapp.models import Product, Category, Brand, ProductReview

logger = logging.getLogger(__name__)

class ProductService:
    """Service layer for Product operations"""
    
    @staticmethod
    def get_all_products(filters=None, search=None, ordering=None):
        """Get all products with optional filters and search"""
        queryset = Product.objects.filter(status=True, product_status='published')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()
        
        if filters:
            if 'category' in filters:
                queryset = queryset.filter(category__cid=filters['category'])
            if 'brand' in filters:
                queryset = queryset.filter(brand__bid=filters['brand'])
            if 'min_price' in filters and 'max_price' in filters:
                queryset = queryset.filter(
                    price__gte=filters['min_price'],
                    price__lte=filters['max_price']
                )
        
        if ordering:
            queryset = queryset.order_by(ordering)
        
        logger.info(f"Retrieved {queryset.count()} products with filters: {filters}")
        return queryset
    
    @staticmethod
    def get_product_by_id(product_id):
        """Get a single product with related data"""
        product = get_object_or_404(Product, pid=product_id, status=True)
        logger.info(f"Retrieved product: {product.title}")
        return product
    
    @staticmethod
    def get_product_average_rating(product_id):
        """Calculate average rating for a product"""
        reviews = ProductReview.objects.filter(product__pid=product_id)
        if not reviews.exists():
            return 0
        
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else 0
    
    @staticmethod
    def get_featured_products(limit=10):
        """Get featured products"""
        return Product.objects.filter(
            status=True,
            featured=True,
            product_status='published'
        )[:limit]
    
    @staticmethod
    def get_related_products(product_id, limit=5):
        """Get related products from same category"""
        product = get_object_or_404(Product, pid=product_id)
        return Product.objects.filter(
            category=product.category,
            status=True,
            product_status='published'
        ).exclude(pid=product_id)[:limit]
    
    @staticmethod
    def get_categories():
        """Get all categories"""
        return Category.objects.all()
    
    @staticmethod
    def get_brands():
        """Get all brands"""
        return Brand.objects.all()