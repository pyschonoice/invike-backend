from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RSVPViewSet, GuestListViewSet

router = DefaultRouter()
router.register(r'', RSVPViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('events/<uuid:event_id>/guests/', GuestListViewSet.as_view({'get': 'list'}), name='event-guests'),
    path('events/<uuid:event_id>/guests/export/', GuestListViewSet.as_view({'get': 'export'}), name='export-guests'),
]