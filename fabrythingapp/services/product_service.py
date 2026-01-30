"""
Product Service - Business logic for product operations

This service handles all product-related operations including retrieval,
filtering, and query optimization. It uses select_related() and prefetch_related()
to minimize database queries (N+1 prevention).

Architecture Pattern:
    Views → Service → QuerySet/Models → Database
    
The service layer keeps business logic separate from HTTP handling in views,
making it testable and reusable.

Example:
    from fabrythingapp.services import ProductService
    
    # Get products with optimized queries
    products = ProductService.get_all_products(
        filters={'category': 'cat123'},
        search='cotton',
        ordering='-price'
    )
"""

import logging
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count, F, DecimalField, IntegerField
from django.db.models.functions import Cast
from fabrythingapp.models import Product, Category, Brand, ProductReview, ProductView

logger = logging.getLogger(__name__)


class ProductService:
    """Service layer for Product operations with optimization"""
    
    @staticmethod
    def get_all_products(filters=None, search=None, ordering=None):
        """
        Get all products with optional filters and search.
        
        Optimizations:
        - select_related() for ForeignKey (user, category, brand)
        - prefetch_related() for reverse relationships (reviews, images)
        - Only fetch published, active products
        
        Args:
            filters (dict): Filter criteria
                - category (str): Category CID
                - brand (str): Brand BID
                - min_price (float): Minimum price
                - max_price (float): Maximum price
                - status (bool): Active/inactive
            search (str): Search term for title/description/tags
            ordering (str): Field to order by (e.g., '-price', 'title')
        
        Returns:
            QuerySet: Optimized product queryset
        
        Example:
            >>> products = ProductService.get_all_products(
            ...     filters={'category': 'cat123'},
            ...     search='shirt',
            ...     ordering='-date'
            ... )
            >>> products.count()
            15
        """
        # Start with base queryset
        queryset = Product.objects.filter(
            status=True,
            product_status='published'
        )
        
        # OPTIMIZATION: Reduce database queries for related data
        # select_related() for single foreign key lookups
        queryset = queryset.select_related(
            'user',      # Profile info
            'category',  # Category name
            'brand'      # Brand name
        )
        
        # prefetch_related() for reverse relationships
        queryset = queryset.prefetch_related(
            'product_images',  # Multiple images per product
            'reviews'          # Multiple reviews per product
        )
        
        # FILTERING: Apply filter criteria
        if filters:
            if 'category' in filters:
                queryset = queryset.filter(category__cid=filters['category'])
                logger.debug(f"Filtered by category: {filters['category']}")
            
            if 'brand' in filters:
                queryset = queryset.filter(brand__bid=filters['brand'])
                logger.debug(f"Filtered by brand: {filters['brand']}")
            
            if 'min_price' in filters and 'max_price' in filters:
                queryset = queryset.filter(
                    price__gte=filters['min_price'],
                    price__lte=filters['max_price']
                )
                logger.debug(
                    f"Filtered by price: ${filters['min_price']}-${filters['max_price']}"
                )
            
            if 'status' in filters:
                queryset = queryset.filter(status=filters['status'])
        
        # SEARCH: Full-text search across multiple fields
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()
            logger.debug(f"Applied search filter: '{search}'")
        
        # ORDERING: Sort results
        if ordering:
            queryset = queryset.order_by(ordering)
            logger.debug(f"Ordered by: {ordering}")
        else:
            queryset = queryset.order_by('-date')  # Default: newest first
        
        logger.info(f"ProductService.get_all_products() returned {queryset.count()} products")
        return queryset
    
    @staticmethod
    def get_product_by_id(product_id):
        """
        Get single product with all related data efficiently.
        
        Args:
            product_id (str): Product PID
        
        Returns:
            Product: Product instance with all related data loaded
        
        Raises:
            Http404: If product not found or not published
        
        Example:
            >>> product = ProductService.get_product_by_id('prod123')
            >>> product.category.title
            'Men's Fashion'
        """
        product = Product.objects.select_related(
            'user', 'category', 'brand'
        ).prefetch_related(
            'product_images',
            'reviews',
            'reviews__user'
        ).get(pid=product_id, status=True, product_status='published')
        
        logger.info(f"Retrieved product: {product.title} ({product_id})")
        return product
    
    @staticmethod
    def get_product_with_ratings(product_id):
        """
        Get product with average rating calculated.
        
        Args:
            product_id (str): Product PID
        
        Returns:
            dict: Product data with average rating and review count
        
        Example:
            >>> data = ProductService.get_product_with_ratings('prod123')
            >>> data['average_rating']
            4.5
            >>> data['review_count']
            12
        """
        product = ProductService.get_product_by_id(product_id)
        
        # Calculate ratings efficiently
        review_stats = product.reviews.aggregate(
            avg_rating=Avg('rating'),
            review_count=Count('id')
        )
        
        return {
            'product': product,
            'average_rating': round(review_stats['avg_rating'] or 0, 1),
            'review_count': review_stats['review_count'] or 0,
        }
    
    @staticmethod
    def get_featured_products(limit=10):
        """Get featured products (curated, hand-picked items)"""
        queryset = Product.objects.filter(
            status=True,
            featured=True,
            product_status='published'
        ).select_related(
            'category', 'brand'
        ).prefetch_related(
            'reviews'
        )[:limit]
        
        logger.debug(f"Retrieved {queryset.count()} featured products")
        return queryset
    
    @staticmethod
    def get_related_products(product_id, limit=5):
        """
        Get products related by category (content-based similarity).
        
        Args:
            product_id (str): Product PID to find relations for
            limit (int): Maximum number of related products
        
        Returns:
            QuerySet: Related products in same category
        """
        product = get_object_or_404(Product, pid=product_id)
        
        related = Product.objects.filter(
            category=product.category,
            status=True,
            product_status='published'
        ).exclude(
            pid=product_id
        ).select_related(
            'category', 'brand'
        ).prefetch_related(
            'reviews'
        )[:limit]
        
        logger.debug(f"Retrieved {related.count()} products related to {product_id}")
        return related
    
    @staticmethod
    def get_categories():
        """Get all product categories"""
        return Category.objects.all()
    
    @staticmethod
    def get_brands():
        """Get all product brands"""
        return Brand.objects.all()
    
    @staticmethod
    def track_product_view(user, product):
        """
        Track that a user viewed a product.
        Used by analytics for popularity calculations.
        
        Args:
            user (User): User viewing product
            product (Product): Product being viewed
        
        Returns:
            ProductView: The created view record
        """
        view = ProductView.objects.create(
            user=user,
            product=product
        )
        logger.debug(f"Tracked view: {user.email} viewed {product.title}")
        return view