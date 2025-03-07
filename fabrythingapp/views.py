from django.shortcuts import render
from fabrythingapp.models import Product, Category, Vendor, CartOrder, CartOrderItems, Wishlist, ProductImages, ProductReview, Address, Brand
from django.db.models import Count


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

    product_image = product.product_images.all()

    context = {
        'product': product,
        'product_image': product_image,
    }

    return render(requests, 'core/product-details.html', context)