from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from fabrythingapp.Helpers import renderResponse
from fabrythingapp.Permission import IsSuperAdmin
from userauthapp.serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserSerializer
)
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate


logger = logging.getLogger(__name__)


class RegisterAPIView(APIView):
    """
    Register new user
    POST /api/v1/auth/register/
    
    Request body:
    {
        "email": "user@example.com",
        "password": "SecurePassword123",
        "password_confirm": "SecurePassword123",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890"
    }
    """
    
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            
            if serializer.is_valid():
                user = serializer.save()
                
                logger.info(f"User registered successfully: {user.email}")
                
                return Response(
                    {
                        'success': True,
                        'message': 'User registered successfully',
                        'data': {
                            'id': user.id,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                        }
                    },
                    status=status.HTTP_201_CREATED
                )
            
            return Response(
                {
                    'success': False,
                    'message': 'Registration failed',
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {
                    'success': False,
                    'message': 'An error occurred during registration'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# class LoginAPIView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')

#         if username is None or password is None:
#             return renderResponse(data='Please provide both username and password',message='Please provide both username and password',status=status.HTTP_400_BAD_REQUEST)

#         user = authenticate(request, username=username, password=password)
#         if user:
#             refresh = RefreshToken.for_user(user)
#             access =refresh.access_token
#             access['username'] = user.username
#             access['email'] = user.email
#             access['profile_pic'] = user.profile_pic

#             return Response({
#                 'refresh': str(refresh),
#                 'access': str(access),
#             })
#         else:
#             return renderResponse(data='Invalid credentials',message='Invalid credentials',status=status.HTTP_400_BAD_REQUEST)
#     def get(self,request):
#         return renderResponse(data='Please Use Post Method to Login',message='Please Use Post Method to Login',status=status.HTTP_400_BAD_REQUEST)
    


# Serializer Login Code Start
class LoginAPIView(APIView):
#     """
#     Login user and get JWT tokens
#     POST /api/v1/auth/login/
    
#     Request body:
#     {
#         "email": "user@example.com",
#         "password": "SecurePassword123"
#     }
    
#     Response:
#     {
#         "success": true,
#         "message": "Login successful",
#         "data": {
#             "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#             "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#             "user": {
#                 "id": 1,
#                 "email": "user@example.com",
#                 "first_name": "John",
#                 "last_name": "Doe"
#             }
#         }
#     }
#     """
    
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            
            if serializer.is_valid():
                data = serializer.validated_data
                
                logger.info(f"User logged in: {data['user']['email']}")
                
                return Response(
                    {
                        'success': True,
                        'message': 'Login successful',
                        'data': {
                            'access_token': data['access'],
                            'refresh_token': data['refresh'],
                            'user': data['user']
                        }
                    },
                    status=status.HTTP_200_OK
                )
            
            return Response(
                {
                    'success': False,
                    'message': 'Invalid credentials',
                    'errors': serializer.errors
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {
                    'success': False,
                    'message': 'An error occurred during login'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# Serializer Logic Code End
class RefreshTokenAPIView(APIView):
    """
    Refresh access token using refresh token
    POST /api/v1/auth/refresh/
    
    Request body:
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return Response(
                    {
                        'success': False,
                        'message': 'Refresh token is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                refresh = RefreshToken(refresh_token)
                access_token = str(refresh.access_token)
                
                return Response(
                    {
                        'success': True,
                        'message': 'Token refreshed successfully',
                        'data': {
                            'access_token': access_token
                        }
                    },
                    status=status.HTTP_200_OK
                )
            
            except Exception as e:
                return Response(
                    {
                        'success': False,
                        'message': 'Invalid refresh token'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return Response(
                {
                    'success': False,
                    'message': 'An error occurred during token refresh'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CurrentUserAPIView(APIView):
    """
    Get current authenticated user
    GET /api/v1/auth/me/
    
    Headers:
    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
    """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            serializer = UserSerializer(user)
            
            return Response(
                {
                    'success': True,
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return Response(
                {
                    'success': False,
                    'message': 'An error occurred'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LogoutAPIView(APIView):
    """
    Logout user (blacklist token on client side)
    POST /api/v1/auth/logout/
    
    This endpoint is mainly for logging purposes.
    Client should delete tokens from localStorage.
    """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            logger.info(f"User logged out: {request.user.email}")
            
            return Response(
                {
                    'success': True,
                    'message': 'Logged out successfully. Please delete tokens from client.'
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {
                    'success': False,
                    'message': 'An error occurred during logout'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class PublicAPIView(APIView):
    def get(self, request):
        return renderResponse(
            data='This is a public endpoint accessible to everyone.',
            message='Public endpoint'
        )
    
class ProtectedAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return renderResponse(
            data=f'Hello, {request.user.email}! You are now authenticated.',
            message='Protected endpoint'
        )

class SuperAdminAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def get(self, request):
        if hasattr(request.user, 'role') and request.user.role == 'Super Admin':
            return renderResponse(
                data=f'Hello, {request.user.email}! This is a Super Admin endpoint.',
                message='Super Admin endpoint'
            )
        else:
            return renderResponse(
                data='You are not authorized to access this endpoint.',
                message='Unauthorized',
                status=403
            )