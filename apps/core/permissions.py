from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False

class IsEventHost(permissions.BasePermission):
    """
    Custom permission to only allow hosts of an event to perform certain actions.
    """
    def has_permission(self, request, view):
        # Default to checking object permissions
        return True
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is the host of the event
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'event'):
            return obj.event.created_by == request.user
        
        return False    