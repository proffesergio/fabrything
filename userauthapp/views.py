from django.shortcuts import render, redirect
from userauthapp.forms import UserRegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from userauthapp.models import User
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from userauthapp.models import User
from userauthapp.serializers import (
    CustomTokenObtainPairSerializer, UserRegistrationSerializer, UserSerializer
)

logger = logging.getLogger(__name__)

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login endpoint with user details"""
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User operations
    Endpoints:
    - POST /api/v1/auth/register/ - Register new user
    - POST /api/v1/auth/login/ - Login user
    - GET /api/v1/auth/me/ - Get current user
    - PUT /api/v1/auth/me/ - Update current user
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.all()
    
    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
    def register(self, request):
        """Register new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"New user registered: {serializer.validated_data['email']}")
            return Response(
                {'detail': 'User registered successfully'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['GET'])
    def me(self, request):
        """Get current user details"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['PUT'])
    def update_me(self, request):
        """Update current user"""
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User updated: {request.user.email}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# User = settings.AUTH_USER_MODEL

# Create your views here.
def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:index') 

    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Hey {username}, Your account was created successfully!")
            new_user = authenticate(username=form.cleaned_data['email'], password = form.cleaned_data['password1'])
            login(request, new_user)

            return redirect('core:index')

        print("User registration successful")
    else:
        print("User cannot be registered.")
        form = UserRegisterForm()
    
    
    context = {
        'form': form,

    }
    return render(request, 'userauthapp/sign-up.html', context)

def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, f"Hey, you're already logged in!")
        print("Logged in already!")
        return redirect('core:index')
    
    if request.method == "POST":
        email = request.POST.get('email') #user passed email
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            #auto login user
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Logged in {email} successfully!")
                return redirect('core:index')
            else:
                messages.warning(request, f"{email} Does Not Exist!")
        except:
            messages.warning(request, f"User with {email} doesn't exist!")

     
    return render(request, "userauthapp/sign-in.html")

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, f"Logged out successfully!")
        return redirect("userauthapp:sign-in")