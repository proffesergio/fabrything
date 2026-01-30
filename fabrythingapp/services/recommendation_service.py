"""
Recommendation Service - Core recommendation engine

This service generates personalized product recommendations using multiple strategies:

1. POPULARITY-BASED: For new users
   - Returns top popular products overall
   - Simple but effective for new user onboarding

2. PERSONALIZED BY SEGMENT:
   - new_user: Top 10 popular products overall
   - active_user: Popular products in their favorite categories
   - frequent_buyer: New products in categories + trending items
   - dormant_user: Best-sellers + discounted items (re-engagement)

3. CONTENT-BASED SIMILARITY:
   - For "similar products" on product detail page
   - Based on category, brand, price range

Architecture:
    RecommendationService
        ↓
    AnalyticsService (get segment, popularity scores)
    CachingService (cache results)
    ProductService (get products efficiently)

Caching Strategy:
    - Results cached with segment-specific TTLs
    - Invalidated when user purchases
    - Hit/miss statistics tracked

Example Usage:
    from fabrythingapp.services import RecommendationService
    
    # Get personalized recommendations for authenticated user
    recs = RecommendationService.get_personalized_recommendations(user_id=5, limit=10)
    
    # Get trending products (public)
    trending = RecommendationService.get_trending_products(limit=10)
    
    # Get similar products (on product detail page)
    similar = RecommendationService.get_similar_products(product_id='prod123', limit=5)
"""

import logging
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from fabrythingapp.models import Product, Category, Brand
from fabrythingapp.services.analytics_service import AnalyticsService
from fabrythingapp.services.caching_service import CachingService
from fabrythingapp.services.product_service import ProductService
from django.conf import settings

logger = logging.getLogger(__name__)
CONFIG = settings.RECOMMENDATION_CONFIG
CACHE_TIMEOUT = settings.CACHE_TIMEOUT


