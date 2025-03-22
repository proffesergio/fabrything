from django.shortcuts import render, get_object_or_404
from fabrythingapp.models import Product, Category, Vendor, CartOrder, CartOrderItems, Wishlist, ProductImages, ProductReview, Address, Brand, User
from django.db.models import Count, Avg
from taggit.models import Tag
from fabrythingapp.forms import ProductReviewForm
from django.http import HttpResponse, JsonResponse



# Create your views here.
def index(requests):
    # products = Product.objects.all()
    products = Product.objects.filter(featured=True, product_status='published', )

    categories = Category.objects.all()

    brands = Brand.objects.all()

    context = {
        'products' : products,
        'categories': categories,
        'brands': brands,
    }
    return render(requests, 'core/home.html', context)

def category_list_view(requests):

    # categories = Category.objects.all().annotate(product_count=Count('products'))
    categories = Category.objects.all()
    products = Product.objects.all()

    context = {
        'categories':categories,
        'products':products,
    }
    return render(requests, 'core/category-list.html', context)

def get_brands(requests):
    brands = Brand.objects.all()
    
    context = {
        'brands':brands,
    }
    return render(requests, 'core/home.html', context)

def category_products(requests, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status='published', category=category)

    context = {
        'category':category,
        'products':products,
    }
    return render(requests, 'core/category-products.html', context)

def product_details_view(requests, pid):
    product = Product.objects.get(pid=pid)
    related_products = Product.objects.filter(category=product.category).exclude(pid=pid)
    reviews = ProductReview.objects.filter(product=product)
    avg_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))


    product_image = product.product_images.all()

    # Product Review Form 
    review_form = ProductReviewForm()

    make_review = True 

    if requests.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=requests.user, product=product).count()

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
    return render(requests, 'core/product-details.html', context)

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