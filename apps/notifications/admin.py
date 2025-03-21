from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__name', 'title', 'message')
    raw_id_fields = ('user', 'event')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'event', 'type', 'title', 'message')
        }),
        ('Actions', {
            'fields': ('action_link', 'action_text', 'is_read')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )