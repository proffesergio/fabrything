from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    path("", include("fabrythingapp.urls", 'core'), name='core'),
    path("user/", include("userauthapp.urls")),
    #CkEditor
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    # path("upload/", custom_upload_function, name="custom_upload_file"),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Versioning
    path('api/v1/', include('fabrythingapp.api_urls')),
    path('api/v1/auth/', include('userauthapp.api_urls')),
    path('api/vendor/', include('vendor.urls')),
    path('api/v1/vendor/', include('vendor.urls')),
    
    # Legacy URLs (keep for backward compatibility)
    path('', include('fabrythingapp.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path("", include("fabrythingapp.urls", 'core'), name='core'),
#     path("user/", include("userauthapp.urls")),
#     #CkEditor
#     path("ckeditor5/", include('django_ckeditor_5.urls')),
#     # path("upload/", custom_upload_function, name="custom_upload_file"),

# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
