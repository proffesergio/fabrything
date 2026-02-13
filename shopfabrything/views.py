from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

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