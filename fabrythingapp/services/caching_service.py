"""
Caching Service - Intelligent caching with TTL management

This service provides an abstraction layer for caching, making it easy to:
1. Cache recommendation results with configurable TTL
2. Invalidate cache when needed
3. Monitor cache performance
4. Switch cache backends (Django cache → Redis) without changing code

Caching Layers:
1. Django's cache framework (default: database backend for dev)
2. RecommendationCache model (persistent, queryable cache)

Cache Keys Pattern:
    recommendation:{user_id}:{cache_type}:{category_id}
    trending:products:7_days
    popular:products
    similar:{product_id}

TTL Strategy:
    - Popular: 24 hours (stable data, changes slowly)
    - Trending: 6 hours (changes daily)
    - Personalized: 3 hours (user behavior evolves)

Example:
    from fabrythingapp.services import CachingService
    
    # Get from cache or generate fresh
    recs = CachingService.get_recommendations(
        cache_key='rec:user5',
        generator_func=RecommendationService.get_personalized_recommendations,
        generator_args={'user_id': 5},
        ttl=3600
    )
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from fabrythingapp.models import RecommendationCache

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = settings.CACHE_TIMEOUT


class CachingService:
    """Service for caching operations"""
    
    @staticmethod
    def generate_cache_key(*parts):
        """
        Generate cache key from parts.
        
        Example:
            >>> key = CachingService.generate_cache_key('rec', 'user5', 'popular')
            >>> key
            'rec:user5:popular'
        """
        return ':'.join(str(p) for p in parts)
    
    @staticmethod
    def get_cached_data(cache_key, ttl=None):
        """
        Retrieve data from cache.
        
        Args:
            cache_key (str): Cache key to retrieve
            ttl (int): Optional - if set, check if in RecommendationCache
        
        Returns:
            dict or None: Cached data or None if not found/expired
        """
        try:
            # Try Django cache first (fast)
            data = cache.get(cache_key)
            if data:
                logger.debug(f"Cache HIT: {cache_key}")
                return data
            
            logger.debug(f"Cache MISS: {cache_key}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving cache {cache_key}: {str(e)}")
            return None
    
    @staticmethod
    def set_cached_data(cache_key, data, ttl=3600, cache_type=None, user_id=None):
        """
        Store data in cache.
        
        Args:
            cache_key (str): Cache key
            data: Data to cache (should be JSON-serializable)
            ttl (int): Time-to-live in seconds (default 1 hour)
            cache_type (str): Type of cache ('popular', 'trending', 'personalized', 'similar')
            user_id (int): Optional user ID if personalized
        
        Returns:
            bool: Success status
        """
        try:
            # Store in Django cache
            cache.set(cache_key, data, ttl)
            logger.debug(f"Cache SET: {cache_key} (TTL: {ttl}s)")
            
            # Also store in RecommendationCache model for querying/monitoring
            if cache_type:
                expires_at = timezone.now() + timedelta(seconds=ttl)
                RecommendationCache.objects.update_or_create(
                    cache_key=cache_key,
                    defaults={
                        'cache_type': cache_type,
                        'user': None if user_id is None else user_id,
                        'recommendations_data': data if isinstance(data, list) else [data],
                        'expires_at': expires_at,
                        'hit_count': 0,
                    }
                )
            
            return True
        except Exception as e:
            logger.error(f"Error setting cache {cache_key}: {str(e)}")
            return False
    
    @staticmethod
    def invalidate_cache(cache_key):
        """
        Remove entry from cache.
        
        Args:
            cache_key (str): Cache key to invalidate
        """
        try:
            cache.delete(cache_key)
            RecommendationCache.objects.filter(cache_key=cache_key).delete()
            logger.debug(f"Cache INVALIDATED: {cache_key}")
        except Exception as e:
            logger.error(f"Error invalidating cache {cache_key}: {str(e)}")
    
    @staticmethod
    def invalidate_user_cache(user_id):
        """Invalidate all cache entries for a user"""
        cache_keys = [
            CachingService.generate_cache_key('rec', user_id, 'personalized'),
            CachingService.generate_cache_key('rec', user_id, 'segment'),
        ]
        for key in cache_keys:
            CachingService.invalidate_cache(key)
        logger.info(f"Invalidated all cache for user {user_id}")
    
    @staticmethod
    def get_or_generate(cache_key, generator_func, generator_args=None, 
                       ttl=3600, cache_type=None, user_id=None):
        """
        Get cached data or generate fresh if not cached.
        
        This is the main method you'll use. It handles:
        1. Checking cache
        2. Generating if missing
        3. Storing result
        4. Returning data
        
        Args:
            cache_key (str): Cache key
            generator_func (callable): Function to call if cache miss
            generator_args (dict): Arguments for generator function
            ttl (int): Cache TTL in seconds
            cache_type (str): Type of cache for monitoring
            user_id (int): User ID if personalized
        
        Returns:
            Any: Cached or freshly generated data
        
        Example:
            from fabrythingapp.services import CachingService, RecommendationService
            
            recs = CachingService.get_or_generate(
                cache_key='rec:user5:personalized',
                generator_func=RecommendationService.get_personalized_recommendations,
                generator_args={'user_id': 5},
                ttl=10800,
                cache_type='personalized',
                user_id=5
            )
        """
        # Try to get from cache
        cached_data = CachingService.get_cached_data(cache_key, ttl)
        if cached_data is not None:
            # Update hit count
            RecommendationCache.objects.filter(
                cache_key=cache_key
            ).update(hit_count=F('hit_count') + 1)
            return cached_data
        
        # Generate fresh data
        try:
            if generator_args is None:
                generator_args = {}
            
            logger.info(f"Generating cache for {cache_key}")
            data = generator_func(**generator_args)
            
            # Store in cache
            CachingService.set_cached_data(
                cache_key, data, ttl, cache_type, user_id
            )
            
            return data
        except Exception as e:
            logger.error(f"Error generating cache for {cache_key}: {str(e)}")
            return None
    
    @staticmethod
    def cleanup_expired_cache():
        """
        Delete expired cache entries from RecommendationCache model.
        
        Run this periodically (hourly) via Celery task.
        
        Example:
            # In Django management command or Celery task
            CachingService.cleanup_expired_cache()
        """
        expired = RecommendationCache.objects.filter(
            expires_at__lt=timezone.now()
        )
        count = expired.count()
        expired.delete()
        logger.info(f"Cleaned up {count} expired cache entries")
        return count
    
    @staticmethod
    def get_cache_stats():
        """Get cache performance statistics"""
        stats = RecommendationCache.objects.aggregate(
            total_entries=Count('id'),
            total_hits=Sum('hit_count'),
            avg_hits=Avg('hit_count'),
        )
        logger.debug(f"Cache stats: {stats}")
        return stats


# Import for easier access in services/__init__.py
from django.db.models import Sum, Avg, Count, F