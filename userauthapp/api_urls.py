from django.urls import path, include
from userauthapp.Controllers import AuthController
# from userauthapp.Controllers.AuthController import 
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from userauthapp.views import CustomTokenObtainPairView, UserViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('publicApi/', AuthController.PublicAPIView.as_view(), name='public_api'),
    path('protectedApi/', AuthController.ProtectedAPIView.as_view(), name='protected_api'),
    path('superadminurl/', AuthController.SuperAdminAPIView.as_view(), name='superadminurl'),
    path('register/', AuthController.RegisterAPIView.as_view(), name='register'),
    path('login/', AuthController.LoginAPIView.as_view(), name='login'),
    path('refresh/', AuthController.RefreshTokenAPIView.as_view(), name='refresh'),
    path('me/', AuthController.CurrentUserAPIView.as_view(), name='current-user'),
    path('logout/', AuthController.LogoutAPIView.as_view(), name='logout'),
]