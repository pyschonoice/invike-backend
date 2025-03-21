from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'privacy', 'created_by')
    list_filter = ('privacy', 'date')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'date', 'location')
        }),
        ('Settings', {
            'fields': ('privacy', 'created_by', 'cover_image')
        }),
        ('Map Data', {
            'fields': ('latitude', 'longitude')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )