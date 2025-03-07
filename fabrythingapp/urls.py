from django.urls import path
from fabrythingapp import views
from fabrythingapp.views import category_list_view, category_products, product_details_view

app_name = "fabrythingapp"

urlpatterns = [
    path("", views.index, name='index'),
    path("categories/", category_list_view, name='categories'),
    path("category/<cid>/", category_products, name='category-products'),
    path("product/<pid>/", product_details_view, name='product-details'),
]