from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg
from fabrythingapp.services.analytics_service import AnalyticsService
from fabrythingapp.services.recommendation_service import RecommendationService
from fabrythingapp.services.user_preference_service import UserPreferenceService
from taggit.models import Tag
from fabrythingapp.forms import ProductReviewForm
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from decimal import Decimal
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
import logging
from fabrythingapp.forms import ProductReviewForm

logger = logging.getLogger(__name__)

from fabrythingapp.models import (
    Cart, CartItem, OrderStatus, Product, Category, Brand, ProductImages, ProductReview,
    CartOrder, CartOrderItems, ShippingMethod, UserPreferences, Wishlist, Address
)
from fabrythingapp.serializers import (
    CartItemSerializer, CartSerializer, CheckoutSerializer, OrderConfirmationSerializer, 
    OrderDetailSerializer, OrderListSerializer, OrderStatusSerializer, 
    ProductFilterFacetsSerializer, ProductSerializer, ProductDetailSerializer, 
    CategorySerializer, BrandSerializer, ProductReviewSerializer, CartOrderSerializer,
    CartOrderItemsSerializer, RecommendationProductSerializer, ShippingMethodSerializer, 
    WishlistSerializer, AddressSerializer, UserPreferencesSerializer
)
from fabrythingapp.services import ProductService, ReviewService, CartService

from django.contrib.auth.decorators import login_required

@login_required
def cart_page(request):
    return render(request, 'core/cart.html')

@login_required
def checkout_page(request):
    return render(request, 'core/checkout.html')

@login_required
def order_confirmation_page(request, order_id):
    return render(request, 'core/order-confirmation.html', {'order_id': order_id})

@login_required
def my_orders_page(request):
    return render(request, 'core/my-orders.html')

logger = logging.getLogger(__name__)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Product operations
    Endpoints:
    - GET /api/v1/products/ - List all products
    - GET /api/v1/products/{pid}/ - Get product details
    - GET /api/v1/products/featured/ - Get featured products
    - GET /api/v1/products/{pid}/related/ - Get related products
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'brand', 'status']
    search_fields = ['title', 'description', 'tags__name']
    ordering_fields = ['price', 'date', 'title']
    ordering = ['-date']
    
    def get_queryset(self):
        return ProductService.get_all_products()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        products = ProductService.get_featured_products()
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """Get related products"""
        products = ProductService.get_related_products(pk)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Category operations
    Endpoints:
    - GET /api/v1/categories/ - List all categories
    - GET /api/v1/categories/{cid}/ - Get category details
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Brand operations
    Endpoints:
    - GET /api/v1/brands/ - List all brands
    - GET /api/v1/brands/{bid}/ - Get brand details
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProductReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProductReview operations
    Endpoints:
    - GET /api/v1/reviews/ - List all reviews
    - POST /api/v1/reviews/ - Create review
    - GET /api/v1/reviews/{id}/ - Get review details
    - PUT /api/v1/reviews/{id}/ - Update review
    - DELETE /api/v1/reviews/{id}/ - Delete review
    """
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['product', 'rating']
    ordering = ['-date']
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ProductReview.objects.all()
        return ProductReview.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        # Ensure user can only update their own reviews
        if serializer.instance.user != self.request.user:
            return Response(
                {'detail': 'You can only update your own reviews'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def create_review(self, request):
        """Create a new review"""
        product_id = request.data.get('product_id')
        rating = request.data.get('rating')
        review_text = request.data.get('review')
        review_heading = request.data.get('review_heading')
        
        review, message = ReviewService.create_review(
            request.user.id, product_id, rating, review_text, review_heading
        )
        
        if review:
            serializer = self.get_serializer(review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)

class CartOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CartOrder operations
    Endpoints:
    - GET /api/v1/cart/ - Get current user's cart
    - POST /api/v1/cart/add-item/ - Add item to cart
    - POST /api/v1/cart/remove-item/ - Remove item from cart
    - POST /api/v1/cart/checkout/ - Checkout cart
    """
    serializer_class = CartOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartOrder.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current_cart(self, request):
        """Get current user's cart"""
        cart = CartService.create_or_get_cart(request.user.id)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        try:
            cart_item = CartService.add_to_cart(request.user.id, product_id, quantity)
            cart = CartService.create_or_get_cart(request.user.id)
            serializer = self.get_serializer(cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error adding to cart: {str(e)}")
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from cart"""
        product_title = request.data.get('item')
        
        if CartService.remove_from_cart(request.user.id, product_title):
            cart = CartService.create_or_get_cart(request.user.id)
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
        
        return Response(
            {'detail': 'Item not found in cart'},
            status=status.HTTP_404_NOT_FOUND
        )

class WishlistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Wishlist operations
    Endpoints:
    - GET /api/v1/wishlist/ - Get user's wishlist
    - POST /api/v1/wishlist/add/ - Add to wishlist
    - POST /api/v1/wishlist/remove/ - Remove from wishlist
    """
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def add(self, request):
        """Add product to wishlist"""
        product_id = request.data.get('product_id')
        
        try:
            wishlist_item, created = CartService.add_to_wishlist(
                request.user.id, product_id
            )
            serializer = self.get_serializer(wishlist_item)
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(serializer.data, status=status_code)
        except Exception as e:
            logger.error(f"Error adding to wishlist: {str(e)}")
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def remove(self, request):
        """Remove product from wishlist"""
        product_id = request.data.get('product_id')
        
        if CartService.remove_from_wishlist(request.user.id, product_id):
            return Response(
                {'detail': 'Removed from wishlist'},
                status=status.HTTP_204_NO_CONTENT
            )
        
        return Response(
            {'detail': 'Item not found in wishlist'},
            status=status.HTTP_404_NOT_FOUND
        )

# Create your views here.
def index(request):
    # products = Product.objects.all()
    products = Product.objects.filter(featured=True, product_status='published', )

    categories = Category.objects.all()

    brands = Brand.objects.all()

    context = {
        'products' : products,
        'categories': categories,
        'brands': brands,
    }
    return render(request, 'core/home.html', context)

def category_list_view(request):
    # categories = Category.objects.all().annotate(product_count=Count('products'))
    categories = Category.objects.all()
    products = Product.objects.all()

    context = {
        'categories':categories,
        'products':products,
    }
    return render(request, 'core/category-list.html', context)

def product_list_view(request):
    # categories = Category.objects.all().annotate(product_count=Count('products'))
    categories = Category.objects.all()
    products = Product.objects.all()

    context = {
        'categories':categories,
        'products':products,
    }
    return render(request, 'core/product-list.html', context)

def get_brands(request):
    brands = Brand.objects.all()
    
    context = {
        'brands':brands,
    }
    return render(request, 'core/home.html', context)

def category_products(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status='published', category=category)

    context = {
        'category':category,
        'products':products,
    }
    return render(request, 'core/category-products.html', context)

def product_details_view(request, pid):
    product = Product.objects.get(pid=pid)
    related_products = Product.objects.filter(category=product.category).exclude(pid=pid)
    reviews = ProductReview.objects.filter(product=product)
    avg_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))


    product_image = product.product_images.all()

    # Product Review Form 
    review_form = ProductReviewForm()

    make_review = True 

    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()

        if user_review_count > 0:
            make_review = False

    context = {
        'product': product,
        'product_image': product_image,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'make_review': make_review,
        'related_products': related_products,
    }
    return render(request, 'core/product-details.html', context)


