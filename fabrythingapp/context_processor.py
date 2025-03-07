from fabrythingapp.models import Product, Category


def default(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    return {
        'categories':categories,
        'products':products,
    }