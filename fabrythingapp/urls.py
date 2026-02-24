from django.urls import path, include
from fabrythingapp import views
from fabrythingapp.views import category_list_view, category_products, product_details_view, tag_list, ajax_add_review, search_view, filter_products, product_list_view
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin


app_name = "fabrythingapp"

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.index, name='index'),
    path("categories/", category_list_view, name='categories'),
    path("products/", product_list_view, name='products'),
    path("category/<cid>/", category_products, name='category-products'),
    path("product/<pid>/", product_details_view, name='product-details'),

    # Tags
    path("products/tag/<tag_slug>/", tag_list, name='tags'),
    #Add Review
    path("add-review/<pid>/", ajax_add_review, name="add-review"),
    #Search
    path("search/", search_view, name="search"),
    #Filter
    path("filter-products/", filter_products, name="filter-products"),
    # Cart & Checkout
    path('cart/', views.cart_page, name='cart'),
    path('checkout/', views.checkout_page, name='checkout'),
    path('order-confirmation/<str:order_id>/', views.order_confirmation_page, name='order-confirmation'),
    path('my-orders/', views.my_orders_page, name='my-orders'),

    # API v1 - Auth endpoints
    path('api/v1/auth/', include('userauthapp.urls')),
    # API v1 - App endpoints
    path('api/v1/', include('fabrythingapp.api_urls')),
    path('api/v1/', include('userauthapp.api_urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)