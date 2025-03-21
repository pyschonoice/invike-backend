from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import (
    UserSerializer, 
    UserDetailSerializer,
    UserRegistrationSerializer, 
    UserLoginSerializer,
    SocialLoginSerializer,
    TokenRefreshSerializer,
    ProfileUpdateSerializer
)

class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """
    API endpoint for user login
    """
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SocialLoginView(APIView):
    """
    API endpoint for social login (Google, Apple)
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = SocialLoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            provider = serializer.validated_data['provider']
            token = serializer.validated_data['access_token']
            
            # In a real implementation:
            # 1. Validate the token with the provider (Google/Apple)
            # 2. Get user info from the provider
            # 3. Create or authenticate user based on provider's response
            
            # For testing purposes, we'll create a dummy implementation
            if provider == 'google':
                # Simulating user lookup or creation based on Google token
                # In production, you'd validate the token with Google
                user, created = User.objects.get_or_create(
                    email='google_user@example.com',
                    defaults={
                        'username': 'google_user@example.com',
                        'name': 'Google User',
                        'google_id': 'dummy_google_id'
                    }
                )
            else:  # provider == 'apple'
                # Simulating user lookup or creation based on Apple token
                user, created = User.objects.get_or_create(
                    email='apple_user@example.com',
                    defaults={
                        'username': 'apple_user@example.com',
                        'name': 'Apple User',
                        'apple_id': 'dummy_apple_id'
                    }
                )
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                'message': f'{provider.capitalize()} login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TokenRefreshView(APIView):
    """
    API endpoint for refreshing JWT token
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = TokenRefreshSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data['refresh_token']
                token = RefreshToken(refresh_token)
                
                return Response({
                    'status': 'success',
                    'tokens': {
                        'access': str(token.access_token),
                        'refresh': str(token)
                    }
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'status': 'error',
                    'message': 'Invalid refresh token',
                    'details': str(e)
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving user profile
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ProfileUpdateView(generics.UpdateAPIView):
    """
    API endpoint for updating user profile
    """
    serializer_class = ProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'status': 'success',
            'message': 'Profile updated successfully',
            'user': UserDetailSerializer(instance).data
        })