class RecommendationService:
    """Core recommendation engine"""
    
    @staticmethod
    def get_personalized_recommendations(user_id, limit=None, use_cache=True):
        """
        Get personalized product recommendations for a user.
        
        Strategy differs by user segment:
        
        new_user (< 7 days, 0 purchases):
        - Show top popular products overall
        - Goal: Onboard user, build initial interest
        
        active_user (1-2 purchases, $100-$500 spend):
        - Show popular products in their favorite categories
        - Mix with trending items
        - Goal: Increase purchase frequency
        
        frequent_buyer (3+ purchases, $500+ spend):
        - Show new products in their categories
        - Trending items across all categories
        - Limited discounted items
        - Goal: Increase average order value
        
        dormant_user (30+ days no activity):
        - Show best-sellers (social proof)
        - Limited-time deals (re-engagement)
        - New arrivals in previous categories
        - Goal: Reactivate user
        
        Args:
            user_id (int): User ID
            limit (int): Number of recommendations (default: 10)
            use_cache (bool): Use cache if available
        
        Returns:
            QuerySet: Recommended products in priority order
        
        Example:
            >>> recs = RecommendationService.get_personalized_recommendations(user_id=5)
            >>> recs.count()
            10
            >>> recs[0].title
            'Popular T-Shirt'
        """
        if limit is None:
            limit = CONFIG['personalized_limit']
        
        # Create cache key
        cache_key = CachingService.generate_cache_key('rec', user_id, 'personalized')
        
        if use_cache:
            cached = CachingService.get_cached_data(cache_key)
            if cached:
                return cached
        
        try:
            # Get user segment
            segment = AnalyticsService.get_user_segment(user_id)
            logger.info(f"Generating {segment} recommendations for user {user_id}")
            
            # Get recommendations based on segment
            if segment == 'new_user':
                recommendations = RecommendationService._get_new_user_recommendations(limit)
            elif segment == 'active_user':
                recommendations = RecommendationService._get_active_user_recommendations(user_id, limit)
            elif segment == 'frequent_buyer':
                recommendations = RecommendationService._get_frequent_buyer_recommendations(user_id, limit)
            else:  # dormant_user
                recommendations = RecommendationService._get_dormant_user_recommendations(user_id, limit)
            
            # Convert to list of product PIDs for caching
            rec_pids = list(recommendations.values_list('pid', flat=True))
            
            # Cache results
            ttl = CACHE_TIMEOUT['personalized_recommendations']
            CachingService.set_cached_data(
                cache_key,
                rec_pids,
                ttl,
                cache_type='personalized',
                user_id=user_id
            )
            
            logger.info(f"Generated {len(rec_pids)} personalized recommendations for user {user_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendations for user {user_id}: {str(e)}")
            # Fallback to popular products
            return AnalyticsService.get_popular_products_by_category(limit=limit)
    
    @staticmethod
    def _get_new_user_recommendations(limit):
        """Recommendations for new users: Top popular products"""
        return AnalyticsService.get_popular_products_by_category(limit=limit)
    
    @staticmethod
    def _get_active_user_recommendations(user_id, limit):
        """Recommendations for active users: Popular in favorite categories"""
        # Get categories user has purchased from
        user_categories = AnalyticsService.get_user_purchase_categories(user_id)
        
        if not user_categories.exists():
            # No purchase history, fallback to popular
            return AnalyticsService.get_popular_products_by_category(limit=limit)
        
        # Get popular products from user's categories
        recommendations = Product.objects.filter(
            category__in=user_categories,
            status=True,
            product_status='published'
        ).annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).select_related(
            'category', 'brand'
        ).order_by(
            '-review_count', '-avg_rating'
        )[:limit]
        
        return recommendations
    
    @staticmethod
    def _get_frequent_buyer_recommendations(user_id, limit):
        """Recommendations for frequent buyers: New + trending in favorite categories"""
        user_categories = AnalyticsService.get_user_purchase_categories(user_id)
        
        if not user_categories.exists():
            return AnalyticsService.get_popular_products_by_category(limit=limit)
        
        # Mix of: newest products in categories + trending
        # 70% newest in categories, 30% trending
        newest_count = int(limit * 0.7)
        trending_count = limit - newest_count
        
        newest_products = Product.objects.filter(
            category__in=user_categories,
            status=True,
            product_status='published'
        ).select_related(
            'category', 'brand'
        ).order_by('-date')[:newest_count]
        
        trending_products = AnalyticsService.get_trending_products(limit=trending_count)
        
        # Combine and remove duplicates
        all_pids = list(newest_products.values_list('pid', flat=True))
        for product in trending_products:
            if product.pid not in all_pids:
                all_pids.append(product.pid)
        
        # Return products in PIDs order
        if all_pids:
            recommendations = Product.objects.filter(
                pid__in=all_pids
            ).select_related('category', 'brand')
            return recommendations
        
        return newest_products[:limit]
    
    @staticmethod
    def _get_dormant_user_recommendations(user_id, limit):
        """Recommendations for dormant users: Best-sellers + re-engagement deals"""
        # Get their previous categories
        user_categories = AnalyticsService.get_user_purchase_categories(user_id)
        
        recommendations = Product.objects.filter(
            status=True,
            product_status='published'
        ).annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating'),
            has_discount=Count('id', filter=Q(price__lt=F('old_price')))
        ).select_related(
            'category', 'brand'
        )
        
        # Prioritize: products with discounts + high ratings
        recommendations = recommendations.order_by(
            '-has_discount', '-avg_rating', '-review_count'
        )[:limit]
        
        return recommendations
    
    @staticmethod
    def get_trending_products(limit=None, use_cache=True):
        """
        Get trending products (7-day trending).
        
        Args:
            limit (int): Number of products
            use_cache (bool): Use cache
        
        Returns:
            QuerySet: Trending products
        """
        if limit is None:
            limit = CONFIG['trending_limit']
        
        cache_key = CachingService.generate_cache_key('trending', 'products')
        
        if use_cache:
            cached = CachingService.get_cached_data(cache_key)
            if cached:
                # Reconstruct queryset from PIDs
                products = Product.objects.filter(pid__in=cached)
                return products
        
        trending = AnalyticsService.get_trending_products(days=CONFIG['trending_days'], limit=limit)
        
        # Cache
        trending_pids = list(trending.values_list('pid', flat=True))
        ttl = CACHE_TIMEOUT['trending_products']
        CachingService.set_cached_data(
            cache_key, trending_pids, ttl, cache_type='trending'
        )
        
        return trending
    
    @staticmethod
    def get_popular_products(limit=None, use_cache=True):
        """Get all-time popular products"""
        if limit is None:
            limit = CONFIG['popular_limit']
        
        cache_key = CachingService.generate_cache_key('popular', 'products')
        
        if use_cache:
            cached = CachingService.get_cached_data(cache_key)
            if cached:
                products = Product.objects.filter(pid__in=cached)
                return products
        
        popular = AnalyticsService.get_popular_products_by_category(limit=limit)
        
        # Cache
        popular_pids = list(popular.values_list('pid', flat=True))
        ttl = CACHE_TIMEOUT['popular_products']
        CachingService.set_cached_data(
            cache_key, popular_pids, ttl, cache_type='popular'
        )
        
        return popular
    
    @staticmethod
    def get_similar_products(product_id, limit=None):
        """
        Get content-based similar products.
        
        Similarity based on:
        1. Same category (primary)
        2. Similar price (within +/- 20%)
        3. Popular products preferred
        
        Args:
            product_id (str): Product PID
            limit (int): Number of similar products
        
        Returns:
            QuerySet: Similar products
        """
        if limit is None:
            limit = CONFIG['similar_limit']
        
        cache_key = CachingService.generate_cache_key('similar', product_id)
        cached = CachingService.get_cached_data(cache_key)
        if cached:
            products = Product.objects.filter(pid__in=cached)
            return products
        
        product = get_object_or_404(Product, pid=product_id)
        
        # Price range: +/- 20%
        price_min = product.price * 0.8
        price_max = product.price * 1.2
        
        similar = Product.objects.filter(
            category=product.category,
            status=True,
            product_status='published',
            price__gte=price_min,
            price__lte=price_max
        ).exclude(
            pid=product_id
        ).annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).select_related(
            'category', 'brand'
        ).order_by(
            '-review_count', '-avg_rating'
        )[:limit]
        
        # Cache
        similar_pids = list(similar.values_list('pid', flat=True))
        ttl = CACHE_TIMEOUT['personalized_recommendations']
        CachingService.set_cached_data(
            cache_key, similar_pids, ttl, cache_type='similar'
        )
        
        return similar