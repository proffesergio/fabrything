"""
Services Package - Business logic layer

Services organize reusable business logic separate from HTTP views.
This makes code testable, reusable, and maintainable.

Services included:
- ProductService: Product retrieval and filtering
- AnalyticsService: User segmentation and popularity scoring
- RecommendationService: Personalized recommendations
- CachingService: Caching layer with TTL
- UserPreferenceService: User preference management

Usage:
    from fabrythingapp.services import ProductService, RecommendationService
    
    products = ProductService.get_all_products(filters={'category': 'cat123'})
    recommendations = RecommendationService.get_personalized_recommendations(user_id=5)
"""

from .product_service import ProductService
from .analytics_service import AnalyticsService
from .recommendation_service import RecommendationService
from .caching_service import CachingService
from .user_preference_service import UserPreferenceService

__all__ = [
    'ProductService',
    'AnalyticsService',
    'RecommendationService',
    'CachingService',
    'UserPreferenceService',
]