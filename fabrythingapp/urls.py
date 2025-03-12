from django.urls import path, include
from fabrythingapp import views
from fabrythingapp.views import category_list_view, category_products, product_details_view, tag_list
from django.conf.urls.static import static
from django.conf import settings


app_name = "fabrythingapp"

urlpatterns = [
    path("", views.index, name='index'),
    path("categories/", category_list_view, name='categories'),
    path("category/<cid>/", category_products, name='category-products'),
    path("product/<pid>/", product_details_view, name='product-details'),

    # Tags
    path("products/tag/<tag_slug>/", tag_list, name='tags'),
] 