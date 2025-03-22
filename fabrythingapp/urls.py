from django.urls import path, include
from fabrythingapp import views
from fabrythingapp.views import category_list_view, category_products, product_details_view, tag_list, ajax_add_review, search_view
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

    #Add Review
    path("add-review/<pid>/", ajax_add_review, name="add-review"),

    #Search
    path("search/", search_view, name="search"),
] 