"""
User Preference Service - Manage explicit user preferences

Preferences are explicit signals from users about what they like:
- Favorite categories
- Favorite brands
- Price range preferences

Used to personalize recommendations without requiring complex ML.
"""

import logging
from django.shortcuts import get_object_or_404
from fabrythingapp.models import UserPreferences, Category, Brand
from userauthapp.models import User

logger = logging.getLogger(__name__)


class UserPreferenceService:
    """Service for managing user preferences"""
    
    @staticmethod
    def get_or_create_preferences(user_id):
        """Get or create preference record for user"""
        user = get_object_or_404(User, id=user_id)
        preferences, created = UserPreferences.objects.get_or_create(user=user)
        if created:
            logger.info(f"Created preferences for user {user_id}")
        return preferences
    
    @staticmethod
    def add_preferred_category(user_id, category_id):
        """Add category to user's preferences"""
        preferences = UserPreferenceService.get_or_create_preferences(user_id)
        category = get_object_or_404(Category, id=category_id)
        preferences.preferred_categories.add(category)
        logger.debug(f"Added category {category.title} to user {user_id} preferences")
        return preferences
    
    @staticmethod
    def remove_preferred_category(user_id, category_id):
        """Remove category from user's preferences"""
        preferences = UserPreferenceService.get_or_create_preferences(user_id)
        preferences.preferred_categories.remove(category_id)
        logger.debug(f"Removed category {category_id} from user {user_id} preferences")
        return preferences
    
    @staticmethod
    def add_preferred_brand(user_id, brand_id):
        """Add brand to user's preferences"""
        preferences = UserPreferenceService.get_or_create_preferences(user_id)
        brand = get_object_or_404(Brand, id=brand_id)
        preferences.preferred_brands.add(brand)
        logger.debug(f"Added brand {brand.title} to user {user_id} preferences")
        return preferences
    
    @staticmethod
    def set_price_range(user_id, min_price, max_price):
        """Set user's preferred price range"""
        preferences = UserPreferenceService.get_or_create_preferences(user_id)
        preferences.min_price = min_price
        preferences.max_price = max_price
        preferences.save()
        logger.debug(f"Set price range ${min_price}-${max_price} for user {user_id}")
        return preferences
    
    @staticmethod
    def get_preferences(user_id):
        """Get user preferences"""
        return UserPreferenceService.get_or_create_preferences(user_id)