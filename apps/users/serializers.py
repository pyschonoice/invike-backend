from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model excluding sensitive information
    """
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'avatar', 'role')
        read_only_fields = ('id',)

class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed User serializer for profile views
    """
    payment_summary = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'avatar', 'role', 'phone_number', 'date_joined')
        read_only_fields = ('id', 'date_joined')

    def get_payment_summary(self, obj):
        # Only include payment summary for the user themselves
        request_user = self.context['request'].user
        if request_user != obj:
            return None
        
        from apps.payments.models import Payment
        
        # Get payment counts
        paid_count = Payment.objects.filter(user=obj, status='PAID').count()
        pending_count = Payment.objects.filter(user=obj, status='PENDING').count()
        
        # For hosts, get payment counts for their events
        if obj.role == 'HOST':
            from apps.events.models import Event
            
            host_events = Event.objects.filter(created_by=obj)
            host_paid_count = Payment.objects.filter(
                event__in=host_events, 
                status='PAID'
            ).count()
            host_pending_count = Payment.objects.filter(
                event__in=host_events, 
                status='PENDING'
            ).count()
            
            return {
                'user_payments': {
                    'paid': paid_count,
                    'pending': pending_count
                },
                'host_payments': {
                    'paid': host_paid_count,
                    'pending': host_pending_count
                }
            }
        
        return {
            'paid': paid_count,
            'pending': pending_count
        }

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password', 'role', 'avatar', 'phone_number')
        read_only_fields = ('id',)
        
    def create(self, validated_data):
        # Create user with encrypted password
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            role=validated_data.get('role', 'GUEST'),
            avatar=validated_data.get('avatar', None),
            phone_number=validated_data.get('phone_number', None)
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
        return {'user': user}

class SocialLoginSerializer(serializers.Serializer):
    """
    Serializer for social login (Google, Apple)
    """
    provider = serializers.ChoiceField(choices=['google', 'apple'])
    access_token = serializers.CharField()
    
    # In a real implementation, you would validate the token with the provider
    # and create or authenticate the user based on the provider's response

class TokenRefreshSerializer(serializers.Serializer):
    """
    Serializer for JWT token refresh
    """
    refresh_token = serializers.CharField()

class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    """
    class Meta:
        model = User
        fields = ('name', 'avatar', 'phone_number', 'role')

