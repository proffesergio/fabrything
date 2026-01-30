"""
Analytics Service - User segmentation and product scoring

This service handles all analytics operations including:
1. User Segmentation - Classify users into behavioral groups
2. Popularity Scoring - Calculate product popularity metrics
3. Trend Analysis - Identify trending products

User Segments:
- new_user: Created < 7 days ago, no purchases
- active_user: 1-2 purchases, $100-$500 total spend
- frequent_buyer: 3+ purchases, $500+ total spend
- dormant_user: No activity > 30 days OR created but never purchased

Popularity Score Formula:
    score = (review_count * 0.3 + avg_rating * 0.4 + view_count * 0.3) * 100 / 3
    
    - Reviews (30%): Social proof
    - Rating (40%): Quality indicator
    - Views (30%): Popularity signal

Architecture:
    RecommendationService → AnalyticsService → Product/Review/User Models
    
    The analytics service provides data that other services depend on.
"""

import logging
from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q, F, DecimalField
from django.db.models.functions import Cast
from django.conf import settings
from fabrythingapp.models import (
    Product, ProductReview, ProductView, CartOrder, CartOrderItems, User
)

logger = logging.getLogger(__name__)

# Get configuration from settings
CONFIG = settings.RECOMMENDATION_CONFIG


class AnalyticsService:
    """Service for analytics operations"""
    
    @staticmethod
    def get_user_segment(user_id):
        """
        Classify user into behavioral segment.
        
        Segmentation Logic:
        1. Check if new_user: Created < 7 days ago
        2. Check if frequent_buyer: 3+ purchases AND $500+ spend
        3. Check if dormant: No purchases in 30+ days
        4. Otherwise: active_user
        
        Args:
            user_id (int): User ID
        
        Returns:
            str: User segment ('new_user', 'active_user', 'frequent_buyer', 'dormant_user')
        
        Example:
            >>> segment = AnalyticsService.get_user_segment(user_id=5)
            >>> segment
            'active_user'
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.warning(f"User {user_id} not found for segmentation")
            return 'new_user'
        
        # Check if new user (created < 7 days ago)
        user_age_days = (timezone.now() - user.date_joined).days
        if user_age_days < CONFIG['new_user_days']:
            logger.debug(f"User {user_id} classified as: new_user (age: {user_age_days} days)")
            return 'new_user'
        
        # Get purchase statistics
        purchases = CartOrder.objects.filter(
            user=user,
            paid_status=True
        )
        purchase_count = purchases.count()
        
        # Calculate total spend
        total_spent = purchases.aggregate(
            total=Sum('price', output_field=DecimalField())
        )['total'] or 0
        
        # Check if frequent buyer (3+ purchases AND $500+ spend)
        if (purchase_count >= CONFIG['frequent_buyer_purchases'] and
            float(total_spent) >= CONFIG['frequent_buyer_spend_threshold']):
            logger.debug(
                f"User {user_id} classified as: frequent_buyer "
                f"(purchases: {purchase_count}, spend: ${total_spent})"
            )
            return 'frequent_buyer'
        
        # Check if active user (1-2 purchases, $100-$500 spend)
        if (0 < purchase_count < CONFIG['frequent_buyer_purchases'] and
            CONFIG['active_user_spend_threshold'] <= float(total_spent) < CONFIG['frequent_buyer_spend_threshold']):
            logger.debug(
                f"User {user_id} classified as: active_user "
                f"(purchases: {purchase_count}, spend: ${total_spent})"
            )
            return 'active_user'
        
        # Check if dormant (no purchases in 30+ days OR created 30+ days ago but never purchased)
        if purchase_count == 0:
            # Never made a purchase
            if user_age_days >= CONFIG['dormant_days']:
                logger.debug(
                    f"User {user_id} classified as: dormant_user "
                    f"(age: {user_age_days} days, never purchased)"
                )
                return 'dormant_user'
        else:
            # Has made purchases, check last purchase date
            last_purchase = purchases.order_by('-order_date').first()
            days_since_purchase = (timezone.now() - last_purchase.order_date).days
            if days_since_purchase >= CONFIG['dormant_days']:
                logger.debug(
                    f"User {user_id} classified as: dormant_user "
                    f"(last purchase {days_since_purchase} days ago)"
                )
                return 'dormant_user'
        
        # Default: active user
        logger.debug(
            f"User {user_id} classified as: active_user (default)"
        )
        return 'active_user'
    
    @staticmethod
    def calculate_product_popularity_score(product_id):
        """
        Calculate product popularity score (0-100).
        
        Formula:
            score = (review_count * 0.3 + avg_rating * 0.4 + view_count * 0.3) * 100 / 3
        
        Weights:
        - Review Count (30%): How many people reviewed (social proof)
        - Average Rating (40%): Quality indicator (most important)
        - View Count (30%): How many times viewed (popularity signal)
        
        Args:
            product_id (str): Product PID
        
        Returns:
            float: Popularity score between 0-100
        
        Example:
            >>> score = AnalyticsService.calculate_product_popularity_score('prod123')
            >>> score
            75.5
        """
        try:
            product = Product.objects.get(pid=product_id)
        except Product.DoesNotExist:
            logger.warning(f"Product {product_id} not found for scoring")
            return 0.0
        
        # Get review statistics
        review_stats = ProductReview.objects.filter(
            product=product
        ).aggregate(
            count=Count('id'),
            avg_rating=Avg('rating')
        )
        
        review_count = review_stats['count'] or 0
        avg_rating = review_stats['avg_rating'] or 0
        
        # Get view count
        view_count = ProductView.objects.filter(product=product).count()
        
        # Normalize values (cap at reasonable maximums)
        # Review count: normalize to 0-1 scale (max 100 reviews)
        normalized_reviews = min(review_count / 100, 1.0)
        
        # Rating: already 0-5 scale, normalize to 0-1
        normalized_rating = (avg_rating / 5.0) if avg_rating > 0 else 0
        
        # View count: normalize to 0-1 scale (max 1000 views)
        normalized_views = min(view_count / 1000, 1.0)
        
        # Calculate weighted score
        weights = CONFIG
        score = (
            (normalized_reviews * weights['review_weight']) +
            (normalized_rating * weights['rating_weight']) +
            (normalized_views * weights['view_weight'])
        ) * 100
        
        logger.debug(
            f"Product {product_id} popularity score: {score:.2f} "
            f"(reviews: {review_count}, rating: {avg_rating:.1f}, views: {view_count})"
        )
        
        return round(score, 2)
    
    @staticmethod
    def get_trending_products(days=None, limit=None):
        """
        Get trending products (recently popular items).
        
        Trending = Products with highest popularity score in recent period
        
        Args:
            days (int): Look back X days (default from settings)
            limit (int): Maximum products to return (default from settings)
        
        Returns:
            QuerySet: Top trending products
        
        Example:
            >>> trending = AnalyticsService.get_trending_products(days=7, limit=10)
            >>> trending.count()
            10
        """
        if days is None:
            days = CONFIG['trending_days']
        if limit is None:
            limit = CONFIG['trending_limit']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Products with recent views or reviews are trending
        trending_products = Product.objects.annotate(
            recent_views=Count(
                'views',
                filter=Q(views__viewed_at__gte=cutoff_date)
            ),
            recent_reviews=Count(
                'reviews',
                filter=Q(reviews__date__gte=cutoff_date)
            ),
            avg_rating=Avg('reviews__rating')
        ).filter(
            Q(recent_views__gt=0) | Q(recent_reviews__gt=0),
            status=True,
            product_status='published'
        ).select_related(
            'category', 'brand'
        ).order_by(
            '-recent_views', '-recent_reviews', '-avg_rating'
        )[:limit]
        
        logger.info(f"Retrieved {trending_products.count()} trending products (last {days} days)")
        return trending_products
    
    @staticmethod
    def get_popular_products_by_category(category_id=None, limit=None):
        """
        Get most popular products (optionally by category).
        
        Popular = Products with highest all-time popularity score
        
        Args:
            category_id (str): Category CID (optional)
            limit (int): Maximum products (default from settings)
        
        Returns:
            QuerySet: Most popular products
        """
        if limit is None:
            limit = CONFIG['popular_limit']
        
        queryset = Product.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating'),
            view_count=Count('views')
        ).filter(
            status=True,
            product_status='published'
        )
        
        if category_id:
            queryset = queryset.filter(category__cid=category_id)
        
        # Order by: reviews (social proof) → rating (quality) → views (popularity)
        queryset = queryset.select_related(
            'category', 'brand'
        ).order_by(
            '-review_count', '-avg_rating', '-view_count'
        )[:limit]
        
        logger.info(f"Retrieved {queryset.count()} popular products")
        return queryset
    
    @staticmethod
    def get_user_purchase_categories(user_id):
        """
        Get categories user has purchased from (identifies preferences).
        
        Args:
            user_id (int): User ID
        
        Returns:
            list: List of Category objects ordered by frequency
        """
        categories = Product.objects.filter(
            cartorderitems__order__user_id=user_id,
            cartorderitems__order__paid_status=True
        ).values_list('category', flat=True).distinct()
        
        from fabrythingapp.models import Category
        cats = Category.objects.filter(id__in=categories)
        logger.debug(f"User {user_id} has purchased from {cats.count()} categories")
        return cats
    
    @staticmethod
    def get_user_total_spend(user_id):
        """Get total amount user has spent"""
        total = CartOrder.objects.filter(
            user_id=user_id,
            paid_status=True
        ).aggregate(
            total=Sum('price', output_field=DecimalField())
        )['total'] or 0
        return float(total)
    
    @staticmethod
    def get_user_purchase_count(user_id):
        """Get number of purchases user has made"""
        return CartOrder.objects.filter(
            user_id=user_id,
            paid_status=True
        ).count()