from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from userauthapp.models import User
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

class RegisterApiView(APIView):
    """
    Register new user
    POST /api/v1/auth/register/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            confirm_password = request.data.get('confirm_password')
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')

            # Validation
            if not email or not password:
                return Response(
                    {'error': 'Email and password are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if password != confirm_password:
                return Response(
                    {'error': 'Passwords do not match'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if len(password) < 8:
                return Response(
                    {'error': 'Password must be at least 8 characters'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if User.objects.filter(email=email).exists():
                return Response(
                    {'error': 'Email already registered'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create user
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                username=email
            )

            return Response(
                {
                    'success': True,
                    'message': 'User registered successfully',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginAPIView(APIView):

    """
    Login user and return JWT tokens
    POST /api/v1/auth/signin/
    """
    permission_classes = [AllowAny]

    def post(self, request):

        try:
            email = request.data.get('email')
            password = request.data.get('password')

            if not email or not password:
                return Response(
                    {'error': 'Email and password are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Authenticate user
            user = authenticate(request, username=email, password=password)

            if user is None:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    'success': True,
                    'message': 'Login successful',
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class PublicAPIView(APIView):
    
    def get(self, request):
        return Response(
            {
                'success': True,
                'message': 'This is a public endpoint',
                'user': {
                    'id': request.user.id,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                }
            },
            status=status.HTTP_200_OK
        )
class ProtectedAPIView(APIView):
    authentication_classes = [JWTAuthentication] # Use JWT authentication for this view
    permission_classes = [IsAuthenticated] # Only allow authenticated users

    def get(self, request):
        return Response(
            {
                'success': True,
                'message': 'This is a protected endpoint',
                'user': {
                    'id': request.user.id,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                }
            },
            status=status.HTTP_200_OK
        )