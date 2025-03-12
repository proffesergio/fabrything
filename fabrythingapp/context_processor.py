from fabrythingapp.models import Product, Category, Address


def default(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    # customer_address = Address.objects.get(user=request.user.id)
    try:
        address = Address.objects.get(user=request.user)
    except:
        address = None

    return {
        'categories':categories,
        'products':products,
        'address':address,
        # 'customer_address':customer_address,
    }