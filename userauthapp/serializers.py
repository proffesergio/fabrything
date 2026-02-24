from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from userauthapp.models import User
import logging

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    """User serializer for registration and profile"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'username', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration with validation"""
    
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text='Password must be at least 8 characters'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='Confirm your password'
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone', 
            'username', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        """Validate registration data"""
        
        # Check passwords match
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match'
            })
        
        # Check email uniqueness
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                'email': 'Email already registered'
            })
        
        # Check username uniqueness
        if attrs.get('username') and User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({
                'username': 'Username already taken'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password"""
        
        # Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # If username not provided, use email prefix
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email'].split('@')[0][:10]
        
        # Create user
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        # fixing the domain_user_id property error
        # if not user.domain_user_id:
        #     user.domain_user_id = str(user.id)
        user.save()
        
        logger.info(f"New user registered: {user.email}")
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with user details"""
    
    def validate(self, attrs):
        """Validate and return tokens with user info"""
        
        email = attrs.get('email')
        password = attrs.get('password')
        
        if not email or not password:
            raise serializers.ValidationError({
                'detail': 'Email and password are required'
            })
        
        # Authenticate using email as username
        user = authenticate(
            username=email,
            password=password
        )
        
        if user is None:
            raise serializers.ValidationError({
                'detail': 'Invalid credentials'
            })
        
        # Get tokens
        data = super().get_token(user)
        
        return {
            'access': str(data.access_token),
            'refresh': str(data),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
            }
        }
    
    def validate_email(self, value):
        """Custom field for email instead of username"""
        return value
    
    @classmethod
    def get_token(cls, user):
        """Override to customize token claims"""
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        
        return token