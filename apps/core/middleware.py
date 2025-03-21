import time
import logging
from django.utils.deprecation import MiddlewareMixin

# Configure logger
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log request details and timing
    """
    def process_request(self, request):
        # Store request start time
        request.start_time = time.time()
    
    def process_response(self, request, response):
        # Calculate request duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log request details
            logger.info(
                f"{request.method} {request.path} - {response.status_code} - {duration:.2f}s"
            )
        
        return response

class APIKeyMiddleware(MiddlewareMixin):
    """
    Middleware to validate API key for external services
    """
    def process_request(self, request):
        # This is a placeholder for real API key validation
        # In a real implementation, you'd check for API keys on specific routes
        pass