# Product Details View End 
def tag_list(request, tag_slug=None):

    products = Product.objects.filter(product_status='published').order_by('-id')

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

        context = {
            'products':products,
            'tag': tag,
        }
        return render(request, 'core/tag.html', context)
    
def ajax_add_review(request, pid):
    product = Product.objects.get(pid=pid)
    user = request.user 

    review = ProductReview.objects.create(
        user=user,
        product = product,
        review = request.POST['review'],
        rating = request.POST['rating'],
    )

    context = {
        'user': user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
    }

    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    return JsonResponse(
        {
            'bool': True,
            'context': context,
            'avg_rating': average_rating,
        }
    )

def search_view(request):
    query = request.GET.get("q")
    products = Product.objects.filter(title__icontains=query).order_by("-date")

    context = {
        "products": products,
        "query": query,
    }
    return render(request, 'core/search.html', context)

# Filter Products 
def filter_products(request):
    categories = request.GET.getlist('category[]')

    products = Product.objects.filter(product_status="published").order_by("-id").distinct()
    # Category length must be > 0
    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct() # chaining in python -> product__title__name



    data = render_to_string("core/async/product-list.html", {"products":products})

    return JsonResponse({"data": data})

# ============================================================================
# RECOMMENDATION VIEWSETS
# ============================================================================



