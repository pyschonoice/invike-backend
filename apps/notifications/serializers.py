from rest_framework import serializers
from .models import Notification
from apps.users.serializers import UserSerializer
from apps.events.serializers import EventSerializer

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model
    """
    event = EventSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = (
            'id', 'user', 'event', 'type', 'title', 
            'message', 'action_link', 'action_text',
            'is_read', 'created_at'
        )
        read_only_fields = ('id', 'user', 'created_at')

class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notifications
    """
    event_id = serializers.UUIDField(required=False, allow_null=True)
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        write_only=True
    )
    
    class Meta:
        model = Notification
        fields = (
            'id', 'user_ids', 'event_id', 'type', 'title', 
            'message', 'action_link', 'action_text'
        )
        read_only_fields = ('id',)
    
    def validate(self, data):
        """
        Validate notification data
        """
        user_ids = data.pop('user_ids')
        event_id = data.get('event_id')
        
        # Check that users exist
        from apps.users.models import User
        users = User.objects.filter(id__in=user_ids)
        if len(users) != len(user_ids):
            raise serializers.ValidationError("Some users do not exist")
        
        # Check that event exists if provided
        if event_id:
            from apps.events.models import Event
            try:
                event = Event.objects.get(pk=event_id)
                data['event'] = event
            except Event.DoesNotExist:
                raise serializers.ValidationError("Event does not exist")
        
        # Store users for create method
        self.users = users
        
        return data
    
    def create(self, validated_data):
        """
        Create notifications for multiple users
        """
        users = self.users
        notifications = []
        
        # Create a notification for each user
        for user in users:
            notification = Notification.objects.create(
                user=user,
                **validated_data
            )
            notifications.append(notification)
        
        # Return the first notification for API response
        # In a real app, might want to return all of them
        return notifications[0] if notifications else None

class NotificationBatchSerializer(serializers.Serializer):
    """
    Serializer for batch operations on notifications
    """
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True
    )
    
    def validate(self, data):
        user = self.context['request'].user
        notification_ids = data['notification_ids']
        
        # Check that all notifications belong to the user
        notifications = Notification.objects.filter(
            id__in=notification_ids,
            user=user
        )
        
        if len(notifications) != len(notification_ids):
            raise serializers.ValidationError("Some notifications do not exist or do not belong to you")
        
        # Store notifications for later use
        self.notifications = notifications
        
        return data