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
    CartOrderItemsSerializer, WishlistSerializer, AddressSerializer
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


