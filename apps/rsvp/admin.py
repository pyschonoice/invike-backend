from django.contrib import admin
from .models import RSVP

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'plus_ones', 'is_approved', 'created_at')
    list_filter = ('status', 'is_approved', 'created_at')
    search_fields = ('user__name', 'user__email', 'event__title')
    raw_id_fields = ('user', 'event')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('event', 'user', 'status', 'plus_ones', 'is_approved')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )