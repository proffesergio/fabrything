from django.urls import path, include
from userauthapp.Controllers import AuthController
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from userauthapp.views import CustomTokenObtainPairView, UserViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('publicApi/', AuthController.PublicAPIView.as_view(), name='public_api'),
    path('protectedApi/', AuthController.ProtectedAPIView.as_view(), name='protected_api'),
]