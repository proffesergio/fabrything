from fabrythingapp.models import Product, Category, Address


def default(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    # customer_address = Address.objects.get(user=request.user.id)

    return {
        'categories':categories,
        'products':products,
        # 'customer_address':customer_address,
    }