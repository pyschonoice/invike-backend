from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, payment_webhook

router = DefaultRouter()
router.register(r'', PaymentViewSet, basename='payment')



urlpatterns = [
    # Make sure these custom action paths come BEFORE the router.urls
    path('add-link/', PaymentViewSet.as_view({'post': 'add_payment_link'}), name='add-payment-link'),
    path('confirm/', PaymentViewSet.as_view({'post': 'confirm_payment'}), name='confirm-payment'),
    path('event-status/', PaymentViewSet.as_view({'get': 'event_status'}), name='event-payment-status'),

    # Explicitly define the update_status endpoint with consistent naming
    path('<uuid:pk>/update-status/', PaymentViewSet.as_view({'patch': 'update_status'}), name='update-payment-status'),
    
    # New webhook endpoint
    path('webhook/', payment_webhook, name='payment-webhook'),

    # Then include the router URLs for general CRUD operations
    path('', include(router.urls)),
]