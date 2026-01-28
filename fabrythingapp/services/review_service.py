import logging
from django.shortcuts import get_object_or_404
from fabrythingapp.models import ProductReview, Product
from userauthapp.models import User

logger = logging.getLogger(__name__)

class ReviewService:
    """Service layer for Review operations"""
    
    @staticmethod
    def create_review(user_id, product_id, rating, review_text, review_heading=None):
        """Create a new product review"""
        user = get_object_or_404(User, id=user_id)
        product = get_object_or_404(Product, pid=product_id)
        
        # Check if user already reviewed this product
        existing_review = ProductReview.objects.filter(
            user=user,
            product=product
        ).first()
        
        if existing_review:
            logger.warning(f"User {user.id} already reviewed product {product.pid}")
            return None, "You have already reviewed this product"
        
        review = ProductReview.objects.create(
            user=user,
            product=product,
            rating=rating,
            review=review_text,
            review_heading=review_heading
        )
        
        logger.info(f"Created review {review.id} for product {product.pid}")
        return review, "Review created successfully"
    
    @staticmethod
    def get_product_reviews(product_id, ordering=None):
        """Get all reviews for a product"""
        product = get_object_or_404(Product, pid=product_id)
        reviews = ProductReview.objects.filter(product=product)
        
        if ordering:
            reviews = reviews.order_by(ordering)
        
        return reviews
    
    @staticmethod
    def update_review(review_id, rating=None, review_text=None, review_heading=None):
        """Update an existing review"""
        review = get_object_or_404(ProductReview, id=review_id)
        
        if rating is not None:
            review.rating = rating
        if review_text is not None:
            review.review = review_text
        if review_heading is not None:
            review.review_heading = review_heading
        
        review.save()
        logger.info(f"Updated review {review_id}")
        return review
    
    @staticmethod
    def delete_review(review_id):
        """Delete a review"""
        review = get_object_or_404(ProductReview, id=review_id)
        product_id = review.product.pid
        review.delete()
        logger.info(f"Deleted review {review_id} for product {product_id}")
        return True