class RecommendationViewSet(viewsets.ViewSet):
    """
    ViewSet for product recommendations.
    
    Endpoints:
    - GET /api/v1/recommendations/personalized/ - Personalized for authenticated user
    - GET /api/v1/recommendations/trending/ - 7-day trending products
    - GET /api/v1/recommendations/popular/ - All-time popular products
    
    All endpoints support:
    - ?limit=10 - Number of products to return
    - ?page=1 - Pagination
    - Cache-Control headers for browser caching
    """
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def personalized(self, request):
        """
        Get personalized recommendations for authenticated user.
        
        Returns products based on user's behavioral segment:
        - new_user: Popular products
        - active_user: Popular in favorite categories
        - frequent_buyer: New + trending in categories
        - dormant_user: Best-sellers + discounted items
        
        Query params:
        - ?limit=10 - Number of products
        - ?page=1 - Pagination page
        
        Response: 3-hour cache (user behavior evolves)
        """
        limit = request.query_params.get('limit', 10)
        
        try:
            # Get personalized recommendations using service
            products = RecommendationService.get_personalized_recommendations(
                user_id=request.user.id,
                limit=int(limit),
                use_cache=True
            )
            
            # Get user segment for display
            segment = AnalyticsService.get_user_segment(request.user.id)
            
            # Serialize
            serializer = RecommendationProductSerializer(
                products,
                many=True,
                context={'request': request}
            )
            
            # Add caching headers
            response_data = {
                'products': serializer.data,
                'user_segment': segment,
                'total_count': len(serializer.data),
                'cached': False,  # Could track from service if needed
                'cache_expires_in_minutes': 180  # 3 hours
            }
            
            response = Response(response_data)
            response['Cache-Control'] = 'private, max-age=10800'  # 3 hours
            
            logger.info(f"Returned {len(serializer.data)} personalized recommendations for user {request.user.id}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendations: {str(e)}")
            return Response(
                {'detail': 'Error generating recommendations'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """
        Get trending products (last 7 days).
        
        Trending = Products with high recent engagement
        (views, reviews, sales)
        
        Response: 6-hour cache (changes daily)
        """
        limit = request.query_params.get('limit', 10)
        
        try:
            products = RecommendationService.get_trending_products(
                limit=int(limit),
                use_cache=True
            )
            
            serializer = RecommendationProductSerializer(
                products,
                many=True,
                context={'request': request}
            )
            
            response_data = {
                'products': serializer.data,
                'total_count': len(serializer.data),
                'period_days': 7,
                'cache_expires_in_minutes': 360  # 6 hours
            }
            
            response = Response(response_data)
            response['Cache-Control'] = 'public, max-age=21600'  # 6 hours
            
            logger.info(f"Returned {len(serializer.data)} trending products")
            return response
            
        except Exception as e:
            logger.error(f"Error generating trending recommendations: {str(e)}")
            return Response(
                {'detail': 'Error generating trending products'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Get all-time popular products.
        
        Popular = Highest rated + most reviewed products
        
        Query params:
        - ?category=cat123 - Filter by category (optional)
        - ?limit=10 - Number of products
        
        Response: 24-hour cache (very stable data)
        """
        limit = request.query_params.get('limit', 10)
        category_id = request.query_params.get('category', None)
        
        try:
            if category_id:
                products = AnalyticsService.get_popular_products_by_category(
                    category_id=category_id,
                    limit=int(limit)
                )
            else:
                products = RecommendationService.get_popular_products(
                    limit=int(limit),
                    use_cache=True
                )
            
            serializer = RecommendationProductSerializer(
                products,
                many=True,
                context={'request': request}
            )
            
            response_data = {
                'products': serializer.data,
                'total_count': len(serializer.data),
                'cache_expires_in_minutes': 1440  # 24 hours
            }
            
            response = Response(response_data)
            response['Cache-Control'] = 'public, max-age=86400'  # 24 hours
            
            logger.info(f"Returned {len(serializer.data)} popular products")
            return response
            
        except Exception as e:
            logger.error(f"Error generating popular recommendations: {str(e)}")
            return Response(
                {'detail': 'Error generating popular products'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SimilarProductsViewSet(viewsets.ViewSet):
    """
    ViewSet for similar product discovery.
    
    Endpoint:
    - GET /api/v1/products/{pid}/similar/ - Content-based similar products
    """
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'], url_path='similar/(?P<product_id>[^/.]+)')
    def similar(self, request, product_id=None):
        """
        Get products similar to given product.
        
        Similarity based on:
        1. Same category (primary)
        2. Similar price (±20%)
        3. High ratings/reviews preferred
        
        Query params:
        - ?limit=5 - Number of similar products
        
        Response: 3-hour cache
        """
        limit = request.query_params.get('limit', 5)
        
        try:
            products = RecommendationService.get_similar_products(
                product_id=product_id,
                limit=int(limit)
            )
            
            serializer = RecommendationProductSerializer(
                products,
                many=True,
                context={'request': request}
            )
            
            response_data = {
                'products': serializer.data,
                'total_count': len(serializer.data),
                'cache_expires_in_minutes': 180
            }
            
            response = Response(response_data)
            response['Cache-Control'] = 'private, max-age=10800'
            
            logger.info(f"Returned {len(serializer.data)} similar products for {product_id}")
            return response
            
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error generating similar products: {str(e)}")
            return Response(
                {'detail': 'Error generating similar products'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user preferences.
    
    Endpoints:
    - GET /api/v1/user/preferences/ - Get user preferences
    - PUT /api/v1/user/preferences/ - Update preferences
    - POST /api/v1/user/preferences/add_category/ - Add favorite category
    - POST /api/v1/user/preferences/remove_category/ - Remove favorite category
    - POST /api/v1/user/preferences/add_brand/ - Add favorite brand
    - POST /api/v1/user/preferences/remove_brand/ - Remove favorite brand
    """
    
    serializer_class = UserPreferencesSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get or create preferences for authenticated user"""
        preferences, created = UserPreferences.objects.get_or_create(
            user=self.request.user
        )
        return preferences
    
    def get_queryset(self):
        """Return empty queryset - we use get_object() instead"""
        return UserPreferences.objects.none()
    
    def list(self, request, *args, **kwargs):
        """Get user preferences"""
        preferences = self.get_object()
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update user preferences"""
        preferences = self.get_object()
        serializer = self.get_serializer(
            preferences,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Updated preferences for user {request.user.id}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def add_category(self, request):
        """Add category to preferences"""
        category_id = request.data.get('category_id')
        if not category_id:
            return Response(
                {'detail': 'category_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            UserPreferenceService.add_preferred_category(
                request.user.id,
                category_id
            )
            preferences = self.get_object()
            serializer = self.get_serializer(preferences)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def remove_category(self, request):
        """Remove category from preferences"""
        category_id = request.data.get('category_id')
        if not category_id:
            return Response(
                {'detail': 'category_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        UserPreferenceService.remove_preferred_category(
            request.user.id,
            category_id
        )
        preferences = self.get_object()
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_brand(self, request):
        """Add brand to preferences"""
        brand_id = request.data.get('brand_id')
        if not brand_id:
            return Response(
                {'detail': 'brand_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            UserPreferenceService.add_preferred_brand(
                request.user.id,
                brand_id
            )
            preferences = self.get_object()
            serializer = self.get_serializer(preferences)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def remove_brand(self, request):
        """Remove brand from preferences"""
        brand_id = request.data.get('brand_id')
        if not brand_id:
            return Response(
                {'detail': 'brand_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        UserPreferenceService.remove_preferred_brand(request.user.id, brand_id)
        preferences = self.get_object()
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)


class ProductViewTrackingViewSet(viewsets.ViewSet):
    """
    Track product views for analytics and recommendations.
    
    Endpoint:
    - POST /api/v1/products/{pid}/view/ - Track a product view
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='view/(?P<product_id>[^/.]+)')
    def track_view(self, request, product_id=None):
        """
        Track that user viewed a product.
        
        Called from frontend when product detail page loads.
        Used for:
        - Popularity scoring
        - Trending calculations
        - User behavior analysis
        
        Response: 204 No Content (successful tracking)
        """
        try:
            product = Product.objects.get(pid=product_id)
            ProductService.track_product_view(request.user, product)
            
            logger.debug(f"Tracked view: user {request.user.id} viewed product {product_id}")
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error tracking product view: {str(e)}")
            # Don't fail the main request if tracking fails
            return Response(
                {'detail': 'View tracked with errors'},
                status=status.HTTP_200_OK
            )


class ProductFilterFacetsViewSet(viewsets.ViewSet):
    """
    Get available filter options for product discovery.
    
    Endpoint:
    - GET /api/v1/products/facets/ - Get filter facets with counts
    """
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def facets(self, request):
        """
        Get available categories, brands, and price ranges with product counts.
        
        Used by frontend to build filter UI (sidebar, dropdowns).
        
        Response example:
        {
            "categories": [
                {"cid": "cat1", "title": "Men", "product_count": 45},
                ...
            ],
            "brands": [...],
            "price_ranges": [...]
        }
        
        Response: 12-hour cache (counts relatively stable)
        """
        serializer = ProductFilterFacetsSerializer({})
        data = serializer.data
        
        response = Response(data)
        response['Cache-Control'] = 'public, max-age=43200'  # 12 hours
        
        logger.debug("Returned product filter facets")
        return response

# ============================================================================
# TIER 1: CART & CHECKOUT VIEWSETS
# ============================================================================

# class CheckoutViewSet(viewsets.ViewSet):
#     """
#     ViewSet for checkout process.
    
#     Endpoints:
#     - POST /api/v1/checkout/validate/ - Validate checkout data
#     - POST /api/v1/checkout/confirm/ - Complete checkout and create order
#     """
    
#     permission_classes = [IsAuthenticated]
    
#     @action(detail=False, methods=['post'])
#     def validate(self, request):
#         """Validate checkout data before final confirmation"""
#         serializer = CheckoutSerializer(
#             data=request.data,
#             context={'request': request}
#         )
        
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # Get cart
#             cart = CartOrder.objects.get(
#                 id=serializer.validated_data['cart_id'],
#                 user=request.user,
#                 paid_status=False
#             )
            
#             if not cart.items.exists():
#                 return Response(
#                     {'detail': 'Cart is empty'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             # Get shipping details
#             address = Address.objects.get(
#                 id=serializer.validated_data['shipping_address_id'],
#                 user=request.user
#             )
#             shipping_method = ShippingMethod.objects.get(
#                 id=serializer.validated_data['shipping_method_id'],
#                 is_active=True
#             )
            
#             return Response({
#                 'valid': True,
#                 'cart': CartOrderSerializer(cart).data,
#                 'address': AddressSerializer(address).data,
#                 'shipping_method': ShippingMethodSerializer(shipping_method).data
#             })
            
#         except CartOrder.DoesNotExist:
#             return Response(
#                 {'detail': 'Cart not found'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             logger.error(f"Error validating checkout: {str(e)}")
#             return Response(
#                 {'detail': 'Error validating checkout'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
    
#     @action(detail=False, methods=['post'])
#     def confirm(self, request):
#         """
#         Complete checkout and create order.
        
#         This is the final step that converts cart to order.
#         """
#         serializer = CheckoutSerializer(
#             data=request.data,
#             context={'request': request}
#         )
        
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # Get cart
#             cart = CartOrder.objects.get(
#                 id=serializer.validated_data['cart_id'],
#                 user=request.user,
#                 paid_status=False
#             )
            
#             # Get shipping details
#             address = Address.objects.get(
#                 id=serializer.validated_data['shipping_address_id'],
#                 user=request.user
#             )
#             shipping_method = ShippingMethod.objects.get(
#                 id=serializer.validated_data['shipping_method_id'],
#                 is_active=True
#             )
            
#             # Calculate totals
#             subtotal = sum(item.total for item in cart.items.all())
#             taxes = subtotal * 0.05  # 5% tax (configurable)
#             shipping_cost = shipping_method.cost
#             total = subtotal + taxes + shipping_cost
            
#             # Update order
#             cart.subtotal = subtotal
#             cart.taxes = taxes
#             cart.shipping_cost = shipping_cost
#             cart.price = total
#             cart.shipping_method = shipping_method
#             cart.shipping_address = address
#             cart.payment_method = serializer.validated_data['payment_method']
#             cart.coupon_code = serializer.validated_data.get('coupon_code', '')
#             cart.notes = serializer.validated_data.get('notes', '')
#             cart.save()
            
#             # Create initial status
#             OrderStatus.objects.create(
#                 order=cart,
#                 status='pending',
#                 notes='Order placed successfully'
#             )
            
#             # Send confirmation email (async task via Celery)
#             # tasks.send_order_confirmation.delay(cart.id)
            
#             logger.info(f"Order created: {cart.id} for user {request.user.id}")
            
#             return Response(
#                 OrderConfirmationSerializer(cart).data,
#                 status=status.HTTP_201_CREATED
#             )
            
#         except CartOrder.DoesNotExist:
#             return Response(
#                 {'detail': 'Cart not found'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Address.DoesNotExist:
#             return Response(
#                 {'detail': 'Shipping address not found'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except ShippingMethod.DoesNotExist:
#             return Response(
#                 {'detail': 'Shipping method not found'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             logger.error(f"Error confirming checkout: {str(e)}")
#             return Response(
#                 {'detail': 'Error processing order'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

# ============================================================================
# CHECKOUT VIEWSET (Complete 4-Step Process)
# ============================================================================


logger = logging.getLogger(__name__)

class CheckoutViewSet(viewsets.ViewSet):
    """
    ViewSet for complete checkout process.
    
    Endpoints:
    GET  /api/v1/checkout/summary/       - Get checkout data (addresses, shipping)
    POST /api/v1/checkout/validate/      - Validate checkout form
    POST /api/v1/checkout/process/       - Create order
    GET  /api/v1/checkout/order-preview/ - Preview order before submit
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get all checkout summary data:
        - Current cart
        - User's addresses
        - Available shipping methods
        - Tax calculation
        """
        try:
            user = request.user
            
            # Get active cart
            try:
                cart = CartOrder.objects.get(
                    user=user,
                    paid_status=False,
                    order_status='pending'
                )
                
                # Calculate totals
                subtotal = cart.items.aggregate(
                    total=Sum('total')
                )['total'] or Decimal('0.00')
                
                # Get user's addresses
                addresses = Address.objects.filter(
                    user=user,
                    is_active=True
                ).values(
                    'id', 'full_name', 'phone_number', 'address_type',
                    'street_address', 'city', 'state', 'postal_code',
                    'country', 'is_default'
                )
                
                # Get shipping methods
                shipping_methods = ShippingMethod.objects.filter(
                    is_active=True
                ).values(
                    'id', 'name', 'cost', 'delivery_days', 'description'
                )
                
                return Response({
                    'success': True,
                    'cart': {
                        'id': cart.id,
                        'items': CartOrderItemsSerializer(
                            cart.items.all(),
                            many=True
                        ).data,
                        'subtotal': str(subtotal),
                        'item_count': cart.items.aggregate(
                            total=Sum('quantity')
                        )['total'] or 0,
                    },
                    'addresses': list(addresses),
                    'shipping_methods': list(shipping_methods),
                    'default_address': Address.objects.filter(
                        user=user,
                        is_default=True,
                        is_active=True
                    ).values(
                        'id', 'full_name', 'phone_number', 'street_address',
                        'city', 'state', 'postal_code', 'country'
                    ).first(),
                })
                
            except CartOrder.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Cart is empty. Please add items before checkout.',
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Checkout summary error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Error retrieving checkout data',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """
        Validate checkout data before processing.
        
        Request body:
        {
            "shipping_address_id": 1,
            "shipping_method_id": 2,
            "payment_method": "cod",
            "coupon_code": "SAVE10" (optional),
            "notes": "Special delivery instructions" (optional)
        }
        """
        try:
            user = request.user
            data = request.data
            
            # Validate address
            try:
                address = Address.objects.get(
                    id=data.get('shipping_address_id'),
                    user=user,
                    is_active=True
                )
            except Address.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid shipping address',
                    'field': 'shipping_address_id'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate shipping method
            try:
                shipping = ShippingMethod.objects.get(
                    id=data.get('shipping_method_id'),
                    is_active=True
                )
            except ShippingMethod.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid shipping method',
                    'field': 'shipping_method_id'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate payment method
            payment_methods = ['cod', 'bkash', 'nagad', 'rocket', 'visa', 'mastercard', 'stripe']
            if data.get('payment_method') not in payment_methods:
                return Response({
                    'success': False,
                    'error': 'Invalid payment method',
                    'field': 'payment_method'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get cart and calculate totals
            try:
                cart = CartOrder.objects.get(user=user, paid_status=False)
            except CartOrder.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Cart not found',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            subtotal = cart.items.aggregate(
                total=Sum('total')
            )['total'] or Decimal('0.00')
            
            # Calculate tax (5%)
            tax = subtotal * Decimal('0.05')
            
            # Apply coupon if provided
            discount = Decimal('0.00')
            if data.get('coupon_code'):
                # TODO: Implement coupon validation
                pass
            
            total = subtotal - discount + shipping.cost + tax
            
            return Response({
                'success': True,
                'totals': {
                    'subtotal': str(subtotal),
                    'discount': str(discount),
                    'shipping': str(shipping.cost),
                    'tax': str(tax),
                    'total': str(total),
                },
                'message': 'Checkout data validated successfully'
            })
            
        except Exception as e:
            logger.error(f"Checkout validation error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Error validating checkout data',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def process(self, request):
        """
        Create order from cart.
        
        Request body:
        {
            "shipping_address_id": 1,
            "shipping_method_id": 2,
            "payment_method": "cod",
            "coupon_code": "SAVE10" (optional),
            "notes": "Special instructions" (optional)
        }
        """
        try:
            user = request.user
            data = request.data
            
            # Get cart
            try:
                cart = CartOrder.objects.get(user=user, paid_status=False)
            except CartOrder.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Cart not found',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not cart.items.exists():
                return Response({
                    'success': False,
                    'error': 'Cart is empty',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get address
            try:
                address = Address.objects.get(
                    id=data.get('shipping_address_id'),
                    user=user,
                    is_active=True
                )
            except Address.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid shipping address',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get shipping method
            try:
                shipping = ShippingMethod.objects.get(
                    id=data.get('shipping_method_id'),
                    is_active=True
                )
            except ShippingMethod.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid shipping method',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Calculate totals
            subtotal = cart.items.aggregate(
                total=Sum('total')
            )['total'] or Decimal('0.00')
            
            tax = subtotal * Decimal('0.05')
            discount = Decimal('0.00')
            shipping_cost = shipping.cost
            total_price = subtotal - discount + shipping_cost + tax
            
            # Update cart as completed order
            cart.shipping_address = address
            cart.shipping_method = shipping
            cart.payment_method = data.get('payment_method', 'cod')
            cart.subtotal = subtotal
            cart.tax_amount = tax
            cart.discount_amount = discount
            cart.shipping_cost = shipping_cost
            cart.price = total_price
            cart.total_price = total_price
            cart.order_status = 'confirmed'
            cart.coupon_code = data.get('coupon_code', '')
            cart.notes = data.get('notes', '')
            cart.save()
            
            # Create initial order status
            OrderStatus.objects.create(
                order=cart,
                status='confirmed',
                notes='Order placed successfully'
            )
            
            # Dispatch event for notifications
            try:
                # Send confirmation email
                send_order_confirmation_email(cart)
            except Exception as e:
                logger.error(f"Error sending email: {str(e)}")
            
            logger.info(f"Order {cart.order_id} created for user {user.id}")
            
            serializer = CartOrderSerializer(cart)
            return Response({
                'success': True,
                'order_id': cart.order_id,
                'message': 'Order placed successfully!',
                'order': serializer.data,
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Checkout process error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Error processing checkout',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def order_preview(self, request):
        """Get cart preview before checkout"""
        try:
            user = request.user
            cart = CartOrder.objects.get(user=user, paid_status=False)
            
            serializer = CartOrderSerializer(cart)
            return Response({
                'success': True,
                'cart': serializer.data,
            })
        except CartOrder.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Cart not found',
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error getting order preview: {str(e)}")
            return Response({
                'success': False,
                'error': 'Error retrieving cart preview',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required
def checkout_page(request):
    """Checkout page"""
    return render(request, 'core/checkout.html')

@login_required
def order_confirmation_page(request, order_id):
    """Order confirmation page"""
    try:
        order = CartOrder.objects.get(
            order_id=order_id,
            user=request.user
        )
        return render(request, 'core/order-confirmation.html', {
            'order': order
        })
    except CartOrder.DoesNotExist:
        return redirect('fabrythingapp:index')

@login_required
def my_orders_page(request):
    """User's orders page"""
    orders = CartOrder.objects.filter(
        user=request.user,
        paid_status=True
    ).order_by('-created_at')
    
    return render(request, 'core/my-orders.html', {
        'orders': orders
    })

def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer.
    Can be made async with Celery later.
    """
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    
    try:
        subject = f'Order Confirmation - {order.order_id}'
        
        # Render email template
        html_message = render_to_string('emails/order-confirmation.html', {
            'order': order,
            'customer_name': order.user.first_name or order.user.username,
        })
        
        send_mail(
            subject,
            'Your order has been confirmed.',
            'noreply@fabrything.com',
            [order.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Confirmation email sent for order {order.order_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending confirmation email: {str(e)}")
        return False
    
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

# Add at END of file

# ============================================================================
# CART MANAGEMENT VIEWSET (TIER 1)
# ============================================================================

# class CartViewSet(viewsets.ViewSet):
#     """
#     ViewSet for shopping cart operations.
    
#     Endpoints:
#     - GET /api/v1/cart/ - Get current user's active cart
#     - POST /api/v1/cart/add-item/ - Add product to cart
#     - POST /api/v1/cart/remove-item/ - Remove item from cart
#     - PATCH /api/v1/cart/update-item/ - Update item quantity
#     - DELETE /api/v1/cart/clear/ - Clear entire cart
#     """
    
#     permission_classes = [IsAuthenticated]
    
#     @action(detail=False, methods=['get'])
#     def current_cart(self, request):
#         """Get current user's active cart"""
#         try:
#             cart, created = CartOrder.objects.get_or_create(
#                 user=request.user,
#                 paid_status=False
#             )
#             serializer = CartOrderSerializer(cart)
#             return Response(serializer.data)
#         except Exception as e:
#             logger.error(f"Error getting cart: {str(e)}")
#             return Response(
#                 {'detail': 'Error retrieving cart'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
    
#     @action(detail=False, methods=['post'])
#     def add_item(self, request):
#         """
#         Add product to cart or update quantity if exists.
        
#         Request body:
#         {
#             "product_id": "prod123",
#             "quantity": 1,
#             "size": "M",
#             "color": "Blue"
#         }
#         """
#         try:
#             product_id = request.data.get('product_id')
#             quantity = int(request.data.get('quantity', 1))
#             size = request.data.get('size', '')
#             color = request.data.get('color', '')
            
#             # Validate input
#             if not product_id or quantity < 1:
#                 return Response(
#                     {'detail': 'Invalid product_id or quantity'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             # Get product
#             product = Product.objects.get(pid=product_id)
            
#             # Get or create cart
#             cart, _ = CartOrder.objects.get_or_create(
#                 user=request.user,
#                 paid_status=False
#             )
            
#             # Check if item already in cart
#             cart_item = CartOrderItems.objects.filter(
#                 order=cart,
#                 product=product,
#                 size=size,
#                 color=color
#             ).first()
            
#             if cart_item:
#                 # Update quantity
#                 cart_item.quantity += quantity
#             else:
#                 # Create new cart item
#                 cart_item = CartOrderItems.objects.create(
#                     order=cart,
#                     product=product,
#                     item=product.title,
#                     image=str(product.image),
#                     size=size,
#                     color=color,
#                     quantity=quantity,
#                     price=product.price,
#                     total=quantity * product.price
#                 )
            
#             # Calculate totals
#             cart_item.total = cart_item.quantity * product.price
#             cart_item.save()
            
#             # Update cart total
#             CartService.update_cart_total(cart.id)
            
#             logger.info(f"Added product {product_id} to cart for user {request.user.id}")
            
#             serializer = CartOrderSerializer(cart)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
            
#         except Product.DoesNotExist:
#             return Response(
#                 {'detail': 'Product not found'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except ValueError:
#             return Response(
#                 {'detail': 'Invalid quantity format'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         except Exception as e:
#             logger.error(f"Error adding to cart: {str(e)}")
#             return Response(
#                 {'detail': 'Error adding item to cart'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
    
#     @action(detail=False, methods=['post'])
#     def remove_item(self, request):
#         """Remove item from cart"""
#         try:
#             item_id = request.data.get('item_id')
            
#             if not item_id:
#                 return Response(
#                     {'detail': 'item_id required'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             cart_item = CartOrderItems.objects.get(
#                 id=item_id,
#                 order__user=request.user,
#                 order__paid_status=False
#             )
            
#             cart = cart_item.order
#             cart_item.delete()
            
#             # Recalculate cart total
#             CartService.update_cart_total(cart.id)
            
#             logger.info(f"Removed item {item_id} from cart for user {request.user.id}")
            
#             serializer = CartOrderSerializer(cart)
#             return Response(serializer.data)
            
#         except CartOrderItems.DoesNotExist:
#             return Response(
#                 {'detail': 'Item not found in cart'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             logger.error(f"Error removing from cart: {str(e)}")
#             return Response(
#                 {'detail': 'Error removing item'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
    
#     @action(detail=False, methods=['patch'])
#     def update_item(self, request):
#         """Update cart item quantity"""
#         try:
#             item_id = request.data.get('item_id')
#             quantity = int(request.data.get('quantity', 1))
            
#             if quantity < 0:
#                 return Response(
#                     {'detail': 'Quantity must be >= 0'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             cart_item = CartOrderItems.objects.get(
#                 id=item_id,
#                 order__user=request.user,
#                 order__paid_status=False
#             )
            
#             if quantity == 0:
#                 # Remove item if quantity is 0
#                 cart = cart_item.order
#                 cart_item.delete()
#             else:
#                 # Update quantity
#                 cart_item.quantity = quantity
#                 cart_item.total = quantity * cart_item.price
#                 cart_item.save()
#                 cart = cart_item.order
            
#             CartService.update_cart_total(cart.id)
            
#             serializer = CartOrderSerializer(cart)
#             return Response(serializer.data)
            
#         except CartOrderItems.DoesNotExist:
#             return Response(
#                 {'detail': 'Item not found'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except ValueError:
#             return Response(
#                 {'detail': 'Invalid quantity'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         except Exception as e:
#             logger.error(f"Error updating cart item: {str(e)}")
#             return Response(
#                 {'detail': 'Error updating item'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
    
#     @action(detail=False, methods=['delete'])
#     def clear(self, request):
#         """Clear entire cart"""
#         try:
#             cart = CartOrder.objects.get(
#                 user=request.user,
#                 paid_status=False
#             )
#             cart.items.all().delete()
#             cart.price = 0
#             cart.save()
            
#             logger.info(f"Cleared cart for user {request.user.id}")
            
#             return Response(
#                 {'detail': 'Cart cleared successfully'},
#                 status=status.HTTP_204_NO_CONTENT
#             )
#         except CartOrder.DoesNotExist:
#             return Response(
#                 {'detail': 'No active cart'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             logger.error(f"Error clearing cart: {str(e)}")
#             return Response(
#                 {'detail': 'Error clearing cart'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

# Replace the CartViewSet at the end

class CartViewSet(viewsets.ViewSet):
    """
    ViewSet for shopping cart management.
    
    Endpoints:
    GET    /api/v1/cart/current_cart/ - Get current cart
    POST   /api/v1/cart/add_item/     - Add item to cart
    POST   /api/v1/cart/update_item/  - Update item quantity
    POST   /api/v1/cart/remove_item/  - Remove item from cart
    DELETE /api/v1/cart/clear/        - Clear entire cart
    """
    
    serializer_class = CartOrderSerializer
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
            try:
                product = Product.objects.get(pid=product_id)
            except Product.DoesNotExist:
                return Response(
                    {'detail': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check stock
            if product.stock_count < quantity:
                return Response(
                    {'detail': f'Only {product.stock_count} items available'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
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
                new_quantity = cart_item.quantity + quantity
                if product.stock_count < new_quantity:
                    return Response(
                        {'detail': f'Only {product.stock_count} items available'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_item.quantity = new_quantity
            else:
                # Create new cart item
                cart_item = CartOrderItems(
                    order=cart,
                    product=product,
                    item=product.title,
                    image=str(product.image),
                    size=size,
                    color=color,
                    quantity=quantity,
                    price=product.price,
                )
            
            # Calculate total
            cart_item.total = cart_item.quantity * product.price
            cart_item.save()
            
            # Update cart total
            self._update_cart_total(cart)
            
            logger.info(f"Added product {product_id} to cart for user {request.user.id}")
            
            serializer = CartOrderSerializer(cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
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
                # Check stock
                if cart_item.product.stock_count < quantity:
                    return Response(
                        {'detail': f'Only {cart_item.product.stock_count} items available'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Update quantity
                cart_item.quantity = quantity
                cart_item.total = quantity * cart_item.price
                cart_item.save()
                cart = cart_item.order
            
            self._update_cart_total(cart)
            
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
            self._update_cart_total(cart)
            
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
    
    def _update_cart_total(self, cart):
        """Calculate and update cart totals"""
        items = cart.items.all()
        subtotal = sum(item.total for item in items)
        taxes = subtotal * 0.05  # 5% tax
        cart.subtotal = subtotal
        cart.taxes = taxes
        cart.price = subtotal + taxes
        cart.save()

class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for shopping cart management.
    
    Endpoints:
    GET    /api/v1/cart/          - Get current cart
    POST   /api/v1/cart/          - Create new cart (auto)
    POST   /api/v1/cart/add_item/ - Add item to cart
    POST   /api/v1/cart/update_item/ - Update item quantity
    POST   /api/v1/cart/remove_item/ - Remove item from cart
    POST   /api/v1/cart/clear/    - Clear entire cart
    """
    
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user's cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Add item to cart.
        
        Request body:
        {
            "product_id": 123,
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
            
            if not product_id:
                return Response(
                    {'error': 'product_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create cart
            cart, _ = Cart.objects.get_or_create(user=request.user)
            
            # Get product
            try:
                product = Product.objects.get(pid=product_id)
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Add or update cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                size=size,
                color=color,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Item already exists, update quantity
                cart_item.quantity += quantity
                cart_item.save()
            
            serializer = CartItemSerializer(cart_item)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            logger.error(f"Error adding to cart: {str(e)}")
            return Response(
                {'error': 'Failed to add item to cart'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """
        Update cart item quantity.
        
        Request body:
        {
            "item_id": 456,
            "quantity": 2
        }
        """
        try:
            item_id = request.data.get('item_id')
            quantity = int(request.data.get('quantity', 1))
            
            if quantity < 1:
                # Delete if quantity is 0 or negative
                CartItem.objects.filter(id=item_id).delete()
                return Response(
                    {'message': 'Item removed from cart'},
                    status=status.HTTP_200_OK
                )
            
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user
            )
            cart_item.quantity = quantity
            cart_item.save()
            
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)
        
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating cart item: {str(e)}")
            return Response(
                {'error': 'Failed to update item'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """
        Remove item from cart.
        
        Request body:
        {
            "item_id": 456
        }
        """
        try:
            item_id = request.data.get('item_id')
            CartItem.objects.filter(
                id=item_id,
                cart__user=request.user
            ).delete()
            
            return Response(
                {'message': 'Item removed from cart'},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"Error removing from cart: {str(e)}")
            return Response(
                {'error': 'Failed to remove item'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear entire cart"""
        try:
            Cart.objects.filter(user=request.user).delete()
            return Response(
                {'message': 'Cart cleared'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error clearing cart: {str(e)}")
            return Response(
                {'error': 'Failed to clear cart'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# ADDRESS MANAGEMENT VIEWSET
# ============================================================================

class AddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user addresses.
    
    Endpoints:
    GET    /api/v1/addresses/     - List user's addresses
    POST   /api/v1/addresses/     - Create new address
    GET    /api/v1/addresses/{id}/ - Get address
    PUT    /api/v1/addresses/{id}/ - Update address
    DELETE /api/v1/addresses/{id}/ - Delete address
    """
    
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save()


# ============================================================================
# CHECKOUT & ORDER VIEWSET
# ============================================================================

class CheckoutViewSet(viewsets.ViewSet):
    """
    ViewSet for checkout process.
    
    Endpoints:
    POST /api/v1/checkout/process/ - Place order
    GET  /api/v1/checkout/summary/  - Get checkout summary
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get checkout summary (cart items + shipping options).
        """
        try:
            cart = Cart.objects.get(user=request.user)
            shipping_methods = ShippingMethod.objects.filter(is_active=True)
            addresses = Address.objects.filter(
                user=request.user,
                is_active=True
            )
            
            return Response({
                'cart': CartSerializer(cart).data,
                'shipping_methods': ShippingMethodSerializer(
                    shipping_methods,
                    many=True
                ).data,
                'addresses': AddressSerializer(addresses, many=True).data,
            })
        
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def process(self, request):
        """
        Process checkout and create order.
        
        Request body:
        {
            "shipping_address_id": 1,
            "shipping_method_id": 1,
            "payment_method": "cod",
            "coupon_code": "SAVE10",
            "notes": "Please deliver after 5 PM"
        }
        """
        try:
            # Validate checkout data
            serializer = CheckoutSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get user's cart
            try:
                cart = Cart.objects.get(user=request.user)
                if not cart.items.exists():
                    return Response(
                        {'error': 'Cart is empty'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Cart.DoesNotExist:
                return Response(
                    {'error': 'Cart not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get address and shipping method
            address = Address.objects.get(
                id=serializer.validated_data['shipping_address_id'],
                user=request.user
            )
            shipping_method = ShippingMethod.objects.get(
                id=serializer.validated_data['shipping_method_id']
            )
            
            # Calculate totals
            subtotal = cart.subtotal
            discount = Decimal('0')
            shipping_cost = shipping_method.cost
            tax = Decimal('0')  # TODO: Implement tax calculation
            
            # Create order
            order = CartOrder.objects.create(
                user=request.user,
                subtotal=subtotal,
                discount_amount=discount,
                shipping_cost=shipping_cost,
                tax_amount=tax,
                total_price=(
                    subtotal - discount + shipping_cost + tax
                ),
                shipping_address=address,
                shipping_method=shipping_method,
                payment_method=serializer.validated_data['payment_method'],
                coupon_code=serializer.validated_data.get('coupon_code', ''),
                notes=serializer.validated_data.get('notes', ''),
            )
            
            # Copy cart items to order
            for cart_item in cart.items.all():
                CartOrderItems.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.title,
                    product_price=cart_item.product.price,
                    size=cart_item.size,
                    color=cart_item.color,
                    quantity=cart_item.quantity,
                )
            
            # Create initial order status
            OrderStatus.objects.create(
                order=order,
                status='pending',
                notes='Order received'
            )
            
            # Send confirmation email
            try:
                send_order_confirmation_email.delay(order.id)
            except Exception as e:
                logger.error(f"Error sending confirmation email: {e}")
            
            # Clear cart
            cart.delete()
            
            # Return confirmation
            serializer = OrderConfirmationSerializer(order)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        except Address.DoesNotExist:
            return Response(
                {'error': 'Invalid address'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ShippingMethod.DoesNotExist:
            return Response(
                {'error': 'Invalid shipping method'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Checkout error: {str(e)}")
            return Response(
                {'error': 'Failed to process checkout'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# ORDER MANAGEMENT VIEWSET
# ============================================================================

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and tracking orders.
    
    Endpoints:
    GET /api/v1/orders/        - List user's orders
    GET /api/v1/orders/{id}/   - Get order details
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartOrder.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer
    
    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        """
        Get order tracking information.
        
        Returns status history and estimated delivery.
        """
        order = self.get_object()
        return Response({
            'order_id': order.order_id,
            'current_status': order.get_order_status_display(),
            'status_history': OrderStatusSerializer(
                order.status_history.all(),
                many=True
            ).data,
            'shipping_method': ShippingMethodSerializer(
                order.shipping_method
            ).data,
            'estimated_delivery': (
                order.created_at + 
                timedelta(days=order.shipping_method.delivery_days)
            ).strftime('%Y-%m-%d'),
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel order (only if not yet shipped).
        """
        order = self.get_object()
        
        if order.order_status in ['shipped', 'delivered']:
            return Response(
                {'error': 'Cannot cancel shipped order'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.order_status = 'cancelled'
        order.save()
        
        # Create status record
        OrderStatus.objects.create(
            order=order,
            status='cancelled',
            notes='Order cancelled by customer'
        )
        
        return Response(
            {'message': 'Order cancelled successfully'},
            status=status.HTTP_200_OK
        )
