from django.urls import path
from userauthapp import views
from userauthapp.Controllers import AuthController
from userauthapp.views import CustomTokenObtainPairView, UserViewSet

app_name = "userauthapp"

urlpatterns = [
    # serializer method
    path("sign-up/", views.register_view, name='sign-up'),
    path("sign-in/", views.login_view, name='sign-in'),
    path("sign-out/", views.logout_view, name='sign-out'),
    # controller method
    path('register/', AuthController.RegisterApiView.as_view(), name='register'),
    path('login/', AuthController.LoginAPIView.as_view(), name='login'),
    # path('api/auth/logout/', AuthController.logout, name='logout'),
    # path('api/auth/refresh/', AuthController.refresh_token, name='refresh'),
    # path('api/auth/profile/', AuthController.get_user_profile, name='profile'),

]