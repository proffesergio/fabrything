from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg
from taggit.models import Tag
from fabrythingapp.forms import ProductReviewForm
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from fabrythingapp.models import (
    Product, Category, Brand, ProductReview,
    CartOrder, CartOrderItems, Wishlist, Address
)
from fabrythingapp.serializers import (
    ProductSerializer, ProductDetailSerializer, CategorySerializer,
    BrandSerializer, ProductReviewSerializer, CartOrderSerializer,
    CartOrderItemsSerializer, WishlistSerializer, AddressSerializer,
    UserPreferencesSerializer
)
from fabrythingapp.services import ProductService, ReviewService, CartService

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

class AddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Address operations
    Endpoints:
    - GET /api/v1/addresses/ - Get user's addresses
    - POST /api/v1/addresses/ - Create address
    - PUT /api/v1/addresses/{id}/ - Update address
    - DELETE /api/v1/addresses/{id}/ - Delete address
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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

from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone

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


