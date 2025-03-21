from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    """
    Custom exception handler for standardized error responses
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    
    # If response is not defined, there was an unhandled exception
    if response is None:
        if isinstance(exc, Exception):
            return Response({
                'status': 'error',
                'message': str(exc),
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return None
    
    # Format the response to match our API standard
    if hasattr(response, 'data'):
        error_message = 'An error occurred'
        
        if 'detail' in response.data:
            error_message = response.data['detail']
        elif isinstance(response.data, list) and len(response.data) > 0:
            error_message = response.data[0]
        elif isinstance(response.data, dict):
            # Try to get the first error message
            for key in response.data:
                if isinstance(response.data[key], list) and len(response.data[key]) > 0:
                    error_message = f"{key}: {response.data[key][0]}"
                    break
                elif isinstance(response.data[key], str):
                    error_message = f"{key}: {response.data[key]}"
                    break
        
        response.data = {
            'status': 'error',
            'message': error_message,
            'code': response.status_code,
            'details': response.data
        }
    
    return response

class ResourceNotFoundError(APIException):
    """
    Exception for when a requested resource is not found
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found'
    default_code = 'resource_not_found'

class PermissionDeniedError(APIException):
    """
    Exception for when a user doesn't have permission to access a resource
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action'
    default_code = 'permission_denied'

class InvalidRequestError(APIException):
    """
    Exception for invalid request data
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid request data'
    default_code = 'invalid_request'
